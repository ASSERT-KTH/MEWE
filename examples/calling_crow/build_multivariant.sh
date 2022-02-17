clang entrypoint.c -emit-llvm -c -o entrypoint.bc
clang f.c -emit-llvm -c -o f.bc

# Calling CROW to generate some variants
# Run the exploration for 1 minutes only :)
# The generation can take a while, but no more than 1 hour
docker run -it --rm -e REDIS_PASS=""  -v $(pwd)/crow_out:/slumps/crow/crow/storage/out  -v $(pwd):/workdir slumps/crow2:standalone /workdir/f.c %DEFAULT.order 1,2,4,5,5,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21 %DEFAULT.workers 1  %souper.workers 2 %DEFAULT.keep-wasm-files False %DEFAULT.exploration-timeout 60

echo $(find $(pwd)/crow_out/ -name "*.bc" | wc -l) "Variants"
echo "Creating list of variants to bass to the linker"

for module in $(find $(pwd)/crow_out -name "*.bc")
do
    VARIANTS="$VARIANTS,$(echo $module | grep -E "_\[" | awk '{printf "%s", $1}')"
done


######  DOWNLOADING OUR LINKER
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        wget -O build.zip https://github.com/Jacarte/MEWE/releases/download/binaries/build.linux.llvm12.x.x64.zip
elif [[ "$OSTYPE" == "darwin"* ]]; then
        wget -O build.zip https://github.com/Jacarte/MEWE/releases/download/binaries/build.macos.llvm12.zip
elif [[ "$OSTYPE" == "win32" ]]; then
        wget -O build.zip https://github.com/Jacarte/MEWE/releases/download/binaries/build.windows.llvm12.x.winx64.zip
else
        echo "NOT SUPPORTED OS $OSTYPE"
fi


unzip build.zip -d linker

linker/build/mewe-linker  "f.bc" "allinone.bc"  --complete-replace=false -merge-function-switch-cases --replace-all-calls-by-the-discriminator -mewe-merge-debug-level=2 -mewe-merge-skip-on-error  -mewe-merge-bitcodes="$VARIANTS"

# Link the random source for the dispatcher
llvm-link allinone.bc entrypoint.bc -o allinone.complete.bc


llc -filetype=obj allinone.complete.bc -o allinone.o
clang allinone.o -o allinone

./allinone