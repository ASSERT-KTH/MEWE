# Example 1:

Creating a multivariant from two preexisting libraries. In this example we compile two variants of the same function from source code. We create a multivariant library, and we glue all together with an executable entrypoint. The full scriptinf could be find at `build_multivariant.sh`.

## Variant 1
```C
#include<stdio.h>

int dosomething() {
   // Variant 1 sleeps for 1 second
   sleep(1);
   return 0;
}
```


## Variant 2
```C
#include<stdio.h>

int dosomething() {
   // Variant 2 sleeps for 10 second
   sleep(10);
   return 0;
}
```

## Glue code or entrypoint
```C
#include <time.h>
#include <stdio.h>

int dosomething();

// Random discriminator used by the multivariant library
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
```

## Generating bitcodes from the source code

```bash
clang f1.c -emit-llvm -c -o f1.bc
clang f2.c -emit-llvm -c -o f2.bc
clang entrypoint.c -emit-llvm -c -o entrypoint.bc
```

## Calling our linker

```
$MEWE_LINKER_BIN "f1.bc" "allinone.bc"  --complete-replace=false -merge-function-switch-cases --replace-all-calls-by-the-discriminator -mewe-merge-debug-level=2 -mewe-merge-skip-on-error  -mewe-merge-bitcodes="f2.bc"
```

## Linking with the entry point

```
llvm-link allinone.bc entrypoint.bc -o allinone.complete.bc
```

## Creating the executable binary

```
llc -filetype=obj allinone.complete.bc -o allinone.o
clang allinone.o -o allinone
```

## Executing the multivariant binary

```
-> % time ./allinone           
./allinone  0.00s user 0.00s system 0% cpu 1.195 total
-> % time ./allinone
./allinone  0.00s user 0.00s system 0% cpu 10.005 total
```