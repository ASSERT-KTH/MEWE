# MEWE

# Repository structure
 - `multivariant-mixer`: The MEWE mulrivariant library generator.
 - `link_sodium`, `link_qrcode`: MEWE pipelines. 
 - `experiments`: scripts for experiments reproduction


## Extended linker or "mixer"
[![mewe linker](https://github.com/Jacarte/MEWE/actions/workflows/build_linker.yaml/badge.svg?branch=main)](https://github.com/Jacarte/MEWE/actions/workflows/build_linker.yaml)

**multivariant-mixer**

We merge several libraries into a big one, we call it a multivariant l ibrary. It is a big library containing semantically equivalent functions (yet statically different) for which we orchestrate their execution at runtime. `mixer` creates LLVM multivariant libraries out of a collection of LLVM libraries as input.

Read more about it [here](multivariant-mixer).
 
### MEWE multivariants at the Edge:

Once with the mixer, you can start creating multivariant libraries. To do so, you need to be able of creating semantically equivalent functions out of the original library. A previous [work of us](https://github.com/KTH/slumps/tree/master/crow), uses a superoptimizer to create a handful number of variants out of a single LLVM bitcode. We would like to remark that this approach will work with any diversifier, as soon as it ensures that our merging strategy is correct. 

We created a proof of concept of deploying multivariants at the Edge. Specifically at the Fastly platform. We create multivariant libraries for `libsodium` and a `qrcode_generator`. We then passed these multivariant binaries to the `rustc` compiler to generate a valid executable Wasm binary (according to the Fastly ABI).

The process to do this experiment can be appreiciated in the pipeline folders, `link_sodium` and `link_qrcode`.

1 - Each pipeline folder contains the corresponding bash script to collect intermediate bitcodes from rustc (e.g. ./rust/build.py). 

2 - The collected intermediate bitcodes need to be sent to CROW for diversification. After collecting the diversified modules, run the script 
`build_multivariant.sh <original bitcode> <mewe-linker binary folder> <diversified bitcodes folder> `. 

3 - The final step is to run the examples. Inside the folder `rust/example`, run the script `build.sh` and collect the Wasm binary.
