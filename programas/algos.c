int is_palindrome(int n)
{
   int reverse = 0, temp;
   temp = n;
   while( temp != 0 )
   {
      reverse = reverse * 10;
      reverse = reverse + temp%10;
      temp = temp/10;
   }
 
   if ( n == reverse )
      return 1;
   else
      return 0;
}

void selection_sort(int array[], int n)
{
   int c, d, position, swap;

   for ( c = 0 ; c < ( n - 1 ) ; c++ )
   {
      position = c;
 
      for ( d = c + 1 ; d < n ; d++ )
      {
         if ( array[position] > array[d] )
            position = d;
      }
      if ( position != c )
      {
         swap = array[c];
         array[c] = array[position];
         array[position] = swap;
      }
   }
}

int binary_search (int array[100], int search, int n)
{
   int c, first, last, middle, search;
   first = 0;
   last = n - 1;
   middle = (first+last)/2;
 
   while (first <= last) {
      if (array[middle] < search)
         first = middle + 1;    
      else if (array[middle] == search) {
      	return middle+1;
      }
      else
         last = middle - 1;
 
      middle = (first + last)/2;
   }
   return n;
}

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