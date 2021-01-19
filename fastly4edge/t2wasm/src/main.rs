
#![feature(asm)]
//#![feature(naked_functions)]
#![feature(global_asm)]

extern crate wat2mir_macro;
use wat2mir_macro::make_answer;

make_answer!("/Users/javierca/Documents/Develop/fastly4edge/wat2mir/resources/babbage_main.wat", // relative to Cargo.toml
"babbage1", 3, 20);

fn main() {
	unsafe{
		babbage1();
	}
}

