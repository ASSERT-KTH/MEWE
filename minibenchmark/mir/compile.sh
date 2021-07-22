
clang --target=wasm32-unknown-wasi -emit-llvm -c $1 -o $1.bc
llc -asm-verbose -o $1.s $1.bc