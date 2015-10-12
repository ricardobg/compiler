# -*- coding: utf-8 -*-
"""
@author: ricardo

Analisador Léxico. Simplesmente remove todos os espaços em branco e quebras de linha.
"""
import sys, re

class Atomo:
	SINAIS_COMPOSTOS = 5
	def __init__(self, tipo, valor):
		self.tipo = tipo
		self.valor = valor

#Produz uma lista de átomos a partir do texto
def LeAtomos(texto):
	#Remove espaços
	last = ''
	atomos = []
	cmds = texto.strip().split()
	for cmd in cmds:
		if cmd == '':
			continue
		p = re.compile('(?:(?:==)|(?:>=)|(?:<=)|(?:[|][|])|(?:&&))|(?:-)|(?:[+{}\(\)\[\]\+\*\/=\<\>\!\,\;])|(?:[a-z0-9]+)', re.IGNORECASE)
		atomos.extend(p.findall(cmd))
	#Gera atomos
	for i, val in enumerate(atomos):
		if val in ['do', 'while', 'for', 'else', 'if', 'int', 'char', 'void' ]:
			atomos[i] = Atomo(val, val)
		elif val in ['-', '+', '*', '/', '%', '!', '=', '>', '<', ',', ';', '(', ')', '[', ']', '{', '}']:
			atomos[i] = Atomo(val, val)
		elif val in ['&&', '||', '>=', '<=', '==' ]:
			atomos[i] = Atomo(val, val)
		elif val.isdigit():
			atomos[i] = Atomo("NUMBER", val)
		else:
			atomos[i] = Atomo("NAME", val)
	return atomos


def main():
    # Checa os parâmetros
    if len(sys.argv) != 3:
        print("Uso: " + sys.argv[0] + " <cadeia entrada> <cadeia saída>")
        sys.exit()
    
    # Lê arquivo de entrada
    programa =  open(sys.argv[1],"r").read()
    atomos = LeAtomos(programa)
    for a in atomos:
    	print str(a.tipo) + " :" + a.valor
    return
    with open(sys.argv[2], "w") as saida:
    	saida.write(programa)

if __name__ == '__main__':
	main() 