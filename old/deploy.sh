cd customWasm
cargo build --target=wasm32-wasi && \

FASTLY_NAME="customWasm.wasm"
WORKDIR=untar
PROJECT_NAME="customWasm"

mkdir -p $WORKDIR/$PROJECT_NAME/bin
cp target/wasm32-wasi/debug/$FASTLY_NAME $WORKDIR/$PROJECT_NAME/bin/main.wasm
cp fastly.toml $WORKDIR/$PROJECT_NAME/
cp Cargo.toml $WORKDIR/$PROJECT_NAME/

cd $WORKDIR
tree .

tar -cvzf $PROJECT_NAME.tar.gz $PROJECT_NAME
cd ..

fastly compute deploy --path $WORKDIR/$PROJECT_NAME.tar.gz --service-id $1

cd ..