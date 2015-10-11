# -*- coding: utf-8 -*-
"""
@author: ricardo

Programa que converte notação de Wirth para Autômato de Pilha Estruturado
"""

import sys, json, pydot

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
	for seq in linha.strip().split('"'):
		if seq == '':
			lendo_terminal = not lendo_terminal
			continue
		if lendo_terminal:
			atomos.append(Atomo(Atomo.TERMINAL, seq))
		else:
			seq2 = ''.join(seq.split())
			for char in seq2:
				if char in ['{','}','(',')','|','[',']','=','.']:
					atomos.append(Atomo(Atomo.SIMBOLO, char))
				else:
					atomos.append(Atomo(Atomo.NAO_TERMINAL, char))
		lendo_terminal = not lendo_terminal
	print [t.valor for t in atomos]
	return atomos


def main():
	if len(sys.argv) != 3:
		print("Uso: " + sys.argv[0] + " <arquivo_wirth> <arquivo_saida>")
		sys.exit()
	maqs = {}
	maq_inicial = ''
   	with open(sys.argv[1],"r") as arquivo:
		for raw_linha in arquivo:
			pilha = []
			contador = 0
			leu = False
			submaquina = Submaquina()
			estado = 0
			for atomo in LeAtomos(raw_linha):
				if not leu:
					if maq_inicial == '':
						maq_inicial = atomo.valor
					maqs[atomo.valor] = submaquina
					leu = True;
					# Adiciona transição de retorno no estado de aceitação
					submaquina.estado_inicial = 0
					submaquina.estados.append(0);
					submaquina.estados.append(1);
					submaquina.estados_finais.append(1);
					submaquina.transicoes.append([[1, ""], []])
					contador = 1
					estado = 0
				else:
					if atomo.tipo == Atomo.TERMINAL:
						if atomo.valor not in submaquina.alfabeto:
							submaquina.alfabeto.append(atomo.valor)
						submaquina.transicoes.append([[str(estado), atomo.valor], [str(contador)]])
						submaquina.estados.append(contador)
						estado = contador
						contador += 1
					elif atomo.tipo == Atomo.NAO_TERMINAL:
						submaquina.transicoes.append([[str(estado), ""], [str(contador), atomo.valor]])
						submaquina.estados.append(contador)
						estado = contador
						contador += 1
					elif atomo.tipo == Atomo.SIMBOLO:
						if atomo.valor in ['{','(','[', '=']:
							if atomo.valor in ['{','[']:
								submaquina.transicoes.append([[str(estado), ""], [str(contador)]])
							if atomo.valor == '{':
								estado = contador
							pilha.append((estado, contador))
							submaquina.estados.append(contador)
							contador += 1
						elif atomo.valor in ['}',')',']','.']:
							last = pilha.pop()
							submaquina.transicoes.append([[str(estado), ""], [str(last[1])]])
							estado = last[1]
						elif atomo.valor == '|':
							submaquina.transicoes.append([[str(estado), ""], [str(pilha[-1][1])]])
							estado = pilha[-1][0]
				print atomo.valor + "|" + str(estado) + "|" + str(contador) + "|" + str(pilha) + "|" + str(submaquina.transicoes[-1])
	obj = {}
	obj["maquina_inicial"] = maq_inicial
	obj["maquinas"] = maqs
	print maq_inicial
	for maq in obj["maquinas"]:
		obj["maquinas"][maq] = obj["maquinas"][maq].to_obj()
	with open(sys.argv[2], 'w') as outfile:
		json.dump(obj, outfile)

main()