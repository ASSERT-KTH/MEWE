use std::{fs::read_to_string, path::PathBuf};

use wat2mir::{translate2mir, dto::Wat2MirConfig};

#[test]
fn testCFG() {

	let mut d2 = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
	d2.push("resources/body1.wat");
	
    let mut d = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
	d.push("resources/babbage.wasm");

	let (head, body, _) = translate2mir(d.into_os_string().to_str().expect("Not valid str"), "printf_core", "babbage", Wat2MirConfig{
		convert_end_to_mir: false
	});

 
	let lines1 = body.split("\n");
	let lines2 = read_to_string(d2).expect("msg");

	lines1.zip(lines2.split("\n")).for_each(|(l1, l2)|{
		println!("{:?} {:?}", l1, l2);
		assert_eq!(l1, l2)
	});

}
