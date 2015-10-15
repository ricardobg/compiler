int a[15], a[15*(2 + 5)];
int teste() {

}
int gera_primos(int primes[10], int n)
{
   int i = 3, count, c;
 
   if (! n++ != 1 )
      primes[0] = 2;
   
   count = 2;
   for (; i < 0; i++, c++) {
      teste();
   }
   while (count <= n)
   {
      c = 2;
      while ( c <= i - 1 )
      {
         if ( i%c == 0 ) {
            c = i;
         }
         ++c;
      }
      if ( c == i )
      {
         primes[count-1] = i;
         count++;
      }
      i++;

   }
   return;
}