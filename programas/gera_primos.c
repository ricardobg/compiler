/*
Insertion sort, ou ordenação por inserção, 
é um simples algoritmo de ordenação, eficiente quando aplicado 
a um pequeno número de elementos. Em termos gerais, ele percorre 
um vetor de elementos da esquerda para a direita e à medida que avança 
vai deixando os elementos mais à esquerda ordenados. O algoritmo de inserção 
funciona da mesma maneira com que muitas pessoas ordenam cartas em um jogo de baralho como o pôquer.
*/
void insertionSort(int numeros[], int tam) {
   int i, j, eleito;
   for (i = 1; i < tam; i++){
      eleito = numeros[i];
      j = i - 1;
      while ((j>=0) && (eleito < numeros[j])) {
         numeros[j+1] = numeros[j];
         j--;
      }
      numeros[j+1] = eleito;
   }
}

/*
O selection sort (do inglês, ordenação por seleção) é um algoritmo de ordenação 
baseado em se passar sempre o menor valor do vetor para a primeira posição 
(ou o maior dependendo da ordem requerida), depois o de segundo menor valor para 
a segunda posição, e assim é feito sucessivamente com os (n-1) elementos restantes, até os últimos dois elementos.
*/

void selection_sort(int num[], int tam) 
 { 
   int i, j, min, aux;
   for (i = 0; i < (tam-1); i++) 
    {
     min = i;
     for (j = (i+1); j < tam; j++) {
       if(num[j] < num[min])
         min = j;
      
     }
     if (i != min) {
       aux = num[i];
       num[i] = num[min];
       num[min] = aux;
     }
   }
 }

/*
O algoritmo Comb sort (ou Combo sort ou ainda algoritmo do pente[1] ) é um algoritmo de ordenação relativamente simples, e faz parte da família de algoritmos de ordenação por troca. Foi desenvolvido em 1980 por Wlodzimierz Dobosiewicz. Mais tarde, foi redescoberto e popularizado por Stephen Lacey e Richard Box em um artigo publicado na revista Byte em Abril de 1991. O Comb sort melhora o Bubble sort, e rivaliza com algoritmos como o Quicksort. A idéia básica é eliminar as tartarugas ou pequenos valores próximos do final da lista, já que em um bubble sort estes retardam a classificação tremendamente. (Coelhos, grandes valores em torno do início da lista, não representam um problema no bubble sort).

O Algoritmo repetidamente reordena diferentes pares de itens, separados por um salto, que é calculado a cada passagem. Método semelhante ao Bubble Sort, porém mais eficiente.

Na Bubble sort, quando quaisquer dois elementos são comparados, eles sempre têm um gap (distância um do outro) de 1. A idéia básica do Comb sort é que a diferença pode ser muito mais do que um. (O Shell sort também é baseado nesta idéia, mas é uma modificação do insertion sort em vez do bubble sort).

O gap (intervalo) começa como o comprimento da lista a ser ordenada dividida pelo fator de encolhimento (em geral 1,3; veja abaixo), e a lista é ordenada com este valor (arredondado para um inteiro se for necessário) para o gap. Então, a diferença é dividida pelo fator de encolhimento novamente, a lista é ordenada com este novo gap, e o processo se repete até que a diferença seja de 1. Neste ponto, o Comb sort continua usando um espaço de 1 até que a lista esteja totalmente ordenada. A fase final da classificação é, portanto, equivalente a um bubble sort, mas desta vez a maioria dos elementos "tartarugas" já foram tratados, assim o bubble sort será eficiente.*/
void combsort(int arr[], int size) {
    float shrink_factor = 1.247330950103979;
    int gap = size, swapped = 1, swap, i;
    while ((gap > 1) || swapped) {
        if (gap > 1)
           gap = gap / shrink_factor;

        swapped = 0;
        i = 0;

        while ((gap + i) < size) {
            if (arr[i] - arr[i + gap] > 0) {
                swap = arr[i];
                arr[i] = arr[i + gap];
                arr[i + gap] = swap;
                swapped = 1;
            }
            ++i;
        }
    }
}


/*
O Quicksort adota a estratégia de divisão e conquista. A estratégia consiste em rearranjar as chaves de modo que as chaves "menores" precedam as chaves "maiores". Em seguida o Quicksort ordena as duas sublistas de chaves menores e maiores recursivamente até que a lista completa se encontre ordenada. [3] Os passos são:

Escolha um elemento da lista, denominado pivô;
Rearranje a lista de forma que todos os elementos anteriores ao pivô sejam menores que ele, e todos os elementos posteriores ao pivô sejam maiores que ele. Ao fim do processo o pivô estará em sua posição final e haverá duas sublistas não ordenadas. Essa operação é denominada partição;
Recursivamente ordene a sublista dos elementos menores e a sublista dos elementos maiores;
A base da recursão são as listas de tamanho zero ou um, que estão sempre ordenadas. O processo é finito, pois a cada iteração pelo menos um elemento é posto em sua posição final e não será mais manipulado na iteração seguinte.
*/

void quickSort(int valor[], int esquerda, int direita)
{
    int i, j, x, y;
    i = esquerda;
    j = direita;
    x = valor[(esquerda + direita) / 2];

    while(i <= j)
    {
        while(valor[i] < x && i < direita)
        {
            i++;
        }
        while(valor[j] > x && j > esquerda)
        {
            j--;
        }
        if(i <= j)
        {
            y = valor[i];
            valor[i] = valor[j];
            valor[j] = y;
            i++;
            j--;
        }
    }
    if(j > esquerda)
    {
        quickSort(valor, esquerda, j);
    }
    if(i < direita)
    {
        quickSort(valor,  i, direita);
    }
}