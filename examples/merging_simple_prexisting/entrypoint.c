#include <time.h>
#include <stdio.h>

int dosomething();

int discriminate(int size) {
   int r = rand();
   return r%size;
}

int main() {
   // Setting up the random generator
   srand(time(NULL)); 

   int r = dosomething();
   return 1;
}
