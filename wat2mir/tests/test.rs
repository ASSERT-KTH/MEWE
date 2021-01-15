


extern crate wat2mir_macro;
use wat2mir_macro::make_answer;

make_answer!("are.wat", "template", 3, 20);

#[test]
fn works() {
	println!("{}", answer());
}

