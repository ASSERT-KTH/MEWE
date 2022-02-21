myrealpath () (
    if [[ -d $1 ]]; then
        OLDPWD=- CDPATH= cd -P -- "$1" && pwd
    else
        OLDPWD=- CDPATH= cd -P -- "${1%/*}" && printf '%s/%s\n' "$PWD" "${1##*/}"
    fi
)

ROOT=$(dirname $(myrealpath  $0))

# env vars
export LINKER=llvm-link
export MEWEFIXER=$ROOT/multivariant-mixer/build/mewe-fixer

alias mewerustc="echo $ROOT; python3 $ROOT/mewe/rust.py"