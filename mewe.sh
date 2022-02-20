ROOT=$(dirname $(realpath  $0))

# env vars
export LINKER=llvm-link
export MEWEFIXER=$ROOT/multivariant-mixer/build/mewe-fixer

alias mewerustc="echo $ROOT; python3 $ROOT/mewe/rust.py"