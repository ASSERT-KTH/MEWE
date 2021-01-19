

extern crate proc_macro;
use proc_macro::*;
use std::{fs, str::Split};
use std::string::String;
use syn::*;
use syn::parse::*;
use fs::*;
use regex::Regex;



#[derive(Debug)]
struct Arguments {
    file: String,
    function_name: String,
    skip: i32,
    take: i32
}

struct Syntax {
    name: LitStr,
    sep1: Token![,],
    function_name: LitStr,
    sep2: Token![,],
    skip: LitInt,
    sep3: Token![,],
    take: LitInt
}
impl Parse for Arguments {
    // Validate and parse the arguments of the macro
    fn parse(stream: ParseStream) -> Result<Self>{

        if stream.is_empty() {
            panic!("You should provide the correct arguments. wat_file, function_name, skip instructions in body, take instructions in body")
        }

        let syntax = Syntax {
            name: stream.parse().unwrap(),
            sep1: stream.parse().unwrap(),
            function_name: stream.parse().unwrap(),
            sep2: stream.parse().unwrap(),
            skip: stream.parse().unwrap(),            
            sep3: stream.parse().unwrap(),       
            take: stream.parse().unwrap(),
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
            Arguments{
                file: syntax.name.value(),
                function_name: syntax.function_name.value().replace("$", "\\$"), // Escape to be able to use in regex
                skip: syntax.skip.base10_parse()?,
                take: syntax.take.base10_parse()?
            }
        )
    }
}


#[proc_macro]
pub fn inject_mir4wasm(_item: TokenStream) -> TokenStream {
    // validate macro arguments
    // expecting wat_file, function_name, skip instructions in body, take instructions in body
    let arguments = parse_macro_input!(_item as Arguments);

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


/*
macro_rules! wat2mir {
    
}*/

/*

TODO

- Load wat file
- Remove comments
- Find function by name
- Genereate function header
- Replace end by LLVM MIR end functions
- Generate the external export functions

TODO

Add a folder instead with all variants
- Generate huge switch case

*/