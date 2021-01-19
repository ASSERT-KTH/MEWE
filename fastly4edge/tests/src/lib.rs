use std::{fs::read_to_string, path::PathBuf};
use wat2mir::{translate2mir, dto::Wat2MirConfig};

#[test]
fn test_translation1() {

	let mut d2 = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
	d2.push("resources/body1.wat");
	
    let mut d = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
	d.push("resources/babbage.wasm");

	let (head, body, _) = translate2mir(d.into_os_string().to_str().expect("Not valid str"), 
	"printf_core", "babbage", Wat2MirConfig{
		convert_end_to_mir: false, .. Wat2MirConfig::new()
	});

 
	let lines1 = body.split("\n");
	let lines2 = read_to_string(d2).expect("msg");

	lines1.zip(lines2.split("\n")).for_each(|(l1, l2)|{
		assert_eq!(l1, l2)
	});

}


#[test]
fn test_translation_with_skip() {

    let mut d = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
	d.push("resources/babbage.wasm");

	let (head, body, tail) = translate2mir(d.into_os_string().to_str().expect("Not valid str"), 
	"__original_main", "babbage", Wat2MirConfig{
		convert_end_to_mir: true,  skip: 5, leave: 11
	});


	println!("{}{}{}", head, body, tail)
}


#[test]
fn test_translation_with_head_parameters() {

    let mut d = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
	d.push("resources/babbage.wasm");

	let (head, _, _) = translate2mir(d.into_os_string().to_str().expect("Not valid str"), 
	"printf_core", "babbage", Wat2MirConfig{
		convert_end_to_mir: true, skip: 5, leave: 11
	});


	println!("{}", head)
}