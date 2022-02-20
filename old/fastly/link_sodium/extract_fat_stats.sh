


s1=$(find original -name "*.bc" -exec wc -c {} \; | awk '{print $1}')

s2=$(find multivariant -name "*.bc" -exec wc -c {} \; | awk '{print $1}')

echo $s1 $s2
bc -l <<< "100*$s2/$s1"


if [[ ! $WASMLD ]]
then
    echo "where is the wasm-ld?"
    exit 1
fi



if [[ ! $WASM2WAT ]]
then
    echo "where is the was2wat?"
    exit 1
fi


find original -name "*.bc" -exec $WASMLD {}  --allow-undefined --export-all --no-entry -o {}.wasm \;
find original -name "*.wasm" -exec $WASM2WAT {}   -o {}.wat \;
find original -name "*.wat" -exec bash -c "cat {} | grep export " \; | wc -l
ws1=$(find original -name "*.wasm" -exec wc -c {} \;| awk '{print $1}')



find multivariant -name "*.bc" -exec $WASMLD {}  --allow-undefined --export-all --no-entry -o {}.wasm \;
find multivariant -name "*.wasm" -exec $WASM2WAT {}   -o {}.wat \;
find multivariant -name "*.wat" -exec bash -c "cat {} | grep export " \; | wc -l
ws2=$(find multivariant -name "*.wasm" -exec wc -c {} \;| awk '{print $1}')

echo $ws1 $ws2

bc -l <<< "100*$ws2/$ws1"