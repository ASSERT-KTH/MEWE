# Example 1:

Creating a multivariant from two preexisting libraries. In this example we compile two variants of the same function from source code. We create a multivariant library, and we glue all together with an executable entrypoint. The full scriptinf could be find at `build_multivariant.sh`.

Copy and paste the following code in your terminal to run this example. Make sure you have LLVM version 12 installed in your computer.

```bash
f1="
#include<stdio.h>

    int dosomething() {
    // Variant 1 sleeps for 1 second
    sleep(1);
    return 0;
}
"

f2="
#include<stdio.h>

int dosomething() {
    // Variant 2 sleeps for 5 second
    sleep(5);
    return 0;
}
"

entrypoint="
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

"

echo "$f1" > f1.c
echo "$f2" > f2.c
echo "$entrypoint" > entrypoint.c

echo "Generating bitcodes"
clang f1.c -emit-llvm -c -o f1.bc
clang f2.c -emit-llvm -c -o f2.bc
clang entrypoint.c -emit-llvm -c -o entrypoint.bc

######  DOWNLOADING OUR LINKER
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        wget -O build.zip https://github.com/Jacarte/MEWE/releases/download/binaries/build.linux.llvm12.x.x64.zip
elif [[ "$OSTYPE" == "darwin"* ]]; then
        wget -O build.zip https://github.com/Jacarte/MEWE/releases/download/binaries/build.macos.llvm12.zip
elif [[ "$OSTYPE" == "win32" ]]; then
        wget -O build.zip https://github.com/Jacarte/MEWE/releases/download/binaries/build.windows.llvm12.x.winx64.zip
else
        echo "NOT SUPPORTED OS $OSTYPE"
fi

unzip build.zip -d linker

linker/build/mewe-linker  "f1.bc" "allinone.bc"  --complete-replace=false -merge-function-switch-cases --replace-all-calls-by-the-discriminator -mewe-merge-debug-level=1 -mewe-merge-skip-on-error  -mewe-merge-bitcodes="f2.bc"

# Link the random source for the dispatcher
llvm-link allinone.bc entrypoint.bc -o allinone.complete.bc


llc -filetype=obj allinone.complete.bc -o allinone.o
clang allinone.o -o allinone

time ./allinone
```