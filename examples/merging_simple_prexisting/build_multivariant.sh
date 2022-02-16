clang f1.c -emit-llvm -c -o f1.bc
clang f2.c -emit-llvm -c -o f2.bc
clang entrypoint.c -emit-llvm -c -o entrypoint.bc

$MEWE_LINKER_BIN "f1.bc" "allinone.bc"  --complete-replace=false -merge-function-switch-cases --replace-all-calls-by-the-discriminator -mewe-merge-debug-level=2 -mewe-merge-skip-on-error  -mewe-merge-bitcodes="f2.bc"

# Link the random source for the dispatcher
llvm-link allinone.bc entrypoint.bc -o allinone.complete.bc


llc -filetype=obj allinone.complete.bc -o allinone.o
clang allinone.o -o allinone