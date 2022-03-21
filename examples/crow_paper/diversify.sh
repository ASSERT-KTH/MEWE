# Calling CROW to generate some variants
# Run the exploration for 1 minutes only :)
# The generation can take a while, but no more than 1 hour

rm -rf crow_out
# ALL
 docker run -it --rm -e REDIS_PASS="" -e BROKER_USER="admin" -e BROKER_PASS="adminadmin" -p 9898:9898 -p 5672:5672  -v $(pwd)/crow_out:/slumps/crow/crow/storage/out  -v $(pwd):/workdir slumps/crow2:standalone /workdir/f.c %DEFAULT.order 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22 %DEFAULT.workers 3 %souper.souper-debug-level 1  %souper.workers 3 %DEFAULT.keep-wasm-files True %DEFAULT.exploration-timeout 60 %DEFAULT.combinations True %DEFAULT.remove-duplicates False %DEFAULT.prune-equal False

