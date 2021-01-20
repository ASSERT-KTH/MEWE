

extern crate proc_macro;
use proc_macro::*;
use wat2mir::{dto::Wat2MirConfig, translate2mir};
use std::{fs, str::Split};
use std::string::String;
use syn::*;
use syn::parse::*;
use fs::*;
use regex::Regex;



#[derive(Debug)]
struct ArgumentsMir4Wasm {
    file: String,
    function_name: String
}

#[derive(Debug)]
struct ArgumentsMirFromWasm {
    file: String,
    function_name: String,
    as_function: String,
    skip: u32,
    leave: u32
}


struct SyntaxMirFromWasm {
    name: LitStr,
    sep1: Token![,],
    function_name: LitStr,
    sep4: Token![,],
    as_function: LitStr,
    sep2: Token![,],
    skip: LitInt,
    sep3: Token![,],
    leave: LitInt
}

struct SyntaxMir4Wasm {
    name: LitStr,
    sep1: Token![,],
    function_name: LitStr
}

impl Parse for ArgumentsMir4Wasm {
    // Validate and parse the arguments of the macro
    fn parse(stream: ParseStream) -> Result<Self>{

        if stream.is_empty() {
            panic!("You should provide the correct arguments. wat_file, function_name, skip instructions in body, take instructions in body")
        }

        let syntax = SyntaxMir4Wasm {
            name: stream.parse().unwrap(),
            sep1: stream.parse().unwrap(),
            function_name: stream.parse().unwrap()
        };

        let meta = match fs::metadata(syntax.name.value())  {
            Err(_) => panic!("File {} does not exist", syntax.name.value()),
            Ok(m)  => m
        };

        if ! meta.is_file() {
            panic!("File {} is not a valid file.", syntax.name.value())
        }
        // Validate the existance of the file

        return Ok(
            ArgumentsMir4Wasm{
                file: syntax.name.value(),
                function_name: syntax.function_name.value().replace("$", "\\$")
            }
        )
    }
}


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



impl Parse for ArgumentsMirFromWasm {
    // Validate and parse the arguments of the macro
    fn parse(stream: ParseStream) -> Result<Self>{

        if stream.is_empty() {
            panic!("You should provide the correct arguments. wat_file, function_name, skip instructions in body, take instructions in body")
        }

        let syntax = SyntaxMirFromWasm {
            name: stream.parse().unwrap(),
            sep1: stream.parse().unwrap(),
            function_name: stream.parse().unwrap(),
            sep4: stream.parse().unwrap(),
            as_function: stream.parse().unwrap(),
            sep2: stream.parse().unwrap(),
            skip: stream.parse().unwrap(),
            sep3: stream.parse().unwrap(),
            leave: stream.parse().unwrap()
        };

        let meta = match fs::metadata(syntax.name.value())  {
            Err(_) => panic!("File {} does not exist", syntax.name.value()),
            Ok(m)  => m
        };

        if ! meta.is_file() {
            panic!("File {} is not a valid file.", syntax.name.value())
        }
        // Validate the existance of the file

        return Ok(
            ArgumentsMirFromWasm{
                file: syntax.name.value(),
                function_name: syntax.function_name.value(),
                as_function: syntax.as_function.value(),
                skip: syntax.skip.base10_parse().expect("The skip parameter (3rd) is not a valid base 10 number"),
                leave: syntax.leave.base10_parse().expect("The leave parameter (4rd) is not a valid base 10 number"),
            }
        )
    }
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
