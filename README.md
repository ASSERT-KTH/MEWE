## Fastly4Edge

### customWasm

This repo first contains a research experiment for edge computing using the Fastly's Compute@Edge service. The code in the `customWasm` folder is an example of running custom Wasm binaries as a Fastly service. Go to [this post](https://www.jacarte.net/blog/2021/HandMadeWasmDeploInFastly/) to read more about how this example works.

### Prerequisites

- [fastly compute CLI tool](https://developer.fastly.com/learning/compute/)
- [Rust nightly](https://www.oreilly.com/library/view/rust-programming-by/9781788390637/e07dc768-de29-482e-804b-0274b4bef418.xhtml)
- A Fastly Compute@Edge account

## How to build and deploy the service 

Run `bash deploy.sh <service_id>`

### wiversify

The `wiversify` folder contains the procedural macros that we implemented in order to provide static and dynamic diversity in Rust code at compilation time. Besides, it contains the needed code to translate Wasm binary functions to LLVM MIR syntax. The folder contains the following packages

- [diversifier](/diversifier): Implementation for the diversification procedural macros
- [t2wasm](/t2wasm): Working example of the diversifier macros and the injection of Wasm functions at compilation time
- [wat2mir](/wat2mir): Translation from Wasm binary to LLVM MIR format.
- [wat2mir_macro](/wat2mir_macro): Procedural macros for the compiling time injection of LLVM MIR code extracted from a Wasm binary.