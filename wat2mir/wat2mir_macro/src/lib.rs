

extern crate proc_macro;
use proc_macro::*;
use std::fs;
use std::string::String;
use syn::*;
use syn::parse::*;

use quote::*;

type WAT_FILE = Literal;
type FUNCTION_NAME = Literal;
type SKIP = Literal;
type TAKE = Literal;

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



        return Ok(
            Arguments{
                file: syntax.name.value(),
                function_name: syntax.function_name,
                skip: syntax.skip,
                take: syntax.take
            }
        )
    }
}

#[proc_macro]
pub fn make_answer(_item: TokenStream) -> TokenStream {
    // validate macro arguments
    // expecting wat_file, function_name, skip instructions in body, take instructions in body
    let arguments = parse_macro_input!(_item as Arguments);
    let a  = format!("{:?}", arguments.file);

    format!(r#"
    fn answer() -> u32 {{ 
        {:?};
        42 
    }}
    "#, a).parse().unwrap()
}

fn load_wat_file(wat_file: String) -> String{
    match fs::read_to_string(wat_file) {
        Err(e) => panic!(e), 
        Ok(x) => x // TODO parse and transform here
    }
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