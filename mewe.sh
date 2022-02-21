abspath() {
  [[ $1 = /* ]] && printf "%s\n" "$1" || printf "%s\n" "$PWD/$1"
}

ROOT=$(dirname $(abspath  $0))

# env vars
export LINKER=llvm-link
export MEWEFIXER=$ROOT/multivariant-mixer/build/mewe-fixer

alias mewerustc="echo $ROOT; python3 $ROOT/mewe/rust.py"