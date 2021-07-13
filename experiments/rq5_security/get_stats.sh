

for f in $(find wasms -name "*.wasm")
do
    FOLDER=$(dirname $f)
    FOLDER=$(basename $FOLDER)
    FNAME=$(basename $f)

    $SEC $f > sec_analysis_out/$FOLDER/$FNAME.txt
done