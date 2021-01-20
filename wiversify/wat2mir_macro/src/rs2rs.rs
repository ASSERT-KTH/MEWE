
extern crate proc_macro;
use proc_macro::*;
use std::{fs, str::Split};
use std::string::String;
use syn::{Expr, ExprCall, Token, parenthesized, punctuated::Punctuated, Type, token};
use syn::parse::*;
use fs::*;
use regex::Regex;
use quote::quote;



#[derive(Debug)]
pub struct ArgumentsDynamicDiversification {
	pub exprs: Vec<String>,
	pub return_ty: String
}


struct SyntaxDynamicDiversification {
	_paren_token: token::Paren,
	calls: Punctuated<Expr, Token![,]>,
	_rarrow_token: Token![->], 
	return_t: Type,
}


fn return_str_expr_from(expr: &Expr) -> String{
	let tokens = quote!{#expr};
	
	tokens.to_string()
}

/// Creates a match pattern for the given arguments
impl Parse for ArgumentsDynamicDiversification {
	// Validate and parse the arguments of the macro
	fn parse(stream: ParseStream) -> Result<Self>{

		eprintln!("{:}", stream.clone());
		if stream.is_empty() {
            panic!("Write full function signature.");
		}
		
		let calls;
        let syntax = SyntaxDynamicDiversification {
			_paren_token: parenthesized!(calls in stream),
			calls: calls.parse_terminated(Expr::parse).unwrap(),
			_rarrow_token: stream.parse().unwrap(),
			return_t: stream.parse().expect("Fail to parse return type")
		};
		
		let r = syntax.return_t;
		let return_token = quote!{#r};

		// TODO validate the same type for all arguments

		return Ok(
			ArgumentsDynamicDiversification{
				exprs: syntax.calls.iter()
				.enumerate()
				.map(|(i, e)| format!("{} => {},", i, return_str_expr_from(e)))
				.collect::<Vec<_>>(),
				return_ty : return_token.to_string()
			}
		)
	}
}