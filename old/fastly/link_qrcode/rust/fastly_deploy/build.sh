rm -rf target
rm Cargo.lock
WORKDIR=untar
FASTLY_NAME=example_qr.wasm
PROJECT_NAME=QRGEN
BC=$2

core=$(ls ../multivariants/core)
LINKING=""

for bc in $core
do
   LINKING="$LINKING -C link-arg=../multivariants/core/$bc"
done

echo $LINKING

export RUSTFLAGS="-C link-arg=../multivariants/$BC $LINKING -C opt-level=0 -C link-dead-code=on -C linker=$CROW_BACK_CLANG"
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


fastly compute deploy --verbose --path=$WORKDIR/$PROJECT_NAME.tar.gz --service-id=$SERVICE_ID

sleep 30

curl -isvo out.txt https://totally-devoted-krill.edgecompute.app/ 2>&1
