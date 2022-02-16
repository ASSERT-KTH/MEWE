#include <time.h>
#include <stdio.h>

int f(int a, int z);

int discriminate(int size) {
   int r = rand();
   printf("Executing variant %d", r%size);
   return r%size;
}

int main() {
   // Setting up the random generator
   srand(time(NULL)); 

   int r = f(1, 10);
   return 1;
}
