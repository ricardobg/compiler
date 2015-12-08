#!/usr/local/bin/python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 07:47:36 2015

@author: ricardo

Programa para simular autômatos finitos.
"""

import sys, json, pydot, re

DEBUG = True

#Ações semânticas
pilha_semantica = []
codigo = ""
simbolo_atual = 0

class TabelaSimbolos:
    def __init__(self):
        self.tabela_simbolos_geral = {}
        self.tabela_simbolos_func = []
    def has_key(self, key):
        return reduce(lambda r, x: r or x.has_key(key), [tabela_simbolos_geral] + self.tabela_simbolos_func, False) 
    def get(self, key):
        return reduce(lambda r, x: r if not x.has_key(key) else x[key], [tabela_simbolos_geral] + self.tabela_simbolos_func, False) 
    def put(self, key, val, general=False):
        if general:
            self.tabela_simbolos_geral[key] = val
        else:
            self.tabela_simbolos_func[-1][key] = val
        return val
    def new_func(self):
        self.tabela_simbolos_func = []
    def enter_context(self):
        self.tabela_simbolos_func.push({})
    def leave_context(self):
        if len(self.tabela_simbolos_func) > 0:
            self.tabela_simbolos_func.pop()
    def print_tabela(self):
        pass

class Simbolo:
    def __init__(self, tipo):
        global simbolo_atual
        print 'novo simbolo'
        self.tipo = tipo
        self.label = 'lbl' + str(simbolo_atual)
        simbolo_atual += 1
tabela_simbolos = TabelaSimbolos()

def declaracao_variavel(token, pilha):
    global tabela_simbolos
    ret = ''
    if DEBUG:
        print "[ACAO SEMANTICA] -> Declaracao de variavel"
    c = reduce(lambda c, x: c if x.valor in [',', ';'] else c + tabela_simbolos.put(x.valor, Simbolo(pilha[0]), True).label + '  K /0000\n', pilha[1:], '')
    
    print [i.valor for i in pilha]
    print c
    del pilha[:]
    return c

acoes_semanticas = {
    '38': declaracao_variavel
}
#Analisador Léxico
class Atomo:
    def __init__(self, tipo, valor, n_linha, n_coluna):
        self.tipo = tipo
        self.valor = valor
        self.n_linha = n_linha
        self.n_coluna = n_coluna

#Retorna uma tupla, primeiro item é uma lista com o texto já quebrado e a segunda é a lista com os tokens
def find(texto, itens):
    lista = []
    txt = texto[:]
    if len(txt) == 0:
        return []
    for i in itens:
        pos = txt.find(i)
        if pos != -1:
            lista.extend(find(txt[0:pos], itens))
            lista.append(txt[pos:pos+len(i)])
            lista.extend(find(txt[pos+len(i):len(txt)], itens))
            break
    if len(lista) == 0 and len(texto) > 0:
        lista.append(txt)
    return lista

def LeAtomos(texto, n_linha, comentario):
    #Remove espaços
    name_exp = re.compile('^[a-z_]([a-z0-9_]*)$' , re.IGNORECASE)
    lidos = []
    if comentario:
        pos = texto.find('*/')
        if pos == -1:
            return ([], True)
        else:
            comentario = False
            lidos = texto[pos+2:].strip().split()
    else:
        pos = texto.find('/*')
        if pos != -1:
            lidos = texto[:pos].strip().split()
            comentario = True
        else:
            lidos = texto.strip().split()

    simbolos = ['-', '+', '*', '/', '%', '!', '=', '>', '<', ',', ';', '(', ')', '[', ']', '{', '}']
    simbolos_compostos = ['&&', '||', '>=', '<=', '==', '++', '--', '!=' ]
    atomos = []
    #Gera atomos
    pos = 0
    for i, cadeia in enumerate(lidos):
        tokens = find(cadeia, simbolos_compostos + simbolos)
        for token in tokens:
            if token in ['do', 'while', 'for', 'else', 'if', 'int', 'char', 'void', 'return', 'float' ]:
                atomos.append(Atomo(token, token, n_linha, pos))
            elif token in simbolos:
                atomos.append(Atomo(token, token, n_linha, pos))
            elif token in simbolos_compostos:
                atomos.append(Atomo(token, token, n_linha, pos))
            elif token.isdigit() or (len(token.split('.')) == 2  and (len(token.split('.')[0]) == 0 or token.split('.')[0].isdigit()) and token.split('.')[1].isdigit()):
                atomos.append(Atomo("NUMBER", token, n_linha, pos))
            elif name_exp.match(token) != None: 
                atomos.append(Atomo("NAME", token, n_linha, pos))
            else:
                raise ValueError(token, n_linha, pos)
            pos += len(token)
        pos += len(cadeia)
    return (atomos, comentario)

class Automato:
    def __init__(self, estados, estado_inicial, estados_finais, alfabeto, transicoes):
        self.estados = map(lambda x: str(x), estados)
        self.estado_inicial = str(estado_inicial)
        self.alfabeto = map(lambda x: str(x), alfabeto)
        self.estados_finais = map(lambda x: str(x), estados_finais)
        # coloca transicões como um dicionário (ESTADO, ENTRADA) -> ESTADO
        self.transicoes = dict(map(lambda x: (tuple(map (lambda y: str(y), x[0])), tuple(x[1])), transicoes))
        self.alfabeto = map(lambda x: str(x), alfabeto)
        if DEBUG:
            print "    Q  =", str(json.dumps(self.estados)).replace('"', '')
            print "    q0 =", self.estado_inicial
            print "    F  =", str(json.dumps(self.estados_finais)).replace('"', '')
            print "    Σ  =", str(json.dumps(self.alfabeto)).replace('"', '')
            print "    δ  ="
            for t in self.transicoes:
                # Transição normal
                if len(self.transicoes[t]) == 1:
                     print "         " + str(json.dumps(t).replace('"', '')) + " -> " + str(json.dumps(self.transicoes[t][0]).replace('"', ''))
                # Transição de empilhar
                elif len(self.transicoes[t]) == 2:
                    print "         " + str(json.dumps(t[0]).replace('"', '')) + ", " + str(json.dumps(self.transicoes[t][1]).replace('"', '')) + " -> EMPILHA " + str(json.dumps(self.transicoes[t][0]).replace('"', ''))
                # Transição de desempilhar
                else:
                    print "         " + str(json.dumps(t[0]).replace('"', '')) + " -> DESEMPILHA"
       
def main():
    # Checa os parâmetros
    if (len(sys.argv) != 3):
        print("Uso: " + sys.argv[0] + " <regras_do_automato> <cadeia>")
        sys.exit()
    
    # Lê arquivo de entrada
    with open(sys.argv[1],"r") as leitura:
        dados = json.load(leitura)
    # Instancia autômatos
    automatos = dict()
    grafo = pydot.Dot(graph_type="digraph", rankdir='LR') 
    clusters = []
    for maq in dados["maquinas"]:
        if DEBUG:
            print "Automato '" + maq + "' lido:"
        automatos[maq] = Automato(dados["maquinas"][maq]["estados"], dados["maquinas"][maq]["estado_inicial"]\
            , dados["maquinas"][maq]["estados_finais"], dados["maquinas"][maq]["alfabeto"], dados["maquinas"][maq]["transicoes"])
    #Adiciona ações semânticas 

    linhas =  open(sys.argv[2],"r").readlines()
    atomos = []
    comentario = False
    for i,l in enumerate(linhas):
        try:
            r = LeAtomos(l, i, comentario)
            comentario = r[1]
            atomos.extend(r[0])
        except ValueError as err:
            print "Símbolo '" + err.args[0] + "' inválido na linha " + str(err.args[1]) + ":"
            print linhas[err.args[1]] ,
            return
    # Inicia autômato
    automato_atual = dados["maquina_inicial"]
    estado_atual = automatos[automato_atual].estado_inicial
    #Pilha com os estados e respectivas máquinas
    pilha = []
    # Variável para rejeitar
    rejeitar = False
    cadeia_lida = []
    for atomo in atomos:
        cadeia_lida.append(atomo)
        ret = le_atomo(atomo, automatos, estado_atual, automato_atual, pilha)
        #Rejeita cadeia
        if len(ret) == 0:
            rejeitar = True
            break
        #Tentou desempilhar
        elif len(ret) == 1:
            if not len(cadeia_lida) == len(atomos):
                rejeitar = True
            break
        estado_atual = ret[0]
        automato_atual = ret[1]

    while automatos[automato_atual].transicoes.has_key((estado_atual, "")):
        if len(automatos[automato_atual].transicoes[(estado_atual, "")]) == 1:
            if DEBUG:
                print automato_atual + ": Saindo do estado " + estado_atual + " e consumindo vazio para ir para o estado " + automatos[automato_atual].transicoes[(estado_atual, "")][0]
            estado_atual = automatos[automato_atual].transicoes[(estado_atual, "")][0];
        else:
            break
    #Tenta desempilhar
    while len(pilha) > 0 and not rejeitar:
        if automatos[automato_atual].transicoes.has_key((estado_atual, "")):
            transicao = automatos[automato_atual].transicoes[(estado_atual, "")]
            # Desempilha
            if len(transicao) == 0:
                if DEBUG:
                    print automato_atual + ": Saindo do estado " + estado_atual + " e desempilhando estado " + pilha[-1][0] + u", indo para a submáquina " + pilha[-1][1]
                desempilha = pilha.pop()
                estado_atual = desempilha[0]
                automato_atual = desempilha[1]
                while automatos[automato_atual].transicoes.has_key((estado_atual, "")):
                    if len(automatos[automato_atual].transicoes[(estado_atual, "")]) == 1:
                        if DEBUG:
                            print automato_atual + ": Saindo do estado " + estado_atual + " e consumindo vazio para ir para o estado " + automatos[automato_atual].transicoes[(estado_atual, "")][0]
                        estado_atual = automatos[automato_atual].transicoes[(estado_atual, "")][0];
                    else:
                        break
        else:
            break

    if (not rejeitar) and len(pilha) == 0 and automatos[automato_atual].estados_finais.count(estado_atual) > 0:
        print "Programa aceito!\n" 
        print codigo
        print "#"
    else:
        print "Erro de Sintaxe na linha " + str(cadeia_lida[-1].n_linha+1) + ". Token '" + cadeia_lida[-1].valor + "' não esperado: "
        print linhas[cadeia_lida[-1].n_linha] ,

def chama_acao_semantica(atomo, estado_atual, vazia=False):
    global acoes_semanticas, pilha_semantica, codigo
    if not vazia:
        pilha_semantica.append(atomo)
    if acoes_semanticas.has_key(estado_atual):
        codigo += acoes_semanticas[estado_atual](pilha_semantica[-1], pilha_semantica)

def le_atomo(atomo, automatos, estado_atual, automato_atual, pilha):
    simbolo = atomo.tipo
    # Transição normal
    if automatos[automato_atual].transicoes.has_key((estado_atual, simbolo)):
        if DEBUG:
            print automato_atual + ": Saindo do estado " + estado_atual + " e consumindo " + simbolo + " para ir para o estado " + automatos[automato_atual].transicoes[(estado_atual, simbolo)][0]
        chama_acao_semantica(atomo, automatos[automato_atual].transicoes[(estado_atual, simbolo)][0])
        return (automatos[automato_atual].transicoes[(estado_atual, simbolo)][0], automato_atual)
    
    # Empilha ou desempilha
    elif automatos[automato_atual].transicoes.has_key((estado_atual, "")):
        transicao = automatos[automato_atual].transicoes[(estado_atual, "")]
        # Empilha
        if len(transicao) == 2:
            if DEBUG:
                print automato_atual + ": Saindo do estado " + estado_atual + u" e indo para a submáquina " + transicao[1] + " (estado " + automatos[transicao[1]].estado_inicial + ") empilhando estado " + transicao[0]
            pilha.append((transicao[0], automato_atual))
            return le_atomo(atomo, automatos, automatos[transicao[1]].estado_inicial, transicao[1], pilha)
        # Desempilha
        elif len(transicao) == 0:
            # Nada para desempilhar, rejeita
            if len(pilha) == 0 and estado_atual not in automatos[automato_atual].estados_finais:
                if DEBUG:
                    print automato_atual + u": Tentando desempilhar mas a pilha está vazia"
                return ([])
            elif len(pilha) != 0:
                if DEBUG:
                    print automato_atual + ": Saindo do estado " + estado_atual + " e desempilhando estado " + pilha[-1][0] + u", indo para a submáquina " + pilha[-1][1]
                desempilha = pilha.pop()
                return le_atomo(atomo, automatos, desempilha[0], desempilha[1], pilha)

    # Rejeita ou desempilha
    else:
        if estado_atual in automatos[automato_atual].estados_finais:
            # Tenta desmpilhar
            if not len(pilha) == 0:
                if DEBUG:
                    print automato_atual + ": Saindo do estado " + estado_atual + " e desempilhando estado " + pilha[-1][0] + u", indo para a submáquina " + pilha[-1][1]
                desempilha = pilha.pop()
                return le_atomo(atomo, automatos, desempilha[0], desempilha[1], pilha)
        if DEBUG:
            print automato_atual + ": No estado " + estado_atual + (u" não há transições em vazio e nem transições consumindo ") + simbolo 
    #Tansição vazia
    if automatos[automato_atual].transicoes.has_key((estado_atual, "")):
        transicao = automatos[automato_atual].transicoes[(estado_atual, "")]
        if len(transicao) == 1:
            if DEBUG:
                print automato_atual + ": Saindo do estado " + estado_atual + " e consumindo vazio para ir para o estado " + automatos[automato_atual].transicoes[(estado_atual, "")][0]
            chama_acao_semantica(atomo, automatos[automato_atual].transicoes[(estado_atual, "")][0], True)
            return le_atomo(atomo, automatos, automatos[automato_atual].transicoes[(estado_atual, "")][0], automato_atual, pilha)
    return ()
    
main()
