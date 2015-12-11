/*Teste palindrome
*/

int palindromes[5];

int is_palindrome(int n)
{
   int reverse, temp, rem;
   reverse = 0;
   temp = n;
   while( temp != 0 )
   {
   	  rem=temp%10;
      reverse=reverse*10+rem;
      temp = temp/10;
   }
 
   if ( n == reverse )
      return 1;
   else
      return 0;
}

void main() {
	int i;
	i = 0;
	palindromes[i] = 10;
	i = i + 1;
	palindromes[i] = 101;
	i = i + 1;
	palindromes[i] = 0;
	i = i + 1;
	palindromes[i] = 1;
	i = i + 1;
	palindromes[i] = 212;
	for (i = 0; i < 5; i = i + 1) {
		palindromes[i] = is_palindrome(palindromes[i]);
	}
}