CURRENT="$PWD"
OUT_FOLDER="multivariant3"
ORIGINAL_BITCODE=$1
MEWE_FOLDER=$2
VARIANTS_FOLDER=$3
shift 3

args="--instrument-only-variants --instrument-include=generate_fractal,lipv_image,fliph_image,blur_image,crop_image,grayscale_image,invert_image,rotate90_image,unsharpen_image"




CURRENT=1
MULTIVARIANTS="$(find ./bitcodes3 -name '*.bc' -exec echo -n ","{} \;)" #"$(find $VARIANTS_FOLDER -name '*.bc' -exec echo -n ","{} \;)"

echo $MULTIVARIANTS
# ORIGINAL_BITCODE=./bitcodes/image_rs4_24308_[xwjjuR2i].bc
# Merge all in one big fat

# Link all originals


$MEWE_FOLDER/build/crow-linker $ORIGINAL_BITCODE "$OUT_FOLDER/allinone.multivariant.i.bc" -complete-replace=false -merge-function-switch-cases --replace-all-calls-by-the-discriminator --instrument-function --override -crow-merge-debug-level=2 -crow-merge-skip-on-error $args -crow-merge-bitcodes="$MULTIVARIANTS"  2> multivariant3/i.map.txt


$MEWE_FOLDER/build/crow-linker $ORIGINAL_BITCODE "$OUT_FOLDER/allinone.multivariant.bc" -complete-replace=false --replace-all-calls-by-the-discriminator -merge-function-switch-cases  --override -crow-merge-debug-level=2 -crow-merge-skip-on-error -crow-merge-bitcodes="$MULTIVARIANTS"


llvm-dis "$OUT_FOLDER/allinone.multivariant.i.bc" -o multivariant/allinone.multivariant.i.bc.ll

#find out_group -name "*.multivariant.bc" -exec cp -f {} $OUT_FOLDER/ \;
