rm -rf target
PACKAGE_NAME="multivariant_zxing"
TYPE="debug"
RUSTFLAGS="" 
build_out=$(cargo build  --target=wasm32-wasi -v  2>&1)


THE_PACKAGE=$(echo "$build_out"  | grep "rustc --crate-name $PACKAGE_NAME")
THE_PACKAGE=$(echo $THE_PACKAGE | sed s/Running//g)

THE_PACKAGE=$(echo $THE_PACKAGE | sed s/\`//g)

EXTRA_FLAGS="-Clto -C embed-bitcode=yes --emit=llvm-bc -C linker-plugin-lto "

eval "$THE_PACKAGE $EXTRA_FLAGS"

rm -rf bitcodes
mkdir -p bitcodes
find target -name "$PACKAGE_NAME*.bc" -exec cp {} bitcodes/$PACKAGE_NAME.bc \;

#rustc --crate-name multivariant_zxing --edition=2018 src/lib.rs --error-format=json --json=diagnostic-rendered-ansi --crate-type lib --emit=dep-info,metadata,link -C embed-bitcode=no -C debug-assertions=off -C metadata=60d956b70724dc62 -C extra-filename=-60d956b70724dc62 --out-dir /Users/javierca/Documents/Develop/fastly4edge/link_zxing/rust/target/wasm32-wasi/release/deps --target wasm32-wasi -L dependency=/Users/javierca/Documents/Develop/fastly4edge/link_zxing/rust/target/wasm32-wasi/release/deps -L dependency=/Users/javierca/Documents/Develop/fastly4edge/link_zxing/rust/target/release/deps --extern image=/Users/javierca/Documents/Develop/fastly4edge/link_zxing/rust/target/wasm32-wasi/release/deps/libimage-c7b7cf96e8b2e87a.rmeta --extern lazy_static=/Users/javierca/Documents/Develop/fastly4edge/link_zxing/rust/target/wasm32-wasi/release/deps/liblazy_static-2cc5ee23317b20eb.rmeta --extern libc=/Users/javierca/Documents/Develop/fastly4edge/link_zxing/rust/target/wasm32-wasi/release/deps/liblibc-1fc36ed5a6791213.rmeta --extern qrcode=/Users/javierca/Documents/Develop/fastly4edge/link_zxing/rust/target/wasm32-wasi/release/deps/libqrcode-61b109df6ddd7d70.rmeta --extern rand=/Users/javierca/Documents/Develop/fastly4edge/link_zxing/rust/target/wasm32-wasi/release/deps/librand-248386f62666d842.rmeta -C lto -C embed-bitcode=yes --emit=llvm-bc