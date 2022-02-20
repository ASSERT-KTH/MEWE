rm -rf target/wasm32-wasi
rm withdeps.bc
rm withdeps2.bc

target="wasm32-wasi"

# Find tehe defined binaries
# It is betters to add this behavior in a build.rs
RUSTFLAGS="--emit=llvm-bc  -C linker-plugin-lto=no" cargo build --release --target=$target || exit 1

# rm target/$target/release/deps/main*
cp multivariants/allinone.multivariant.bc withdeps.bc  || exit 1
llvm-dis withdeps.bc

wasm-ld withdeps.bc --export-all --allow-undefined --no-entry -o p1.wasm
#$WASM2WAT p1.wasm --no-check -o p1.wat

../../../multivariant-mixer/build/rename --version

echo "Renaming main"
../../../multivariant-mixer/build/rename withdeps.bc withdeps2.bc --funcname="main" --replace="main2" || exit 2

llvm-dis withdeps2.bc


../../../multivariant-mixer/build/rename withdeps2.bc withdeps3.bc --funcname="_ZN4main4main17h85cf907bd6a78b6fE" --replace="internal_main" || exit 2

llvm-dis withdeps3.bc

# rustc -C link-arg=withdeps.bc --target=wasm32-wasi -o main.wasm
rustc -C link-arg=withdeps3.bc -C opt-level=0 --verbose  main.rs --target=wasm32-wasi 

$WASM2WAT main.wasm -o main.wat  || exit 3