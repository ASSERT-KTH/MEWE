export RUSTFLAGS=""
# export SERVICE_VERSION=46 export in the python script


FASTLY_NAME="simple_version_retriever.wasm"
WORKDIR=untar
PROJECT_NAME="simple_version_retriever"

touch $PROJECT_NAME/src/main.rs
#touch diversifier/src/lib.rs
cargo build --package $PROJECT_NAME --target=wasm32-wasi 
ls
mkdir -p $WORKDIR/$PROJECT_NAME/bin
cp target/wasm32-wasi/debug/$FASTLY_NAME $WORKDIR/$PROJECT_NAME/bin/main.wasm
cp fastly.toml $WORKDIR/$PROJECT_NAME/
cp simple_version_retriever/Cargo.toml $WORKDIR/$PROJECT_NAME/

cd $WORKDIR

tar -cvzf $PROJECT_NAME.tar.gz $PROJECT_NAME

cd ..
fastly compute deploy --verbose --path $WORKDIR/$PROJECT_NAME.tar.gz --service-id $1