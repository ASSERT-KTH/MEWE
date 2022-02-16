
# multivariant-linker

We extended the LLVM linker tool to merge several libraries into a big one despite symbols duplication. It outputs a big library containing semantically equivalent functions (yet statically different) for which we orchestrate their execution at runtime. Our linker creates LLVM multivariant libraries out of a collection of LLVM libraries as input. To build this tool we have faced and solved some challenges as the following:


### Naming

When you try to run the standard LLVM linker to merge to arbitrary libraries, it might result on a `"Duplicate definition of symbol ..."`. Despite other limitations or analysis such as potential side effects, we see this as a naming issue. **The main reason is that we are merging artificially created libraries, which means that if a function is duplicated it will behave as the original one regarding the memory during runtime**. 

**We extended the LLVM linker to support the renaming of duplicated symbols.** During the new linking process, if a function was already in the library to merge, we check if the body of the function is not the same to the previous added duplicates, we rename it, and then we add it. In addition, it replaces each call to the original name function to the dispatcher.

### Orchestration

Once we added all the duplicated functions to the multivariant library we then need to ensure that they are not dead-code and that at some point all the duplicated functions (or variants) are executed. To ensure this, we take the original names for functions having variants. For each one replace its body with a `random dispatcher`. The random dispatcher is a simple function variant discriminator that looks like the following code:

```llvm
define internal i32 @original_name_function(i32 %0) {
    entry:
        %1 = call i32 @discriminate(i32 3)
        switch i32 %1, label %end [
        i32 0, label %original_name_function_43_
        i32 1, label %original_name_function_44_
        ]

    original_name_function_43_:                ; preds = %entry
        %2 = call i32 @original_name_function_43_(i32 %0)
        ret i32 %2

    original_name_function_44_:                ; preds = %entry
        %3 = call i32 @original_name_function_44_(i32 %0)
        ret i32 %3

    end:                                              ; preds = %entry
        %4 = call i32 @original_name_function_original(i32 %0)
        ret i32 %4
}
```

We create a big switch case for which at runtime a variant is executed. Now every time a function with variants is called, a random one is executed.

**Note**: The dispatchers are built as switch cases for sake of more execution time diversification and trying to avoid speculative execution. Our linker can be set to build table function calls instead.

## Build the mixer

To build the mixer you need the LLVM libraries, once in the root of the `multivariant-mixer` run the following.

`bash build_deps.sh`

After all the LLVM dependencies are installed, run

`bash build.sh`

If this command successfully finish, you will have a binary inside the `multivariant-mixer/build/mewe-linker`. If you want to prevent the build of this tool, you can take a look to the release section for a compilation that suits you. 

## Usage if the mixer

```bash
build/mewe-linker "original.bc" "allinone.multivariant.bc" -complete-replace=false -merge-function-switch-cases --replace-all-calls-by-the-discriminator -mewe-merge-debug-level=1 -mewe-merge-skip-on-error  -mewe-merge-bitcodes="llvm1.bc,llvm2.bc,llvm3.bc"

```

To see the full list of options, just run `mewe-linker --help`