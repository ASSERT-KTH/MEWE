use std::path::PathBuf;

use wat2mir::translate2mir;

#[test]
fn testCFG() {
    let mut d = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
	d.push("resources/babbage.wasm");

	let ret = translate2mir(d.into_os_string().to_str().expect("Not valid str"), "printf_core", "babbage");

    println!("{}", ret)
}
