#!/usr/local/bin/python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 07:47:36 2015

@author: ricardo

Programa para simular autômatos finitos.
"""

import sys, json, pydot, re, copy

DEBUG = True

#Ações semânticas
pilha_semantica = []
area_dados = ""
area_code = ""
area_constantes = ''
simbolo_atual = 0


class TabelaSimbolos:
    def __init__(self):
        self.tabela_simbolos_geral = {}
        self.tabela_simbolos_func = []
        self.current_function = None
    def has_key(self, key):
        return reduce(lambda r, x: r or x.has_key(key), [self.tabela_simbolos_geral] + self.tabela_simbolos_func, False) 
    def get(self, key):
        if not self.has_key(key):
            raise ValueError("Symbol '" + key + "' not declared")
        return reduce(lambda r, x: r if not x.has_key(key) else x[key], [self.tabela_simbolos_geral] + self.tabela_simbolos_func, False) 
    def put(self, key, val, general=False):
        if general:
            if self.tabela_simbolos_geral.has_key(key):
                raise TypeError("Símbolo " + key + " definido múltiplas vezes")
            self.tabela_simbolos_geral[key] = val
        else:
            if self.tabela_simbolos_func[-1].has_key(key):
                raise TypeError("Símbolo " + key + " definido múltiplas vezes")
            self.tabela_simbolos_func[-1][key] = val
        return val
    def new_func(self):
        self.tabela_simbolos_func = []
    def enter_context(self, func=None):
        self.tabela_simbolos_func.append({})
        if not func == None:
            self.current_function = func
    def leave_context(self, func=None):
        if len(self.tabela_simbolos_func) > 0:
            self.tabela_simbolos_func.pop()
        if not func == None:
            self.current_function = None
    def print_tabela(self):
        print "Tabela de Simbolos\n\n"
        print "     Global"
        for k in self.tabela_simbolos_geral:
            g = self.tabela_simbolos_geral[k]
            print  "    '" + str(g.nome) + "' | " + g.tipo + "|" + g.label

class Simbolo:
    def __init__(self, tipo, nome=None, retorno=None, args=[]):
        global simbolo_atual
        if tipo not in ('int', 'int[]', 'function') and retorno not in ('void', 'int', None):
            raise TypeError("Tipo '" + tipo + "' não implementado")
        self.tipo = tipo
        self.label = 'lbl' + str(simbolo_atual)
        self.nome = nome
        if tipo == 'function':
            self.retorno = retorno
            self.args = args
            
        simbolo_atual += 1

tabela_simbolos = TabelaSimbolos()

def declaracao_variavel(token, pilha, var_global=False):
    global tabela_simbolos
    if DEBUG:
        print "[ACAO SEMANTICA] -> Declaracao de variável"
    codigo = ''
    for k,v in enumerate(pilha[1:]):
        if v.valor in [',', ';', '[', ']','='] or v.valor.isdigit():
            continue
        if pilha[1:][k+1].valor == '[':
            codigo += tabela_simbolos.put(v.valor, Simbolo(pilha[0].valor + '[]', v.valor), var_global).label + '   $   =' + pilha[1:][k+2].valor + ' ; vetor ' + v.valor + '\n'
        else:
            codigo += tabela_simbolos.put(v.valor, Simbolo(pilha[0].valor, v.valor), var_global).label + '   K   =' + (pilha[1:][k+2].valor if pilha[1:][k+1].valor == '=' else '0') + ' ; inteiro ' + v.valor + '\n'
    print [i.valor for i in pilha]
    del pilha[:]
    return codigo


def declaracao_funcao(token, pilha):
    global tabela_simbolos
    if DEBUG:
        print "[ACAO SEMANTICA] -> Declaracao de função"
    codigo = ''
    args = []
    func = Simbolo('function', pilha[1].valor, pilha[0])
    tabela_simbolos.enter_context(func)
    tabela_simbolos.put(pilha[1].valor, copy.copy(func), True)
    tabela_simbolos.print_tabela()
    for k,v in enumerate(pilha[3:]):
        if v.valor in [',', ';', '[', ']','int', 'char', 'float', '(', ')'] or v.valor.isdigit():
            continue
        if pilha[3:][k+1].valor == '[':
            args.append(Simbolo(pilha[3:][k-1].valor + '[]', v.valor))
            codigo += tabela_simbolos.put(v.valor, args[-1] , False).label + '   K   =0 ; vetor ' + v.valor + '\n'
        else:
            args.append(Simbolo(pilha[3:][k-1].valor, v.valor))
            codigo += tabela_simbolos.put(v.valor, args[-1], False).label + '   K   =0 ; inteiro ' + v.valor + '\n'


    func.args = args
    
    print [i.valor for i in pilha]
    del pilha[:] 
    return codigo

def limpa_pilha(token, pilha):
    del pilha[:]
    return ''

def fim_contexto(token, pilha, funcao=False):
    global tabela_simbolos
    codigo = ''
    if funcao:
        codigo += '   RS      ' +  tabela_simbolos.current_function.label + '\n'
    tabela_simbolos.leave_context(funcao)
    del pilha[:]
    return codigo

def inicio_contexto(token, pilha):
    pass





# Código para iniciar função
def inicio_funcao(token, pilha):
    global tabela_simbolos
    if DEBUG:
        print "[ACAO SEMANTICA] -> Início de função"
    codigo = tabela_simbolos.current_function.label + '   K   =0   ; funcao ' + tabela_simbolos.current_function.nome + '\n'
    for arg in tabela_simbolos.current_function.args:
        codigo += '   SC    POP ; poping ' + arg.nome + '\n'
        codigo += '   MM   ' + arg.label + '\n' 
    del pilha[:] 
    print codigo
    return codigo


def le_matriz(itens):
    codigo += '     LV     ' + itens[0].valor + '\n ; carrega endereco'
    codigo += '     SC     PUSH\n'
    #Calcula valor
    codigo += '     MM     TEMP\n'
    codigo += '     SC     POP\n'
    codigo += '     SC     POP\n'
    codigo += '    '   
    #primeiro: identificador
    pass

def escreve_matriz(itens):
    pass

#
#Expression
#
pilha_expression = []


def enter_expression(token, pilha):
    global pilha_expression
    if len(pilha_expression) == 0:
        if DEBUG:
            print "[ACAO SEMANTICA] -> Chamou Expression"
        pilha_expression.append(pilha[:])
        del pilha[:]
    return ''

def new_expression(token, pilha): 
    global pilha_expression
    if DEBUG:
        print "[ACAO SEMANTICA] -> Chamou Expression dentro de Expression"
    print [i.valor for i in pilha]
    pilha_expression.append(pilha[:])
    del pilha[:]
    return ''


def leave_expression(token, pilha):
    global pilha_expression
    if DEBUG:
        print "[ACAO SEMANTICA] -> Fim de Expression"
    codigo = ''
    if len(pilha_expression) > 1:
        pilha[:] = pilha_expression.pop() + pilha[:]        
    else:
        print [i.valor for i in pilha]
        ret = trata_piha(pilha)
        del pilha[:]
        pilha = pilha_expression.pop()
        return ret
    return ''


def trata_piha(pilha):
    global tabela_simbolos, area_constantes
    out_expression = []
    operators = []
    equal = []
    for k,i in enumerate(pilha):
        #Função
        if i.tipo == 'NAME' and tabela_simbolos.get(i.valor).tipo == 'function':
            operators.append(i)
        elif i.tipo in ['NAME', 'NUMBER']:
            out_expression.append(i)
        elif i.valor == '=':
            equal = out_expression[:]
            del out_expression[:]
        else:
            if i.valor == '(':
                operators.append(i)   
            elif i.valor == ')':
                print 'FECHANDO'
                print [i.valor for i in operators]
                topo = operators.pop()
                while True: 
                    if topo.valor == '(':
                        break
                    out_expression.append(topo)
                    topo = operators.pop()
                if len(operators) > 0: 
                    topo = operators[-1]
                    if topo.tipo == 'NAME' and tabela_simbolos.get(topo.valor).tipo == 'function':
                        out_expression.append(operators.pop())
            else:   
                if len(operators) > 0: 
                    while len(operators) > 0:
                        topo = operators[-1]
                        #Se lido tiver menos precedencia ou igual ao topo, desempilha
                        #Iguais, desempilha
                        if topo.valor == '(' or topo.valor == ')':
                            break
                        if topo.valor == i.valor and topo.valor != '!': 
                            out_expression.append(operators.pop())
                        elif topo.valor in ['[', ']']:
                            out_expression.append(operators.pop())
                        elif topo.valor in ['*', '/'] and i.valor not in ['[', ']']:
                            out_expression.append(operators.pop())
                        elif topo.valor in ['+', '-'] and i.valor not in ['[', ']', '*', '/']:
                            out_expression.append(operators.pop())
                        elif topo.valor in ['<', '>', '<=', '>='] and i.valor not in ['[', ']', '*', '/', '+', '-']:
                            out_expression.append(operators.pop())
                        elif topo.valor in ['==', '!='] and i.valor not in ['[', ']', '*', '/', '+', '-','<', '>', '<=', '>=']:
                            out_expression.append(operators.pop())
                        elif topo.valor in ['&&'] and i.valor not in ['[', ']', '*', '/', '+', '-','<', '>', '<=', '>=', '==', '!=']:
                            out_expression.append(operators.pop())
                        elif topo.valor in ['||'] and i.valor not in ['[', ']', '*', '/', '+', '-','<', '>', '<=', '>=', '==', '!=', '&&']:
                            out_expression.append(operators.pop())
                        else:
                            break
                operators.append(i)
    operators.reverse()
    out_expression = out_expression + operators
    print "Finished pilha:"
    print [i.valor for i in out_expression]
    #Tratar pilha
    codigo = ''
    for k,i in enumerate(out_expression):
        #Constante numérica
        if i.tipo == "NUMBER":
            if not tabela_simbolos.has_key(int(i.valor)):
                sim = Simbolo('int', int(i.valor))
                tabela_simbolos.put(int(i.valor), sim, True)
                area_constantes +=  sim.label + "   K   =" + str(sim.nome) + " ; cte\n"
            codigo += '     LD     ' + tabela_simbolos.get(int(i.valor)).label + " ; carrega " + i.valor + "\n"
            codigo += '     SC     PUSH\n'
        elif i.tipo == 'NAME':
            #Vetor
            if len(out_expression) > k and out_expression[k] == '[':            
                pass
            #Variável normal
            else:
                codigo += '     LD     ' + tabela_simbolos.get(i.valor).label + " ; carrega " + i.valor + "\n" 
            codigo += '     SC     PUSH\n'
        #operador 
        elif i.valor not in ['[',']']:
            #tira do topo da pilha
            codigo += '     SC     POP\n'
            #guarda topo da pilha em temp
            codigo += '     MM     TEMP\n'
            #tira do topo da pilha
            codigo += '     SC     POP\n'
            #faz operacao com TEMP
            if i.valor in ['+', '-', '/', '*']:
                codigo += '     ' + i.valor + '     TEMP\n'
            else:
                if i.valor == '%':
                    codigo += '     /     TEMP\n'   
                elif i.valor == '>':
                    codigo += '     -     TEMP\n'
                    false_simb = Simbolo('int').label
                    fim_simb = Simbolo('int').label
                    codigo += '     JN   ' + false_simb + ' ; pula para false\n'
                    codigo += '     JZ   ' + false_simb + ' ; pula para false\n'
                    codigo += '          LV =1 ; eh > \n' 
                    codigo += '     JP     ' + fim_simb + ' \n'
                    codigo += false_simb + '    LV =0 ; eh <=\n'
                    codigo += fim_simb #sem quebra de linha: proxima linha começa deste label 
                elif i.valor == '>=':
                    codigo += '     -     TEMP\n'
                    false_simb = Simbolo('int').label
                    fim_simb = Simbolo('int').label
                    codigo += '     JN   ' + false_simb + ' ; pula para false\n'
                    codigo += '          LV =1 ; eh >= \n' 
                    codigo += '     JP     ' + fim_simb + ' \n'
                    codigo += false_simb + '    LV =0 ; eh <\n'
                    codigo += fim_simb #sem quebra de linha: proxima linha começa deste label 
                elif i.valor == '<':
                    codigo += '     -     TEMP\n'
                    verd_simb = Simbolo('int').label
                    fim_simb = Simbolo('int').label
                    codigo += '     JN   ' + verd_simb + ' ; pula para true\n'
                    codigo += '          LV =0 ; eh >= \n' 
                    codigo += '     JP     ' + fim_simb + ' \n'
                    codigo += verd_simb + '    LV =1 ; eh <\n'
                    codigo += fim_simb #sem quebra de linha: proxima linha começa deste label 
                elif i.valor == '<=':
                    codigo += '     -     TEMP\n'
                    verd_simb = Simbolo('int').label
                    fim_simb = Simbolo('int').label
                    codigo += '     JN   ' + verd_simb + ' ; pula para true\n'
                    codigo += '     JZ   ' + verd_simb + ' ; pula para true\n'
                    codigo += '          LV =0 ; eh > \n' 
                    codigo += '     JP     ' + fim_simb + ' \n'
                    codigo += verd_simb + '    LV =1 ; eh <=\n'
                    codigo += fim_simb #sem quebra de linha: proxima linha começa deste label 

                elif i.valor == '==':
                    codigo += '     -     TEMP\n'
                    verd_simb = Simbolo('int').label
                    fim_simb = Simbolo('int').label
                    codigo += '     JZ   ' + verd_simb + ' ; pula para true\n'
                    codigo += '          LV =0 ; eh != \n' 
                    codigo += '     JP     ' + fim_simb + ' \n'
                    codigo += verd_simb + '    LV =1 ; eh ==\n'
                    codigo += fim_simb #sem quebra de linha: proxima linha começa deste label 

                elif i.valor == '!=':
                    codigo += '     -     TEMP\n'
                    false_simb = Simbolo('int').label
                    fim_simb = Simbolo('int').label
                    codigo += '     JZ   ' + false_simb + ' ; pula para false\n'
                    codigo += '          LV =1 ; eh == \n' 
                    codigo += '     JP     ' + fim_simb + ' \n'
                    codigo += false_simb + '    LV =0 ; eh !=\n'
                    codigo += fim_simb #sem quebra de linha: proxima linha começa deste label 

                elif i.valor == '&&':
                    codigo += '     +     TEMP\n'
                    codigo += '     -     DOIS\n'
                    verd_simb = Simbolo('int').label
                    fim_simb = Simbolo('int').label
                    codigo += '     JZ   ' + verd_simb + ' ; pula para true\n'
                    codigo += '          LV =0 ; eh false \n' 
                    codigo += '     JP     ' + fim_simb + ' \n'
                    codigo += verd_simb + '    LV =1 ; eh true \n'
                    codigo += fim_simb #sem quebra de linha: proxima linha começa deste label 

                elif i.valor == '||':
                    codigo += '     +     TEMP\n'
                    false_simb = Simbolo('int').label
                    fim_simb = Simbolo('int').label
                    codigo += '     JZ   ' + false_simb + ' ; pula para false\n'
                    codigo += '          LV =1 ; eh true \n' 
                    codigo += '     JP     ' + fim_simb + ' \n'
                    codigo += false_simb + '    LV =0 ; eh false \n'
                    codigo += fim_simb #sem quebra de linha: proxima linha começa deste label 


            #Coloca resultado no topo da pilha
            codigo += '     SC     PUSH\n'
    #Pop para colocar resultado no acumulador
    if len(out_expression) > 0:
        codigo += '     SC     POP\n'
    #Verifica se tem atribuição e faz
    if len(equal) > 0:
        if len(equal) == 1: 
            codigo += '     MM      ' + tabela_simbolos.get(equal[0].valor).label + ' ; salva no ' + equal[0].valor + '\n'
        else:
            pass
    return codigo

def decr_ou_incr_ou_ref(token, pilha):
    #if DEBUG:
    #    print "[ACAO SEMANTICA] -> Referência a variável com incremento ou decremento"
    return ''
acoes_semanticas = {
    '38': {
        'func_data': lambda token, pilha: declaracao_variavel(token, pilha, True)
    },
    '60': {
        'func_data': declaracao_variavel
    },
    '13': { 
        'func_data': declaracao_funcao,
        'func_code': inicio_funcao
    },
    '15': {
        'func_code': limpa_pilha
    },
    '17': {
        'func_code': lambda token, pilha: fim_contexto(token, pilha, True)
    },
    '248': {
        'func_code': decr_ou_incr_ou_ref
    },
    '180': {
        'func_code': new_expression
    },
    '240': {
        'func_code': new_expression
    },
    '200': {
        'func_code': new_expression
    },
    '270': {
        'func_code': new_expression
    },
    '210': {
        'func_code': new_expression
    },
    '184': {
        'func_code': new_expression
    },
    '223': {
        'func_code': new_expression
    },
    '245': {
        'func_code': new_expression
    },
    '252': {
        'func_code': new_expression
    },
    '177': {
        'func_code': enter_expression
    },
    '178': {
        'func_code': leave_expression
    }
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
    global tabela_simbolos
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
    #try:
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
    tabela_simbolos.print_tabela()
    if (not rejeitar) and len(pilha) == 0 and automatos[automato_atual].estados_finais.count(estado_atual) > 0:
        if not tabela_simbolos.has_key('main'):
            print "Erro: Função 'main' não definida."
            return

        print "Programa aceito!\n" 
        print '@ /0000 '  
        print 'MAIN    SC  ' + tabela_simbolos.get('main').label + ' ; chama main\n'
        print 'END     HM   END ; Fim\n'
        print area_dados + area_code + area_constantes + open('stack.asm').read()
        print "# TEMP"
    else:
        print "Erro de Sintaxe na linha " + str(cadeia_lida[-1].n_linha+1) + ". Token '" + cadeia_lida[-1].valor + "' não esperado: "
        print linhas[cadeia_lida[-1].n_linha] ,
    #except Exception as e:
    #    raise e
    #    print "Erro na linha " + str(cadeia_lida[-1].n_linha+1) + ". " + e.args[0] + ":"
    #    print linhas[cadeia_lida[-1].n_linha] ,


def chama_acao_semantica(atomo, estado_atual, vazia=False):
    global acoes_semanticas, pilha_semantica, area_dados, area_code
    if not vazia and atomo != None:
        pilha_semantica.append(atomo)
    if acoes_semanticas.has_key(estado_atual):
        if acoes_semanticas[estado_atual].has_key('func_data'):
            area_dados += acoes_semanticas[estado_atual]['func_data'](pilha_semantica[-1] if len(pilha_semantica) > 0 else None, pilha_semantica)
        if acoes_semanticas[estado_atual].has_key('func_code'):
            area_code += acoes_semanticas[estado_atual]['func_code'](pilha_semantica[-1] if len(pilha_semantica) > 0 else None, pilha_semantica)

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
            chama_acao_semantica(None, automatos[transicao[1]].estado_inicial)
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
            chama_acao_semantica(None, automatos[automato_atual].transicoes[(estado_atual, "")][0], True)
            return le_atomo(atomo, automatos, automatos[automato_atual].transicoes[(estado_atual, "")][0], automato_atual, pilha)
    return ()
    
main()
