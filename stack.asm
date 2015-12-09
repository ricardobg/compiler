STACK_PTR K STACK ; Ponteiro para o topo da pilha 
STACK 	$ 	=200  ; Pilha em si
DOIS 	  K =2    ; Constante 2 utilizada na implementação da pilha




PUSH_TEMP K =0    
PUSH_MM MM =0
PUSH 	K /0000 ; Endereco de retorno
		MM PUSH_TEMP ; guarda parametro passado
		LD PUSH_MM   ; Carrega comando MM
		+  STACK_PTR ; Soma com stack pointer
		MM PUSH_DO   ; Coloca comando de PUSH
		LD STACK_PTR ; Carrega stack pointer
		+ DOIS  	 ; Soma com 2
		MM STACK_PTR ; Guarda novo stack pointer
		LD PUSH_TEMP ; Carrega parametro
PUSH_DO K  =0
		RS PUSH      ; retorna

POP_LD LD =0 
POP 	K 	/0000    ; Endereco de retorno 	
		LD STACK_PTR ; Carrega stack pointer
		-  DOIS 	 ; Tira dois
		MM STACK_PTR ; Guarda stack pointer
		+  POP_LD    ; Soma com LD
		MM POP_DO    ; Coloca comando de Pop
POP_DO K  /0000      ; Comando de pop
		RS POP  	 ; Retorna
