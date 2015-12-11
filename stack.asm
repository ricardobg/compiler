ZERO 	  K =0    ; Constante 0 utilizada
UM 		  K =1    ; Constante 1 utilizada
DOIS 	  K =2    ; Constante 2 utilizada na implementação da pilha
STACK 	$ 	=200  ; Pilha em si
STACK_PTR K DOIS ; Ponteiro para o topo da pilha 
TEMP 	  K =0   ; Variavel temporaria
TEMP2 	  K =0   ; Variavel temporaria secundária




PUSH_TEMP K =0    
PUSH_MM MM =0
PUSH 	K /0000 ; Endereco de retorno
		MM PUSH_TEMP ; guarda parametro passado
		LD STACK_PTR ; Carrega stack pointer
		+  DOIS 	 ; Soma com 2
		MM STACK_PTR ; Guarda novo stack pointer
		+ PUSH_MM  	 ; Soma com MM
		MM PUSH_DO   ; Coloca comando de PUSH
		LD PUSH_TEMP ; Carrega parametro
PUSH_DO K  =0
		RS PUSH      ; retorna

POP_LD LD =0 
POP 	K 	/0000    ; Endereco de retorno 	
		LD STACK_PTR ; Carrega stack pointer
		+  POP_LD    ; Soma com LD
		MM POP_DO    ; Coloca comando de Pop
		LD STACK_PTR ; Carrega stack pointer
		-  DOIS 	 ; Tira dois
		MM STACK_PTR ; Guarda stack pointer
POP_DO K  /0000      ; Comando de pop
		RS POP  	 ; Retorna
