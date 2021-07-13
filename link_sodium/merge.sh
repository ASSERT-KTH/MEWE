ORIGINAL_BC=$1
VARIANT_BC=$2
FUNCTION_NAME_IN_VARIANT=$3


echo $ORIGINAL_BC $VARIANT_BC $FUNCTION_NAME_IN_VARIANT

# Rename function
$OPT -load $SOUPER_LIB --souper --souper-crow --souper-crow-rename --souper-crow-mangle-function="randombytes_buf" --souper-crow-mangle-function-name="tt5"  $VARIANT_BC  -o isolated.bc

llvm-dis isolated.bc -o j.ll
llvm-dis $ORIGINAL_BC -o i.ll


sed 's/internal//g' j.ll > j1.ll
sed 's/internal//g' i.ll > i1.ll


llvm-as j1.ll -o j1.bc
llvm-as i1.ll -o i1.bc

#llvm-as k.ll -o k.bc

llvm-link -override i1.bc j1.bc -o $ORIGINAL_BC/merge.bc