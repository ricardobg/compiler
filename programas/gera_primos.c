void gera_primos(int primes[], int n)
{
   int  i = 3, count, c;
 
   if ( n >= 1 )
   {
      primes[0] = 2;
   }
 
   for ( count = 2 ; count <= n ;  )
   {
      for ( c = 2 ; c <= i - 1 ; c++ )
      {
         if ( i%c == 0 )
            c = i;
      }
      if ( c == i )
      {
         primes[count-1] = i;
         count++;
      }
      i++;
   }
}