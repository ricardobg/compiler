# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 07:47:36 2015

@author: ricardo

Programa para simular autômatos finitos.
"""

import sys, json, pydot, analisador_lexico

DEBUG = True

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
        print("Uso: " + sys.argv[0] + " <regras_do_automato> <cadeias>")
        sys.exit()
    
    # Lê arquivo de entrada
    with open(sys.argv[1],"r") as leitura:
        dados = json.load(leitura)
    # Instancia autômatos
    automatos = dict()
    grafo = pydot.Dot(graph_type="digraph", rankdir='LR') 
    clusters = []
    for maq in dados["maquinas"]:
        subgrafo_nos = []
        if maq == dados["maquina_inicial"]:
            cluster = pydot.Cluster(maq, label=maq, fontname="bold")
        else:
            cluster = pydot.Cluster(maq, label=maq)
        clusters.append(cluster)

        if DEBUG:
            print "Automato '" + maq + "' lido:"
        automatos[maq] = Automato(dados["maquinas"][maq]["estados"], dados["maquinas"][maq]["estado_inicial"]\
            , dados["maquinas"][maq]["estados_finais"], dados["maquinas"][maq]["alfabeto"], dados["maquinas"][maq]["transicoes"])
        # Adiciona ao grafo os estados
        for estado in automatos[maq].estados:
            if estado in automatos[maq].estados_finais:
                no = pydot.Node(estado, shape="doublecircle")
            else:
                no = pydot.Node(estado, shape="circle")
            subgrafo_nos.append(no)
            cluster.add_node(no)
        no_invisivel = pydot.Node("INVISIVEL" + maq, style="invisible")
        cluster.add_node(no_invisivel)
        orig = [t for t in subgrafo_nos if t.get_name().replace("'","").replace('"','') == automatos[maq].estado_inicial]
        cluster.add_edge(pydot.Edge(no_invisivel, orig[0]))
        # Adiciona as transições
        for transicao in automatos[maq].transicoes:
            orig = [t for t in subgrafo_nos if t.get_name().replace("'","").replace('"','') == transicao[0]]
            # Transição normal
            print transicao
            print automatos[maq].transicoes[transicao]
            if len(automatos[maq].transicoes[transicao]) == 1:
                dest = [t for t in subgrafo_nos if t.get_name().replace("'","").replace('"','') == automatos[maq].transicoes[transicao][0]]
                cluster.add_edge(pydot.Edge(orig[0], dest[0], label= " " + transicao[1]))
            # Transição de empilhar
            elif len(automatos[maq].transicoes[transicao]) == 2:
                dest = [t for t in subgrafo_nos if t.get_name().replace("'","").replace('"','') == automatos[maq].transicoes[transicao][0]]

                cluster.add_edge(pydot.Edge(orig[0], dest[0], label= " " + automatos[maq].transicoes[transicao][1], style="dashed"))
        grafo.add_subgraph(cluster)
    grafo.write_png("grafo.png")
    programa =  open(sys.argv[2],"r").read()
    atomos = LeAtomos(programa)

    print "--------------------------------------------------------------------"
    print "Lendo cadeia "
    # Inicia autômato
    automato_atual = dados["maquina_inicial"]
    estado_atual = automatos[automato_atual].estado_inicial
    #Pilha com os estados e respectivas máquinas
    pilha = []
    # Variável para rejeitar
    rejeitar = False
    leitura = leitura.split()[0]
    cadeia_lida = ""
    for atomo in atomos:
        ret = le_atomo(simbolo, automatos, estado_atual, automato_atual, pilha)
        cadeia_lida += simbolo
        #Rejeita cadeia
        if len(ret) == 0:
            rejeitar = True
            break
        #Tentou desempilhar
        elif len(ret) == 1:
            if cadeia_lida != leitura:
                rejeitar = True
            break
        estado_atual = ret[0]
        automato_atual = ret[1]

    #Tenta ler mais
    while automatos[automato_atual].transicoes.has_key((estado_atual, "")):
        if len(automatos[automato_atual].transicoes[(estado_atual, "")]) == 1:
            if DEBUG:
                print automato_atual + ": Saindo do estado " + estado_atual + " e consumindo vazio para ir para o estado " + automatos[automato_atual].transicoes[(estado_atual, "")][0]
            estado_atual = automatos[automato_atual].transicoes[(estado_atual, "")][0];
        else:
            break

    if (not rejeitar) and len(pilha) == 0 and automatos[automato_atual].estados_finais.count(estado_atual) > 0:
        print "Cadeia " + leitura + " aceita no estado " + estado_atual
    else:
       
        print "Cadeia " + leitura + " não aceita",
        if rejeitar:
            print u"pois não foi encontrada uma transição"
        elif len(pilha) > 0:
            print u"pois a pilha não está vazia: " + str(pilha)
        else:
            print u"pois está em um estado de rejeição: " + estado_atual

def le_atomo(simbolo, automatos, estado_atual, automato_atual, pilha):
    # Transição normal
    if automatos[automato_atual].transicoes.has_key((estado_atual, simbolo)):
        if DEBUG:
            print automato_atual + ": Saindo do estado " + estado_atual + " e consumindo " + simbolo + " para ir para o estado " + automatos[automato_atual].transicoes[(estado_atual, simbolo)][0]
        return (automatos[automato_atual].transicoes[(estado_atual, simbolo)][0], automato_atual)
    
    # Empilha ou desempilha
    elif automatos[automato_atual].transicoes.has_key((estado_atual, "")):
        transicao = automatos[automato_atual].transicoes[(estado_atual, "")]
        # Empilha
        if len(transicao) == 2:
            if DEBUG:
                print automato_atual + ": Saindo do estado " + estado_atual + u" e indo para a submáquina " + transicao[1] + " (estado " + automatos[transicao[1]].estado_inicial + ") empilhando estado " + transicao[0]
            pilha.append((transicao[0], automato_atual))
            return le_atomo(simbolo, automatos, automatos[transicao[1]].estado_inicial, transicao[1], pilha)
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
                return le_atomo(simbolo, automatos, desempilha[0], desempilha[1], pilha)

    # Rejeita ou desempilha
    else:
        if estado_atual in automatos[automato_atual].estados_finais:
            # Tenta desmpilhar
            if not len(pilha) == 0:
                if DEBUG:
                    print automato_atual + ": Saindo do estado " + estado_atual + " e desempilhando estado " + pilha[-1][0] + u", indo para a submáquina " + pilha[-1][1]
                desempilha = pilha.pop()
                return le_atomo(simbolo, automatos, desempilha[0], desempilha[1], pilha)
        if DEBUG:
            print automato_atual + ": No estado " + estado_atual + (u" não há transições em vazio e nem transições consumindo ") + simbolo 
        #Tansição vazia
    if automatos[automato_atual].transicoes.has_key((estado_atual, "")):
        transicao = automatos[automato_atual].transicoes[(estado_atual, "")]
        if len(transicao) == 1:
            if DEBUG:
                print automato_atual + ": Saindo do estado " + estado_atual + " e consumindo vazio para ir para o estado " + automatos[automato_atual].transicoes[(estado_atual, "")][0]
            return le_atomo(simbolo, automatos, automatos[automato_atual].transicoes[(estado_atual, "")][0], automato_atual, pilha)
    return ()
    
main()
