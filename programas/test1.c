/*Teste
*/
int tem1, tem2;
int vetor[100];


void preenche_vetor(int vetor[], int inicial, int passo, int tam) {
	for (int i = 0; i < tam; i = i + 1) {
		vetor[i] = inicial + passo * i;
	}
}

int tem_valor(int vetor[], int valor, int tamanho) {
	int encontrou;
	encontrou = 0;
	for (int i = 0; i < tamanho; i = i + 1) {
		encontrou = encontrou || (vetor[i] == valor);
	}
	return encontrou;
}


void main() {
	preenche_vetor(vetor, 5, 2, 100);
	tem1 = tem_valor(vetor, 5 + 10*2, 100);
	tem2 = tem_valor(vetor, 5 + 20*2 - 3, 100);
}

