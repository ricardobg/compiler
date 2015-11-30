#!/usr/local/bin/python2
# -*- coding: utf-8 -*-
"""
@author: ricardo

Programa que converte notação de Wirth para Autômato de Pilha Estruturado
"""

import sys, json, pydot, re, copy

DEBUG = True
class Atomo:
	TERMINAL = 1
	NAO_TERMINAL = 2
	SIMBOLO = 3
	def __init__(self, tipo, valor):
		self.tipo = tipo
		self.valor = valor

class Submaquina:
	def __init__(self):
		self.alfabeto = []
		self.estados_finais = []
		self.estados = []
		self.estado_inicial = ''
		self.transicoes = []

	def to_obj(self):
		obj = {}
		obj["alfabeto"] = self.alfabeto
		obj["estados_finais"] = self.estados_finais
		obj["estados"] = self.estados
		obj["estado_inicial"] = self.estado_inicial
		obj["transicoes"] = self.transicoes
		return obj

#Produz uma lista de átomos com a linha atual
def LeAtomos(linha):
	#Remove espaços
	last = ''
	lendo_terminal = False
	atomos = []
	for seq in linha.strip().split():
		if seq == '':
			continue
		p = re.compile('(?:[{}\(\)\[\]\=\.|])|(?:["][^"]+["])|(?:[a-z0-9_]+)', re.IGNORECASE)
		atomos.extend(p.findall(seq))
	for i,val in enumerate(atomos):
			if val in ['{','}','(',')','|','[',']','=','.']:
				atomos[i] = Atomo(Atomo.SIMBOLO, val)
			elif val.find('"') == -1:
				atomos[i] = Atomo(Atomo.NAO_TERMINAL, val)
			else:
				atomos[i] = Atomo(Atomo.TERMINAL, val[1:-1])
	#print [t.valor for t in atomos]
	return atomos

def estados_inatingiveis(transicoes, estados):
	rets = estados[:]
	for transicao in transicoes:
		if len(transicao[1]) >= 1:
			 if transicao[1][0] in rets:
			 	rets.remove(transicao[1][0])
	return rets
def transicao_em_vazio(transicoes):
	for i, transicao in enumerate(transicoes):
		if len(transicao[1]) == 1 and len(transicao[0][1]) == 0:
			 return i
	return -1

def encontra_transicoes_out(estado, transicoes):
	lista = []
	for i, transicao in enumerate(transicoes):
		if transicao[0][0] == estado:
			lista.append(i)
	return lista

def encontra_transicoes_in(estado, transicoes):
	lista = []
	for i, transicao in enumerate(transicoes):
		if len(transicao[1]) >= 1 and transicao[1][0] == estado:
			 lista.append(i)
	return lista


def main():
	if len(sys.argv) != 3:
		print("Uso: " + sys.argv[0] + " <arquivo_wirth> <arquivo_saida>")
		sys.exit()
	maqs = {}
	maq_inicial = ''
   	with open(sys.argv[1],"r") as arquivo:
   		contador = 0
   		estado = 0
		for raw_linha in arquivo:
			pilha = []
			leu = False
			submaquina = Submaquina()
			for atomo in LeAtomos(raw_linha):
				if not leu:
					if maq_inicial == '':
						maq_inicial = atomo.valor
					maqs[atomo.valor] = submaquina
					leu = True;
					# Adiciona transição de retorno no estado de aceitação
					if DEBUG:
						print "Lendo definição de Não-Terminal " + atomo.valor + ":"
						print "	Lido '=' -> Criado estado inicial " + str(contador) + " e estado final " + str(contador+1)
						print "		Empilhou estados (" + str(contador) + ", " + str(contador+1) + ")"
					submaquina.estado_inicial = str(contador)
					submaquina.estados.append(str(contador));
					submaquina.estados.append(str(contador+1));
					submaquina.estados_finais.append(str(contador+1));
					submaquina.transicoes.append([[str(contador+1), ""], []])
					pilha.append((contador, contador+1))
					estado = contador
					contador += 2
				else:
					if atomo.tipo == Atomo.TERMINAL:
						if DEBUG:
							print "	Lido terminal '" + atomo.valor + "' -> Criado estado " + str(contador) + " e transição de " + str(estado) + " para " + str(contador) + " consumindo " + atomo.valor
							print "		Foi para estado " + str(contador)
						if atomo.valor not in submaquina.alfabeto:
							submaquina.alfabeto.append(atomo.valor)
						submaquina.transicoes.append([[str(estado), atomo.valor], [str(contador)]])
						submaquina.estados.append(str(contador))
						estado = contador
						contador += 1
					elif atomo.tipo == Atomo.NAO_TERMINAL:
						if DEBUG:
							print "	Lido não terminal '" + atomo.valor + "' -> Criado estado " + str(contador) + " e chamada da submáquina " + atomo.valor + " de " + str(estado) + " empilhando " + str(contador)
							print "		Foi para estado " + str(contador)
						submaquina.transicoes.append([[str(estado), ""], [str(contador), atomo.valor]])
						submaquina.estados.append(str(contador))
						estado = contador
						contador += 1
					elif atomo.tipo == Atomo.SIMBOLO:
						if atomo.valor in ['{','(','[']:
							if DEBUG:
								if atomo.valor == '{':
									print "	Leu '" + atomo.valor + "' e empilhou estados (" + str(contador) + ", " + str(contador) + ")"
								else:
									print "	Leu '" + atomo.valor + "' e empilhou estados (" + str(estado) + ", " + str(contador) + ")"
							if atomo.valor in ['{','[']:
								submaquina.transicoes.append([[str(estado), ""], [str(contador)]])
								if DEBUG:
									print "		Criada transição de " + str(estado) + " para " + str(contador) + " consumindo vazio"
							if atomo.valor == '{':
								estado = contador
								if DEBUG:
									print " 	Foi para estado " + str(estado)
							pilha.append((estado, contador))
							submaquina.estados.append(str(contador))
							contador += 1
						elif atomo.valor in ['}',')',']','.']:
							last = pilha.pop()
							if DEBUG:
								print "	Leu '" + atomo.valor + "' e desmiplhou estados (" + str(last[0]) + ", " + str(last[1]) + "), indo para " + str(last[1])
							submaquina.transicoes.append([[str(estado), ""], [str(last[1])]])
							estado = last[1]
						elif atomo.valor == '|':
							if DEBUG:
								print "	Leu '" + atomo.valor + "' e criou transição de " + str(estado) + " para " + str(pilha[-1][1]) + " consumindo vazio"
								print " 	Voltou para estado " + str(pilha[-1][0])
							submaquina.transicoes.append([[str(estado), ""], [str(pilha[-1][1])]])
							estado = pilha[-1][0]
				#print atomo.valor + "|" + str(estado) + "|" + str(contador) + "|" + str(pilha) + "|" + str(submaquina.transicoes[-1])

			# Remove não-determinismos
			continue
			if DEBUG:
				print "Removendo não determinismos..."
			while True:
				trans = transicao_em_vazio(submaquina.transicoes)
				
				if trans == -1:
					break
				estado_origem = submaquina.transicoes[trans][0][0]
				estado_destino = submaquina.transicoes[trans][1][0]
				transicoes_saindo = encontra_transicoes_out(estado_destino, submaquina.transicoes)
				transicoes_chegando = encontra_transicoes_in(estado_destino, submaquina.transicoes)
				for out in transicoes_saindo:
					submaquina.transicoes[out][0][0] = estado_origem
				for inn in transicoes_chegando:
					submaquina.transicoes[inn][1][0] = estado_origem
				submaquina.estados.remove(estado_destino)
				if (estado_destino in submaquina.estados):
					print "PAAAU MONSTROOOO"
					return -1
				if estado_destino in submaquina.estados_finais:
					submaquina.estados_finais.remove(estado_destino)
					submaquina.estados_finais.append(estado_origem)
				if submaquina.estado_inicial == estado_destino:
					submaquina.estado_inicial = estado_origem
				del submaquina.transicoes[trans]
			#continue
			#Remove estados inatingíveis
			while True:
				estados = estados_inatingiveis(submaquina.transicoes, submaquina.estados)
				if submaquina.estado_inicial in estados:
					estados.remove(submaquina.estado_inicial)
				if len(estados) == 0:
					break
				for estd in estados:
					transicoes_saindo = encontra_transicoes_out(estd, submaquina.transicoes)
					submaquina.transicoes = [t for i,t in enumerate(submaquina.transicoes) if i not in transicoes_saindo ]
					submaquina.estados.remove(estd)
					if estd in submaquina.estados_finais:
						submaquina.estados_finais.remove(estd)
			#Remove estados equivalentes
			achou_igual = True
			while achou_igual:
				achou_igual = False
				for estado_1 in submaquina.estados:
					if submaquina.estado_inicial == estado_1:
						continue
					transicoes_saindo_1 = copy.deepcopy([submaquina.transicoes[i] for i in encontra_transicoes_out(estado_1, submaquina.transicoes)])
					for i,t in enumerate(transicoes_saindo_1):
						transicoes_saindo_1[i][0][0] = "999"

					transicoes_chegando_1 = [submaquina.transicoes[i][0] for i in encontra_transicoes_in(estado_1, submaquina.transicoes)]
					#print "OPA"
					#print transicoes_chegando_1
					for estado_2 in submaquina.estados:
						if submaquina.estado_inicial == estado_2:
							continue
						if estado_1 == estado_2:
							continue
						transicoes_saindo_2 = copy.deepcopy([submaquina.transicoes[i] for i in encontra_transicoes_out(estado_2, submaquina.transicoes)][:])
						for i,t in enumerate(transicoes_saindo_2):
							transicoes_saindo_2[i][0][0] = "999"
						transicoes_chegando_2 =  [submaquina.transicoes[i][0] for i in encontra_transicoes_in(estado_2, submaquina.transicoes)]
						# Compara transições
						diff_saindo = filter(lambda x: x not in transicoes_saindo_2, transicoes_saindo_1) + filter(lambda x: x not in transicoes_saindo_1, transicoes_saindo_2)
						diff_chegando = filter(lambda x: x not in transicoes_chegando_2, transicoes_chegando_1) + filter(lambda x: x not in transicoes_chegando_1, transicoes_chegando_2)

						if len(diff_saindo) == 0 and len(diff_chegando) == 0:
							estados = [estado_2]
							if submaquina.estado_inicial in estados:
								estados.remove(submaquina.estado_inicial)
							for estd in estados:
								transicoes = encontra_transicoes_out(estd, submaquina.transicoes) + encontra_transicoes_in(estd, submaquina.transicoes)
								submaquina.transicoes = [t for i,t in enumerate(submaquina.transicoes) if i not in transicoes ]
								#for i,transicao in enumerate(transicoes):
								#	del submaquina.transicoes[i]
								submaquina.estados.remove(estd)
								if estd in submaquina.estados_finais:
									submaquina.estados_finais.remove(estd)
									if not estado_1 in submaquina.estados_finais:
										submaquina.estados_finais.append(estado_1)
							achou_igual = True
							break
					if achou_igual:
						break



	obj = {}
	obj["maquina_inicial"] = maq_inicial
	obj["maquinas"] = maqs
	print maq_inicial
	for maq in obj["maquinas"]:
		obj["maquinas"][maq] = obj["maquinas"][maq].to_obj()
	with open(sys.argv[2], 'w') as outfile:
		json.dump(obj, outfile)

main()