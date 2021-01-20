
#![feature(asm)]
//#![feature(naked_functions)]
#![feature(global_asm)]

extern crate wat2mir_macro;
use wat2mir_macro::{inject_mir_as_wasm, inject_mir_from_wasm, static_diversification};

inject_mir_as_wasm!("tests/resources/babbage_main.wat", // relative to Cargo.toml
"babbage1");

inject_mir_from_wasm!("tests/resources/babbage.wasm", // relative to Cargo.toml
"__original_main", "babbage2", 5, 12);

fn main() {
	unsafe{
		static_diversification!(babbage1 babbage2)();
	}
}

