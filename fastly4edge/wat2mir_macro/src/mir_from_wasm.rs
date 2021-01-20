

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
pub struct ArgumentsMirFromWasm {
    pub file: String,
    pub function_name: String,
    pub as_function: String,
    pub skip: u32,
    pub leave: u32
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
