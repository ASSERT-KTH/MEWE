
K="%0:i32 = var
%1:i32 = mulnsw 2:i32, %0
%2:i32 = addnsw %0, %1
infer %2
; Block ID 2"

V="%1crow3:i32 = mul 3:i32, %0
result %1crow3"

K2="%0:i32 = var
%1:i32 = mulnsw 2:i32, %0
infer %1
; Block ID 1"

V2="%2crow3:i32 = or %1, %1
result %2crow3"

OPT=/Users/javierca/Documents/Develop/slumps/souper/third_party/llvm-Release-build/bin/opt
PASS=/Users/javierca/Documents/Develop/slumps/souper/build/libsouperPass.dylib

$OPT  -load $PASS -souper -O0 --souper-no-infer --souper-max-lhs-size=4096 --souper-dont-recheck --souper-debug-level=1 crow_out/f/bitcodes/f.bc -o t.bc --souper-internal-cache --souper-crow-inline-cache --souper-crow-cache-inlinek="$K" --souper-crow-cache-inlinev="$V" --souper-crow-cache-inlinek="$K2" --souper-crow-cache-inlinev="$V2"

# $OPT -load $PASS -souper --souper-dont-recheck=true --souper-max-constant-synthesis-tries=1000 --souper-crow-prevent-sorting=true --souper-enumerative-synthesis-max-verification-load=1 --crow-shuflle-enumerative --solver-timeout=150 --souper-dataflow-pruning=true --souper-crow-prune-select=false --souper-crow-prune-unary-operator-on-constant=false --souper-crow-prune-binary-commutative=false --souper-crow-prune-2const-operation=false --souper-crow-prune-sub=false --souper-crow-prune-constant-select=false --souper-crow --souper-debug-level=1 --souper-synthesis-const-with-cegis --souper-infer-inst --souper-synthesis-comps=mul,select,const,const,shl,lshr,ashr,and,or,xor,add,sub,slt,ult,sle,ule,eq,ne crow_out/f/bitcodes/f.bc  -o t2.bc --souper-crow-port=34191 --souper-crow-workers=2 --souper-crow-host=0.0.0.0