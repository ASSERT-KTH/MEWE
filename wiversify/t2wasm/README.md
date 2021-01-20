## Examples about how to use wiversifier proc-macros

Full code [here](https://github.com/Jacarte/fastly4edge/blob/main/wiversify/t2wasm/src/main.rs)

1. Inject two Wasm functions at compilation time

	```rs
	inject_mir_as_wasm!("tests/resources/babbage_main.wat", // relative to Cargo.toml
	"babbage1");

	inject_mir_from_wasm!("tests/resources/babbage.wasm", // relative to Cargo.toml
	"__original_main", "babbage2", 5, 12);

	```
2. Create a dynamic diversifier to use one of the injected functions

	```rs
	dynamic_diversification!((unsafe{babbage1()}, unsafe{babbage2()}) -> i32, "myfunction");
	```

3. Do your service

	```rs
	fn main() {
		unsafe{
			// Create a static diversification behavior
			static_diversification!(babbage1(), babbage2());
		};

		myfunction(rand::thread_rng().next_u32() % 2);
	}


	```