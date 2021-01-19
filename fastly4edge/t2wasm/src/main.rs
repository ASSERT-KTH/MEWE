
#![feature(asm)]
//#![feature(naked_functions)]
#![feature(global_asm)]

extern crate wat2mir_macro;
use wat2mir_macro::inject_mir4wasm;

inject_mir4wasm!("tests/resources/babbage_main.wat", // relative to Cargo.toml
"babbage1", 3, 20);

fn main() {
	unsafe{
		babbage1();
	}
}

