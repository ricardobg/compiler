int binary_search (int array[100], int search, int n)
{
   int c, first, last, middle, search;
   first = 0;
   last = n - 1;
   middle = (first+last)/2;
 
   while (first <= last) {
      if (array[middle] < search)
         first = middle + 1;    
      else {
         if (array[middle] == search) {
      	  return middle+1;
         }
      }
      else
         last = middle - 1;
 
      middle = (first + last)/2;
   }
   return n;
}
