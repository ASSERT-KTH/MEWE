

#LINK_ALL=$(find /Users/javierca/Documents/Develop/fastly4edge/sodium2 -name "*.bc")


#for f in $LINK_ALL ; do
#    $OPT -load $SOUPER_LIB --souper --souper-crow --souper-crow-count --souper-crow-count_name "$f" -o /dev/null 2>&1 | grep 'Defined' | awk '{print $2}' | xargs -n 1 echo  $1 "$(basename $f)"
   # echo "===================="
#done 

#echo "$LINK_ALL" | sort | uniq -c | sort -k1
#exit 0

FASTLY_NAME="multivariant.wasm"
WORKDIR=untar
PROJECT_NAME="multivariant"
LINK_ALL=$(find ../sodium2 -name "*.bc" -exec bash -c "echo -n ' -C' link-arg={}" \; )

export RUSTFLAGS="$LINK_ALL"


#export LDFLAGS="-L/Users/javierca/Documents/Develop/fastly4edge/sodium"
#export RUSTFLAGS=''

cargo build --target=wasm32-wasi
d=$(date +"%d%m%H%ss"   )
cp target/wasm32-wasi/debug/$FASTLY_NAME history/${d}_$FASTLY_NAME

cp target/wasm32-wasi/debug/$FASTLY_NAME $FASTLY_NAME 
wasm2wat $FASTLY_NAME -o $FASTLY_NAME.wat
wasm2wat history/${d}_$FASTLY_NAME -o history/${d}_$FASTLY_NAME.wat
grep -E "import \"env\"" $FASTLY_NAME.wat 
#grep -vwE "import \"env\"" sodium.wat > clean.wat
#wat2wasm clean.wat -o sodium.wasm

#exit 0

mkdir -p $WORKDIR/$PROJECT_NAME/bin
cp target/wasm32-wasi/debug/$FASTLY_NAME $WORKDIR/$PROJECT_NAME/bin/main.wasm
cp fastly.toml $WORKDIR/$PROJECT_NAME/
cp Cargo.toml $WORKDIR/$PROJECT_NAME/

cd $WORKDIR
tree .

tar -cvzf $PROJECT_NAME.tar.gz $PROJECT_NAME
cd ..

fastly compute deploy --verbose --path $WORKDIR/$PROJECT_NAME.tar.gz --service-id $1

cd ..

sleep 60s
curl -isvo out.txt https://totally-devoted-krill.edgecompute.app
cat out.txt