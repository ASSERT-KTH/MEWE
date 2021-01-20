extern crate proc_macro;

mod mir_as_wasm;
mod mir_from_wasm;
use mir_as_wasm::ArgumentsMir4Wasm;
use mir_from_wasm::ArgumentsMirFromWasm;
use proc_macro::*;
use wat2mir::{dto::Wat2MirConfig, translate2mir};
use std::{fs};
use syn::*;
use syn::parse::*;
use rand::{RngCore, seq::SliceRandom};




#[proc_macro]
pub fn inject_mir_as_wasm(_item: TokenStream) -> TokenStream {
    // validate macro arguments
    // expecting wat_file, function_name, skip instructions in body, take instructions in body
    let arguments = parse_macro_input!(_item as ArgumentsMir4Wasm);

    let content = fs::read_to_string(arguments.file).expect("Could not read the file!");
    
    format!(r##"
    #[no_mangle]
    #[cfg(target_arch = "wasm32")]
    global_asm!(
        r#"{}"#
    );

    extern {{
        fn {}() -> i32;
    }}

    "##, content, arguments.function_name ).parse().unwrap()
}




#[proc_macro]
pub fn inject_mir_from_wasm(_item: TokenStream) -> TokenStream {
    // validate macro arguments
    // expecting wat_file, function_name, skip instructions in body, take instructions in body
    let arguments = parse_macro_input!(_item as ArgumentsMirFromWasm);

	let (head, body, tail, fty) = translate2mir(&arguments.file, 
        &arguments.function_name, &arguments.as_function , Wat2MirConfig{
		convert_end_to_mir: true, skip: arguments.skip, leave: arguments.leave
	});
    eprintln!("Injected function\n{}", body);

    format!(r##"
    #[no_mangle]
    #[cfg(target_arch = "wasm32")]
    global_asm!(
        r#"
        {}
        {}
        {}
        "#
    );


    extern {{
        fn {}{};
    }}

    "##, head, body, tail, arguments.as_function, fty ).parse().unwrap()
}


#[proc_macro]
pub fn static_diversification(_item: TokenStream) -> TokenStream {
    // validate macro arguments
    //let arguments = parse_macro_input!(_item as ArgumentsStaticDiversification);

    let tokens = _item.clone().into_iter();
    let mut rand = rand::thread_rng().next_u32();

    let to_skip = rand % (tokens.count() as u32);


    eprintln!("Selected static branch {:?}",to_skip);

    _item.into_iter().skip(to_skip as usize) // random skip x elements
    .take(1).collect::<TokenStream>()
}


