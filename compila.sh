#!/bin/bash 
python2 analisador_sintatico.py language_non_deterministic.json programas/test.c 
java -cp ~/Documents/MLR.jar montador.MvnAsm ~/Documents/t.asm

