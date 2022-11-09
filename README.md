# MEWE

MEWE is a toolset and methodology tailored to provide multivariant execution.


```bibtex
@inproceedings{10.1145/3560828.3564007,
  author = {Cabrera Arteaga, Javier and Laperdrix, Pierre and Monperrus, Martin and Baudry, Benoit},
  title = {Multi-Variant Execution at the Edge},
  year = {2022},
  isbn = {9781450398787},
  publisher = {Association for Computing Machinery},
  address = {New York, NY, USA},
  url = {https://doi.org/10.1145/3560828.3564007},
  doi = {10.1145/3560828.3564007},
  abstract = {Edge-Cloud computing offloads parts of the computations that traditionally occurs in the cloud to edge nodes. The binary format WebAssembly is increasingly used to distribute and deploy services on such platforms. Edge-Cloud computing providers let their clients deploy stateless services in the form of WebAssembly binaries, which are then translated to machine code, sandboxed and executed at the edge. In this context, we propose a technique that (i) automatically diversifies WebAssembly binaries that are deployed to the edge and (ii) randomizes execution paths at runtime. Thus, an attacker cannot exploit all edge nodes with the same payload. Given a service, we automatically synthesize functionally equivalent variants for the functions providing the service. All the variants are then wrapped into a single multivariant WebAssembly binary. When the service endpoint is executed, every time a function is invoked, one of its variants is randomly selected. We implement this technique in the MEWE tool and we validate it with 7 services for which MEWE generates multivariant binaries that embed hundreds of function variants. We execute the multivariant binaries on the world-wide edge platform provided by Fastly, as part as a research collaboration. We show that multivariant binaries exhibit a real diversity of execution traces across the whole edge platform distributed around the globe.},
  booktitle = {Proceedings of the 9th ACM Workshop on Moving Target Defense},
  pages = {11–22},
  numpages = {12},
  keywords = {moving target defense, multivariant execution, edge-cloud computing, webassembly, diversification},
  location = {Los Angeles, CA, USA},
  series = {MTD'22}
}

  


```

## Requirements

MEWE supports rust based projects for now and uses the LLVM toolchain to generate the multivariant binaries. Here you can find the whole list of dependencies you should install in your local pc.

- docker
- LLVM toolchain, version 12 or 13
- cargo and rust compiler

## Try it out

The following example generates a multivariant binary that can execute in your local machine. Make sure you have the LLVM toolchain in your system version 12.

```bash
git clone https://github.com/Jacarte/MEWE
cd MEWE
source mewe.sh
cd examples/simple
mewerustc  --llvm-version 12 --generation-timeout 3600 --exploration-timeout 120
```

Look for examples [here](examples)

# Extended linker and multivariant generation

Our [linker](multivariant-mixer) takes a collection of LLVM libraries as input and outputs a big library containing semantically equivalent functions (yet statically different) for which we orchestrate their execution at runtime.

 
# MEWE multivariants

With our linker, you can start creating multivariant libraries. To do so, you need to be able of creating semantically equivalent functions out of the original library. A previous [work of us](https://github.com/KTH/slumps/tree/master/crow) uses a superoptimizer to create a handful number of variants out of a single LLVM bitcode. We provide an [example](examples/calling_crow) about how to use CROW to generate variants.

Notice that, this approach will work with any diversifier, as soon as it fits with our linker in terms of binary correctness. 

# MEWE pipeline

MEWE uses an extended LLVM linker and CROW to build multivariant binaries. In the following diagram, we dissect how it works. 

MEWE first compiles the cargo based project collecting their intermediate LLVM bitcodes. The collected bitcodes are linked together to build a cumulative LLVM bitcode containing the full cargo application. MEWE then makes a CROW-pass to generate the program variants. 
The variants are passed to our linker to generate the multivarint LLVM bitcode.
MEWE fixes the generated LLVM bitcode depending on the compilation target. 
For example, for was32-wasi target, MEWE, tampers the entrypoint of the multivariant LLVM bitcode and creates a new cargo project that calls this new function. The final stage, is the regular compiler, which understands the missing dependencies and creates the final valid binary.

![diagram](docs/diagram3.png)

# License

This project is licensed under the MIT license. See [LICENSE](LICENSE.md) for more details.
