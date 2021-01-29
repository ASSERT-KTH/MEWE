cargo rustc --target=wasm32-wasi --verbose  -- -v  -C save-temps --emit=llvm-ir

cd target/wasm32-wasi/debug/deps

rm *no-opt*

llvm-as wiw.ll -o wiw.bc

llc wiw.bc -o wiw.o

wasm-ld --verbose --lto-O2 --no-entry wiw.bc -o wiw.wasm

wasm2wat wiw.wasm -o wiw.wat

cd ../../../../
ls