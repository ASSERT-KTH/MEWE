rm -rf target

BITCODES_FOLDER=$2
FASTLY_NAME="multivariant.wasm"
WORKDIR=untar
PROJECT_NAME="multivariant"
LINK_ALL=$(find $BITCODES_FOLDER -name "*.bc" -exec bash -c "echo -n ' -C' link-arg={}" \; )

#LINK_ALL="-C link-arg=../sodium4/codecs.multivariant.bc"

export RUSTFLAGS="$LINK_ALL -C linker=$CROW_BACK_CLANG -C opt-level=0 -C lto=off -C inline-threshold=0 -C link-dead-code=on"

cargo build --target=wasm32-wasi --release 2>&1 || exit 1

d=$(date +"%d_%m_%H.%M.%ss"   )
d="$d$3"
cp target/wasm32-wasi/release/$FASTLY_NAME history/${d}_$FASTLY_NAME
mkdir -p history/${d}_src
cp -p src/* history/${d}_src/

cp target/wasm32-wasi/release/$FASTLY_NAME $FASTLY_NAME 
wc -c $FASTLY_NAME
bash extract_wasm_stats.sh $FASTLY_NAME


$WASM2WAT $FASTLY_NAME -o $FASTLY_NAME.wat
$WASM2WAT history/${d}_$FASTLY_NAME -o history/${d}_$FASTLY_NAME.wat

if grep -qE "import \"env\"" $FASTLY_NAME.wat;
then
   # exit if the binary has external dependencies out of WASI or the Fastly ABI
   echo "Error invalid import"
   grep -E "import \"env\"" $FASTLY_NAME.wat 
   exit 1
fi

# Comment this line to follow up with a deployment
exit 0

mkdir -p $WORKDIR/$PROJECT_NAME/bin
cp target/wasm32-wasi/release/$FASTLY_NAME $WORKDIR/$PROJECT_NAME/bin/main.wasm
cp fastly.toml $WORKDIR/$PROJECT_NAME/
cp Cargo.toml $WORKDIR/$PROJECT_NAME/

cd $WORKDIR
tree .

cp $PROJECT_NAME.tar.gz ../history/
tar -cvzf $PROJECT_NAME.tar.gz $PROJECT_NAME

cd ..

fastly compute deploy --verbose --path $WORKDIR/$PROJECT_NAME.tar.gz --service-id $1

echo "Deployed"
cd ..

sleep 65s
curl -isvo out.txt https://totally-devoted-krill.edgecompute.app 2>&1
cat out.txt