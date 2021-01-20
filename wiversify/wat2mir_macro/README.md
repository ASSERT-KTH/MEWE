## Procedural macros for diversification

> Procedural macros allow you to run code at compile time that operates over Rust syntax, both consuming and producing Rust syntax. You can sort of think of procedural macros as functions from an AST to another AST.

This package contains two procedural macros in order to inject Wasm assembly code in the Rust package at compilation time. 

- [`inject_mir_as_wasm`](https://github.com/Jacarte/fastly4edge/blob/5ce6e88894158d573d2c17766ce0ba1680f7aa80/wiversify/wat2mir_macro/src/lib.rs#L19): Inject Wasm assemnbly instructions as function during compilation. How to use it:

	```rs
	inject_mir_as_wasm!("<mir_wat_file>", // relative to Cargo.toml
	"<inject_as_function_name>");

	inject_mir_as_wasm!("tests/resources/babbage_main.wat", 
	"babbage1");
	```


- [`inject_mir_from_wasm`](https://github.com/Jacarte/fastly4edge/blob/5ce6e88894158d573d2c17766ce0ba1680f7aa80/wiversify/wat2mir_macro/src/lib.rs#L44): This macro is a little bit different from the first one. It receives a valid Wasm binary to extract the function from it. To do so, we use `walrus`, a crate able to parse, transform and emit Wasm code. We extract the function using its name, notice that the provided Wasm needs to have the `name` custom section to be valid to us. Then, the body and the declaration of the function is translated to the MIR LLVM syntax. How to use it


	```rs
	inject_mir_from_wasm!("tests/resources/babbage.wasm", // relative to Cargo.toml
	"__original_main", "babbage2", 5, 12);
	```

	The macro receives 4 parameters, the Wasm binary address, the function to look for, the function name in the Rust package, how many lines to skip in the body of the function and how many lines to skip from the tail. 