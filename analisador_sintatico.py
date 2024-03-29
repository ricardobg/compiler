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
special_expression = False

class TabelaSimbolos:
    def __init__(self):
        self.tabela_simbolos_geral = {}
        self.tabela_simbolos_func = []
        self.current_function = None
    def has_key(self, key):
        return reduce(lambda r, x: r or x.has_key(key), [self.tabela_simbolos_geral] + self.tabela_simbolos_func, False) 
    def get(self, key):
        if not self.has_key(key):
            raise ValueError("Símbolo '" + key + "' não declarado")
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
        pass
       # print "Tabela de Simbolos\n\n"
       # print "     Global"
       # for k in self.tabela_simbolos_geral:
        #    g = self.tabela_simbolos_geral[k]
        #    print  "    '" + str(g.nome) + "' | " + g.tipo + "|" + g.label

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
            vetor = Simbolo(pilha[0].valor + '[]')
            pont  = Simbolo(pilha[0].valor + '[]', v.valor)
            codigo += tabela_simbolos.put(v.valor, pont, var_global).label + '   K   ' + vetor.label + ' ; ponteiro de vetor ' + v.valor + '\n'
            codigo += vetor.label + '   $   =' + pilha[1:][k+2].valor + ' ; vetor ' + v.valor + '\n'
        else:
            codigo += tabela_simbolos.put(v.valor, Simbolo(pilha[0].valor, v.valor), var_global).label + '   K   =' + (pilha[1:][k+2].valor if pilha[1:][k+1].valor == '=' else '0') + ' ; inteiro ' + v.valor + '\n'
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
            #Cria ponteiro para vetor
            pont  = Simbolo(pilha[3:][k-1].valor + '[]', v.valor)
            args.append(pont)
            codigo += tabela_simbolos.put(v.valor, args[-1] , False).label + '   K   =0 ; vetor ' + v.valor + '\n'
        else:
            args.append(Simbolo(pilha[3:][k-1].valor, v.valor))
            codigo += tabela_simbolos.put(v.valor, args[-1], False).label + '   K   =0 ; inteiro ' + v.valor + '\n'


    func.args = args
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

    cp_args = tabela_simbolos.current_function.args[:]
    cp_args.reverse()
    for arg in cp_args:
        codigo += '   SC    POP ; poping ' + arg.nome + '\n'
        codigo += '   MM   ' + arg.label + '\n' 
    del pilha[:] 
    return codigo

#Ler ou escrever em vetor
def acessa_vetor(atomo_vetor, eh_leitura, stack):
    codigo = ''
    #posição de acesso está no topo da pilha
    codigo += '     SC     POP\n'
    codigo += '     *      DOIS\n'
    codigo += '     +      ' + ('POP_LD' if eh_leitura else 'PUSH_MM') + '\n'
    codigo += '     MM     TEMP\n'
    codigo += '     LD     ' + tabela_simbolos.get(atomo_vetor.valor).label + ' ; carrega endereco de ' +  tabela_simbolos.get(atomo_vetor.valor).nome + '\n'
    codigo += '     +       TEMP\n'
    simb = Simbolo('int').label
    codigo += '     MM     ' + simb + ' ; escreve instrucao\n'
    if not eh_leitura:
        if stack[-1].valor in ['++', '--']:
            simb2 = Simbolo('int').label
            codigo += '     -      PUSH_MM\n'
            codigo += '     +      POP_LD\n'
            codigo += '     MM     ' + simb2 + ' ; escreve instrucao\n'
            codigo += simb2 + '   K      =0\n'
            codigo += '     ' + ('+' if stack[-1].valor == '++' else '-') + '       UM\n';
        else:
            #Valor para gravar está no topo da pilha também
            codigo += '     SC    POP\n'
    codigo += simb + '   K      =0\n'
    return codigo

#
#Expression
#
pilha_expression = []
pilha_list_expression = []


def enter_expression(token, pilha):
    global special_expression
    global pilha_expression, pilha_list_expression
    if len(pilha_expression) == 0 and len(pilha_list_expression) == 0:
        if DEBUG:
            print "[ACAO SEMANTICA] -> Chamou Expression"
        if not special_expression:
            pilha_expression.append(pilha[:])
            del pilha[:]
        else:
            pilha_expression.append([])
    return ''

def new_expression(token, pilha): 
    global pilha_expression, pilha_list_expression
    if len(pilha_list_expression) != 0:
        return ''
    if DEBUG:
        print "[ACAO SEMANTICA] -> Chamou Expression dentro de Expression"
    pilha_expression.append(pilha[:])
    del pilha[:]
    return ''

def new_list_expression(token, pilha): 
    global pilha_list_expression
    if DEBUG:
        print "[ACAO SEMANTICA] -> Chamou List Expression dentro de Expression"
    pilha_list_expression.append(pilha[:])
    del pilha[:]
    return ''

def end_list_expression(token, pilha):
    global pilha_list_expression
    if DEBUG:
        print "[ACAO SEMANTICA] -> Fim de List Expression dentro de Expression"
    pilha[:] = pilha_list_expression.pop() + pilha[:]
    return ''

def leave_expression(token, pilha):
    global pilha_expression, pilha_list_expression
    if len(pilha_list_expression) != 0:
        return ''
    if DEBUG:
        print "[ACAO SEMANTICA] -> Fim de Expression"
    codigo = ''
    
    if len(pilha_expression) > 1:
        pilha[:] = pilha_expression.pop() + pilha[:]        
    else:
        ret = trata_piha(pilha)
        del pilha[:]
        pilha[:] = pilha_expression.pop()
        return ret
    return ''

#Coloca resultado no topo da pilha
def create_code_from_npr(stack, left_side=False):
    global tabela_simbolos, area_constantes
    codigo = ''
    vetor_access = []
    for k,i in enumerate(stack):
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
            if len(stack) > k+1 and stack[k+1].valor  == '[': 
                vetor_access.append(i)
            #Variável normal
            else:
                if tabela_simbolos.get(i.valor).tipo == 'function':
                    codigo += '     SC     ' +  tabela_simbolos.get(i.valor).label + ' ; chama ' + i.valor + '\n'
                else:
                    codigo += '     LD     ' + tabela_simbolos.get(i.valor).label + " ; carrega " + i.valor + "\n" 
                codigo += '     SC     PUSH\n'
        #vetor
        elif i.valor == ']':
            codigo += acessa_vetor(vetor_access.pop(), not left_side, stack)
            if not left_side:
                codigo += '     SC     PUSH\n'
            else:
                break
        #operadores unários
        elif i.is_unary:
            #tira do topo da pilha
            codigo += '     SC     POP\n'
            if i.valor == '-':
                codigo += '     MM      TEMP\n'
                codigo += '     LV      =0\n'
                codigo += '     -       TEMP\n'
            elif i.valor == '!': 
                verd_simb = Simbolo('int').label
                fim_simb = Simbolo('int').label
                codigo += '     JZ   ' + verd_simb + ' ; pula para true\n'
                codigo += '          LV =0 ; eh 0 \n' 
                codigo += '     JP     ' + fim_simb + ' \n'
                codigo += verd_simb + '    LV =1 ; eh 1\n'
                codigo += fim_simb #sem quebra de linha: proxima linha começa deste label 
            #Coloca resultado no topo da pilha
            codigo += '     SC     PUSH\n'
        #operadores binários 
        elif i.valor != '[':
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
                    #guarda dividendo
                    codigo += '     MM    TEMP2\n'
                    codigo += '     /     TEMP\n'   
                    codigo += '     *     TEMP\n'
                    codigo += '     MM    TEMP\n'
                    codigo += '     LD    TEMP2\n'
                    codigo += '     -     TEMP\n'
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
    return codigo


 

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
            equal = out_expression[:] + operators[:]
            del out_expression[:]
            del operators[:]
        elif i.valor in ['++', '--']:
            equal = out_expression[:] + operators[:] + [i]
            del out_expression[:]
            del operators[:]
        elif i.valor == '[':
            out_expression.append(i)
        elif i.valor != ',':
            if i.valor == '(':
                operators.append(i)   
            elif i.valor == ')':
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
                        if topo.valor == i.valor and not topo.is_unary:
                            out_expression.append(operators.pop())
                        elif topo.valor in ['[', ']']:
                            out_expression.append(operators.pop())
                        elif topo.is_unary and i.valor not in ['[', ']']:
                            out_expression.append(topo)
                        elif topo.valor in ['*', '/'] and i.valor not in ['[', ']'] and not i.is_unary:
                            out_expression.append(operators.pop())
                        elif topo.valor in ['+', '-'] and i.valor not in ['[', ']', '*', '/'] and not i.is_unary:
                            out_expression.append(operators.pop())
                        elif topo.valor in ['<', '>', '<=', '>='] and i.valor not in ['[', ']', '*', '/', '+', '-'] and not i.is_unary:
                            out_expression.append(operators.pop())
                        elif topo.valor in ['==', '!='] and i.valor not in ['[', ']', '*', '/', '+', '-','<', '>', '<=', '>='] and not i.is_unary:
                            out_expression.append(operators.pop())
                        elif topo.valor in ['&&'] and i.valor not in ['[', ']', '*', '/', '+', '-','<', '>', '<=', '>=', '==', '!='] and not i.is_unary:
                            out_expression.append(operators.pop())
                        elif topo.valor in ['||'] and i.valor not in ['[', ']', '*', '/', '+', '-','<', '>', '<=', '>=', '==', '!=', '&&'] and not i.is_unary:
                            out_expression.append(operators.pop())
                        else:
                            break
                operators.append(i)
    operators.reverse()
    out_expression = out_expression + operators
    #Tratar pilha
    codigo = create_code_from_npr(out_expression)
   
    #Pop para colocar resultado no acumulador
    if len(out_expression) > 0:
        codigo += '     SC     POP\n'
    #Verifica se tem atribuição e faz
    if len(equal) > 0:
        if len(equal) == 1: 
            codigo += '     MM      ' + tabela_simbolos.get(equal[0].valor).label + ' ; salva no ' + equal[0].valor + '\n'
        elif len(equal) == 2:
            codigo += '     ' + ('+' if equal[1].valor == '++' else '-') + '       UM\n';
            codigo += '     MM      ' + tabela_simbolos.get(equal[0].valor).label + ' ; salva no ' + equal[0].valor + '\n'
        else:
            #vetor
            codigo += '     SC     PUSH\n'
            codigo += create_code_from_npr(equal, True)
    return codigo

#
# Comandos
#
class Comando:
    def __init__(self, tipo, before_condition, end, before_update=None):
        self.tipo = tipo
        self.before_condition = before_condition
        self.end = end
        self.before_update = before_update

pilha_comandos = []



def initial_value_for(token, pilha):
    global tabela_simbolos, pilha_comandos
    if DEBUG:
        print "[ACAO SEMANTICA] -> DASASDASDSD de variável"
    if len(pilha) > 4:
        sim = Simbolo('int', pilha[-2].valor)
        lbl = tabela_simbolos.put(pilha[-2].valor, sim).label
        pilha[:] = pilha[:-1]
        return '    MM      ' + lbl + ' \n'
    else:
        lbl = tabela_simbolos.get(pilha[-2].valor).label
        pilha[:] = pilha[:-1]
        return '    MM      ' + lbl + ' \n'

def init_for(token, pilha):
    global tabela_simbolos, pilha_comandos
    codigo = ''
    if len(pilha) >= 4:
        if DEBUG:
            print "[ACAO SEMANTICA] -> Declaração de variável"
        #tem declaração
        codigo += tabela_simbolos.get(pilha[-1].valor).label + '   K   =0 ; inteiro ' + pilha[-1].valor + '\n'

    pilha[:] = pilha[0:2]
    return codigo

def init_command(token, pilha):
    global tabela_simbolos, pilha_comandos
    if DEBUG:
        print "[ACAO SEMANTICA] -> Início de comando"
    for k,v in enumerate(pilha):
        if v.valor == '{' or v.valor == '(':
            del pilha[k]
    #if len(pilha) == 1:
    #    pilha[:] = [pilha[-2]] + [pilha[-1]]
   # else:
   #     pilha[:] = [pilha[-2]] + [pilha[-1]]
    if token != None and token.valor == 'else':
        simb = Simbolo('int').label
        pilha_comandos.append(Comando('else', pilha_comandos[-1].end, simb))
        del pilha[:]
        #Pula para fim (acabou if)
        return  '   JP     ' + simb + '\n' + pilha_comandos[-2].end + ' +   ZERO\n'
    elif len(pilha) > 0 and pilha[0].valor == 'for':
        print 'COMANDO FOR'
        simb = Simbolo('int').label
        pilha_comandos.append(Comando('for', simb, Simbolo('int').label, Simbolo('int').label))
        del pilha[:]
        return simb + ' +   ZERO\n'
    else:
        simb = Simbolo('int').label
        pilha_comandos.append(Comando(pilha[0].valor, simb, Simbolo('int').label))
        del pilha[:]
        return simb + ' +   ZERO\n'




def middle_command(token, pilha):
    global tabela_simbolos, pilha_comandos
    if DEBUG:
        print "[ACAO SEMANTICA] -> Comando pós-condição"
    print [i.valor for i in pilha]
    del pilha[:]
    simb = Simbolo('int').label
    pilha_comandos[-1].execution = simb
    if pilha_comandos[-1].tipo != 'for':
        return '    JZ    ' + pilha_comandos[-1].end + '\n' + simb + ' +   ZERO\n'
    else:
        special_for(token, pilha)
        return '    JZ    ' + pilha_comandos[-1].end + '\n      JP   ' + simb + '\n ' + pilha_comandos[-1].before_update  + ' +   ZERO\n'

def middle_command_for(token, pilha):
    global tabela_simbolos, pilha_comandos, special_expression
    if DEBUG:
        print "[ACAO SEMANTICA] -> Comando pós-atualização do for"
    special_expression = False
    return '    JP      ' + pilha_comandos[-1].before_condition + '\n' +  pilha_comandos[-1].execution + '   +  ZERO\n'
    


def end_command(token, pilha):
    global tabela_simbolos, pilha_comandos
    if DEBUG:
        print "[ACAO SEMANTICA] -> Fim de comando"
    del pilha[:]
    #Depende do tipo
    last_cmd = pilha_comandos.pop() 
    if last_cmd.tipo == 'if':
        return last_cmd.end + ' +   ZERO\n'
    elif last_cmd.tipo == 'else': 
        #desempilha if 
        pilha_comandos.pop() 
        return last_cmd.end + ' +   ZERO\n'
    elif last_cmd.tipo == 'while':
        return '    JP      ' + last_cmd.before_condition  + '\n' + last_cmd.end + ' +   ZERO\n'
    elif last_cmd.tipo == 'for':
        return '    JP      ' + last_cmd.before_update  + '\n' + last_cmd.end + ' +   ZERO\n'
    return ''

def return_command(token, pilha):
    global tabela_simbolos, pilha_comandos
    if DEBUG:
        print "[ACAO SEMANTICA] -> Comando Return"
    del pilha[:]
    return '    RS   ' + tabela_simbolos.current_function.label + '\n'

def special_for(token, pilha):
    global special_expression
    special_expression = True
    return ''

def limpa_pilha2(token, pilha):
    if DEBUG:
        print "[ACAO SEMANTICA] -> LIMPA PILHA"
    del pilha[:]
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
    #Métodos de expression
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
    },
    '219': {
        'func_code': new_list_expression
    },
    '220': {
        'func_code': end_list_expression
    },
    #Comandos
    '144': { #do while
        'func_code': init_command
    },

    '88': { #while
        'func_code': init_command
    },
    '90': {
        'func_code': middle_command
    },
    '91': {
        'func_code': end_command
    },


    '121': { #for
        'func_code': init_command  
    },
    '109': {
        'func_code': initial_value_for
    },
    '110': {
        'func_data': init_for
    },
    '123': {
        'func_code': middle_command
    },
    '125': {
        'func_code': middle_command_for
    },
    '126': {
        'func_code': end_command
    },

    '66': { #if
        'func_code': init_command
    },
    '68': {
        'func_code': middle_command
    },
    '77': {
        'func_code': end_command
    },
    '78': { #else
        'func_code': init_command
    },
    '135': { #return
        'func_code': return_command    
    }
    
}
#Analisador Léxico
class Atomo:
    def __init__(self, tipo, valor, n_linha, n_coluna, is_unary=False):
        self.tipo = tipo
        self.valor = valor
        self.n_linha = n_linha
        self.n_coluna = n_coluna
        self.is_unary = is_unary

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
            elif token in simbolos or token in simbolos_compostos:
                if token in ['++', '--', '!']:
                    atomos.append(Atomo(token, token, n_linha, pos, True)) 
                elif token == '-'  and (len(atomos) == 0 or (atomos[i-1].tipo not in ['NUMBER', 'NAME'] and atomos[i-1].valor not in [')', ']'])):
                    # - unário
                    atomos.append(Atomo(token, token, n_linha, pos, True))
                else:
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
        res = '@ /0000 \n' + 'MAIN    SC  ' + tabela_simbolos.get('main').label + ' ; chama main\n' + 'END     HM   END ; Fim\n' + area_dados + area_code + area_constantes + open('stack.asm').read() +  "# TEMP\n"
        print res
        open('/home/ricardo/Documents/t.asm', 'w').write(res) 
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
                chama_acao_semantica(None, desempilha[0])
                return le_atomo(atomo, automatos, desempilha[0], desempilha[1], pilha)

    # Rejeita ou desempilha
    else:
        if estado_atual in automatos[automato_atual].estados_finais:
            # Tenta desmpilhar
            if not len(pilha) == 0:
                if DEBUG:
                    print automato_atual + ": Saindo do estado " + estado_atual + " e desempilhando estado " + pilha[-1][0] + u", indo para a submáquina " + pilha[-1][1]
                desempilha = pilha.pop()
                chama_acao_semantica(None, desempilha[0])
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
