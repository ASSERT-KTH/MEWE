

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
pub struct ArgumentsMir4Wasm {
    pub file: String,
    pub function_name: String
}

pub struct SyntaxMir4Wasm {
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
