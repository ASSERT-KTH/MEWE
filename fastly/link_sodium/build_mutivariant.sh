CURRENT="$PWD"
OUT_FOLDER="multivariants"
ORIGINAL_FOLDER=$1
VARIANTS_FOLDER=$2
shift
shift

while [ -n "$1" ]; do

    case "$1" in
        -i)
            # Instrument functions for callgraph
            args="$args --instrument-function "
        ;;
      -bb)
          # Instrument by BB
          args="$args --instrument-bb "
        ;;
      -n1)
          # Instrument by BB
          args="$args --merge-function-switch-cases "
        ;;

      -o)
          # Instrument by BB
          OUT_FOLDER=$2
          mkdir -p $OUT_FOLDER
          shift
        ;;
    esac
    shift
done



find find "$VARIANTS_FOLDER" -name "*_\[*.bc" | wc -l

CURRENT=1
MULTIVARIANTS=""
for module in $(ls $VARIANTS_FOLDER)
do
  if [ -d "$VARIANTS_FOLDER/$module" ]
  then
    VARIANTS="$VARIANTS,$(find "$VARIANTS_FOLDER/$module" -name "*_\[*.bc" | grep -E "_\[" | awk '{printf "%s,", $1}')"
    echo $module
  fi
done

# export $LINKER=/Users/javierca/Documents/Develop/slumps/souper/third_party/llvm-Release-build/bin/llvm-link
# Link all originals using the regular LLVM linker
$LINKER $(find $ORIGINAL_FOLDER -name "*.bc") -o "allinone.bc"

mkdir -p "$OUT_FOLDER/original"
mkdir -p "$OUT_FOLDER/instrumented"
mkdir -p "$OUT_FOLDER/multivariant"

rm "$OUT_FOLDER/instrumented/allinone.multivariant.i.bc"
rm "$OUT_FOLDER/multivariant/allinone.multivariant.bc"
rm "$OUT_FOLDER/original/allinone.bc"

cp "allinone.bc" "$OUT_FOLDER/original/allinone.bc"

echo "Building instrumented multivariant $args"
$MEWE_LINKER_BIN "allinone.bc" "$OUT_FOLDER/instrumented/allinone.multivariant.i.bc" -complete-replace=false -merge-function-switch-cases --replace-all-calls-by-the-discriminator --instrument-function --override -crow-merge-debug-level=1 -crow-merge-skip-on-error  -crow-merge-bitcodes="$VARIANTS" 1>i.out.txt  2> i.map.txt || exit 1

echo "Building  multivariant $args"
$MEWE_LINKER_BIN "allinone.bc" "$OUT_FOLDER/multivariant/allinone.multivariant.bc" -complete-replace=false -merge-function-switch-cases --replace-all-calls-by-the-discriminator --override -crow-merge-debug-level=1 -crow-merge-skip-on-error  -crow-merge-bitcodes="$VARIANTS"

#find out_group -name "*.multivariant.bc" -exec cp -f {} $OUT_FOLDER/ \;
 