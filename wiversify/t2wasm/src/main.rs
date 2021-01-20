
#![feature(asm)]
//#![feature(naked_functions)]
#![feature(global_asm)]

extern crate wat2mir_macro;
use wat2mir_macro::{inject_mir_as_wasm, inject_mir_from_wasm, static_diversification,dynamic_diversification_body,  dynamic_diversification};

inject_mir_as_wasm!("tests/resources/babbage_main.wat", // relative to Cargo.toml
"babbage1");

inject_mir_from_wasm!("tests/resources/babbage.wasm", // relative to Cargo.toml
"__original_main", "babbage2", 5, 12);

dynamic_diversification!((unsafe{babbage1()}, unsafe{babbage2()}, 1, 2) -> i32, "myfunction");

fn main() {
	unsafe{
		static_diversification!(babbage1 babbage2)();
	};

	let dis = 2;
	dynamic_diversification_body!((unsafe{babbage1()}, unsafe{babbage2()}, 1, 2) -> i32, "myfunction");

	myfunction(1);
}

