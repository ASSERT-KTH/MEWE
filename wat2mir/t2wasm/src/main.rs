
#![feature(asm)]
//#![feature(naked_functions)]
#![feature(global_asm)]

extern crate wat2mir_macro;
use wat2mir_macro::make_answer;

make_answer!("tests/resources/babbage_main.wat", // relative to Cargo.toml
"babbage", 3, 20);

fn main() {
	unsafe{
		babbage();
	}
}

