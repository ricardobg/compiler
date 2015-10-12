# -*- coding: utf-8 -*-
"""
@author: ricardo

Analisador Léxico. Simplesmente remove todos os espaços em branco e quebras de linha.
"""
import sys, re

class Atomo:
	PALAVRA_RESERVADA = 1
	NAME = 2
	NUMBER = 3
	SINAIS = 4
	SINAIS_COMPOSTOS = 5
	def __init__(self, tipo, valor):
		self.tipo = tipo
		self.valor = valor

#Produz uma lista de átomos com a linha atual
def LeAtomos(texto):
	#Remove espaços
	last = ''
	atomos = []
	cmds = texto.strip().split()
	for cmd in cmds:
		while cmd.find()
		if cmd == '':
			continue

		if len(sem_vazios) == 0:
			continue
		i = 1
		while (1)
			char = sem_vazios[0:i]
			if char in ["do", "while", "for", "if", "else", "int", "char", "void"]
				atomos.append(Atomo(Atomo.PALAVRA_RESERVADA, char))
			elif char in :
				atomos.append(Atomo(Atomo.NAO_TERMINAL, char))
			i = i+1
			if i == len(sem_vazios):
				if char.isdigit():
					atomos.append(Atomo(Atomo.NUMBER, char))
				else
					atomos.append(Atomo(Atomo.NAME, char))
				break
		atomos.append(Atomo(Atomo.SINAIS, ';'))
	return atomos


def main():
    # Checa os parâmetros
    if len(sys.argv) != 3:
        print("Uso: " + sys.argv[0] + " <cadeia entrada> <cadeia saída>")
        sys.exit()
    
    # Lê arquivo de entrada
    programa =  open(sys.argv[1],"r").read()
    programa = programa.split()
    with open(sys.argv[2], "w") as saida:
    	saida.write(programa)
main() 