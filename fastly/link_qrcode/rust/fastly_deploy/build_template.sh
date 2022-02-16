rm -rf target
FASTLY_NAME=example_qr.wasm
PROJECT_NAME=QRGEN
BINARY_VERSION=$1
BINARY_FINAL_DST=$2
TEMPLATE=$3

cp $TEMPLATE src/main.rs
export RUSTFLAGS="-C link-arg=$1 -C opt-level=0  -C inline-threshold=0 -C link-dead-code=on"
cargo build --release --target=wasm32-wasi || exit 1
$WASM2WAT target/wasm32-wasi/release/$FASTLY_NAME -o $FASTLY_NAME.wat



# validate wasm

if grep -qE "import \"env\"" $FASTLY_NAME.wat;
then
   echo "Error invalid import"
   grep -E "import \"env\"" $FASTLY_NAME.wat 
   exit 1
fi

cp target/wasm32-wasi/release/$FASTLY_NAME $BINARY_FINAL_DST