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