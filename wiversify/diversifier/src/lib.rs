extern crate proc_macro;
mod rs2rs;

use proc_macro::*;
use rs2rs::{ArgumentsDynamicDiversification, ArgumentsStaticDiversification, StaticArgumentsMetadata};
use std::{env, fs};
use syn::*;
use syn::parse::*;
use rand::{RngCore, seq::SliceRandom};
use quote::quote;



#[proc_macro]
pub fn static_diversification(_item: TokenStream) -> TokenStream {
    // validate macro arguments
    //let arguments = parse_macro_input!(_item as ArgumentsStaticDiversification);
    let arguments = parse_macro_input!(_item as ArgumentsStaticDiversification);

    let tokens = arguments.exprs.clone().into_iter();
    let rand = rand::thread_rng().next_u32();

    let to_skip = rand % (tokens.count() as u32);


    eprintln!("Selected static branch {:?}",to_skip);

    arguments.exprs.into_iter().skip(to_skip as usize) // random skip x elements
    .next().unwrap().parse().unwrap()
}


#[proc_macro]
pub fn static_version_metadata(_item: TokenStream) -> TokenStream {
    // validate macro arguments
    //let arguments = parse_macro_input!(_item as ArgumentsStaticDiversification);
    let arguments = parse_macro_input!(_item as StaticArgumentsMetadata);
    
	let version = match std::env::var("SERVICE_VERSION") {
		Ok(val) => val,
		Err(_) => panic!("SERVICE_VERSION environment variable not set")
	};

    eprintln!("Service version {:?}",version);

    version.parse().unwrap()
}

#[proc_macro]
pub fn dynamic_diversification(_item: TokenStream) -> TokenStream {
    // validate macro arguments
    let arguments = parse_macro_input!(_item as ArgumentsDynamicDiversification);

    let tokens = format!(r#"
        #[no_mangle]
        fn {}(dis: u32) -> {}{{
            match dis {{
                {}
                _ => panic!("Dont know what to do with the current discriminator value {{}}", dis)
            }}
        }}"#, arguments.as_function,  arguments.return_ty, arguments.exprs.join("\n"));
    
    tokens.parse().unwrap()
}



#[proc_macro]
pub fn dynamic_diversification_body(_item: TokenStream) -> TokenStream {
    // validate macro arguments
    let arguments = parse_macro_input!(_item as ArgumentsDynamicDiversification);

    let tokens = format!(r#"
            // {}
            match dis {{
                {}
                _ => panic!("Dont know what to do with the current discriminator value {{}}", dis)
            }}"#, arguments.as_function, arguments.exprs.join("\n"));
    
    tokens.parse().unwrap()
}
