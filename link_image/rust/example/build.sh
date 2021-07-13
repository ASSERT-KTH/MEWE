rm -rf target
rm Cargo.lock
WORKDIR=untar
FASTLY_NAME=example_img.wasm
PROJECT_NAME=QRGEN
BC=$2
export RUSTFLAGS="-C link-arg=../../multivariant/$BC -C linker-plugin-lto=no -C opt-level=0 -C link-dead-code=on"
cargo build --release --target=wasm32-wasi || exit 1
$WASM2WAT target/wasm32-wasi/release/$FASTLY_NAME -o $FASTLY_NAME.wat
cp target/wasm32-wasi/release/$FASTLY_NAME $FASTLY_NAME
# validate wasm

if grep -qE "import \"env\"" $FASTLY_NAME.wat;
then
   echo "Error invalid import"
   grep -E "import \"env\"" $FASTLY_NAME.wat 
   exit 1
fi

# package for fastly

rm -rf $WORKDIR
mkdir -p $WORKDIR/$PROJECT_NAME/bin
cp target/wasm32-wasi/release/$FASTLY_NAME $WORKDIR/$PROJECT_NAME/bin/main.wasm
cp fastly.toml $WORKDIR/$PROJECT_NAME/
cp Cargo.toml $WORKDIR/$PROJECT_NAME/

cd $WORKDIR
tree .

tar -cvzf $PROJECT_NAME.tar.gz $PROJECT_NAME

cd ..


fastly compute deploy --verbose --path=$WORKDIR/$PROJECT_NAME.tar.gz --service-id=$SERVICE_ID || exit 1

sleep 30

# curl -isv --data-binary "@kth.png" https://totally-devoted-krill.edgecompute.app/ 2>&1
