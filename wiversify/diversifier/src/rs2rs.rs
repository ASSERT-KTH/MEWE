
extern crate proc_macro;
use proc_macro::*;
use std::{borrow::Borrow, fs, str::Split};
use std::string::String;
use syn::{Expr, ExprCall, ExprLit, Field, Lit, LitInt, LitStr, Token, Type, parenthesized, punctuated::Punctuated, token};
use syn::parse::*;
use fs::*;
use regex::Regex;
use quote::quote;


#[derive(Debug)]
pub struct ArgumentsExpand {
	pub expr: String,
	pub from: i32,
	pub to: i32,
}

struct SyntaxArgumentsExpand {
	expr: LitStr,
	_comma: Token![,],
	from: LitInt,
	_comma2: Token![,],
	to: LitInt
}

/// Creates a match pattern for the given arguments
impl Parse for ArgumentsExpand {
	// Validate and parse the arguments of the macro
	fn parse(stream: ParseStream) -> Result<Self>{

		//eprintln!("{:}", stream.clone());
		if stream.is_empty() {
            panic!("Write full function signature.");
		}
		let syntax = SyntaxArgumentsExpand {
			expr: stream.parse().unwrap(),
			_comma: stream.parse().unwrap(),
			from: stream.parse().unwrap(),
			_comma2: stream.parse().unwrap(),
			to: stream.parse().unwrap(),
		};

		return Ok(
			ArgumentsExpand{
				expr: syntax.expr.value(),
				from: syntax.from.base10_parse().expect("Should be an integer"),
				to: syntax.to.base10_parse().expect("Should be and integer")
			}
		)
	}
}
#[derive(Debug)]
pub struct ArgumentsDynamicDiversification {
	pub exprs: Vec<String>,
	pub return_ty: String,
	pub as_function: String,
}

#[derive(Debug)]
pub struct ArgumentsDynamicDiversificationBody {
	pub exprs: Vec<String>
}


struct SyntaxDynamicDiversificationBody {
	exprs: Punctuated<Expr, Token![,]>
}


/// Creates a match pattern for the given arguments
impl Parse for ArgumentsDynamicDiversificationBody {
	// Validate and parse the arguments of the macro
	fn parse(stream: ParseStream) -> Result<Self>{

		//eprintln!("{:}", stream.clone());
		if stream.is_empty() {
            panic!("Write full function signature.");
		}
		let syntax = SyntaxDynamicDiversificationBody {
			exprs: stream.parse_terminated(Expr::parse).unwrap()

		};

		return Ok(
			ArgumentsDynamicDiversificationBody{
				exprs: syntax.exprs.iter()
				.enumerate()
				.map(|(i, e)| format!("{}", return_str_expr_from(e)))
				.collect::<Vec<_>>(),
			}
		)
	}
}

struct SyntaxDynamicDiversification {
	_paren_token: token::Paren,
	calls: Punctuated<Expr, Token![,]>,
	_rarrow_token: Token![->], 
	return_t: Type,
	_comma: Token![,],
	as_function: LitStr,
}


/*

(x: i32, y: i32, z: i32) -> i32, 
("a1", "a2", "a3"),
"a"
*/
struct SyntaxMultipleImport {
	_paren_token: token::Paren,
	args_types: Punctuated<Field, Token![,]>,
	_rarrow_token: Token![->], 
	return_t: Type,
	_comma: Token![,],
	_paren_token2: token::Paren,
	names: Punctuated<Expr, Token![,]>}


#[derive(Debug)]
pub struct ArgumentsMultipleImport {
	pub arg_tpes: Vec<String>,
	pub return_ty: String,
	pub function_names: Vec<String>}



/// Creates a match pattern for the given arguments
impl Parse for ArgumentsMultipleImport {
	// Validate and parse the arguments of the macro
	fn parse(stream: ParseStream) -> Result<Self>{

		eprintln!("{:}", stream.clone());
		if stream.is_empty() {
            panic!("Write full function signature.");
		}
		let args_types;
		let names;
		let syntax = SyntaxMultipleImport {
			_paren_token: parenthesized!(args_types in stream),
			args_types: args_types.parse_terminated(Field::parse_named).unwrap(),
			_rarrow_token: stream.parse().unwrap(),
			return_t: stream.parse().expect("Fail to parse return type"),
			_comma: stream.parse().unwrap(),
			_paren_token2: parenthesized!(names in stream),
			names: names.parse_terminated(Expr::parse).unwrap(),
		};
		

		let r = syntax.return_t;
		let return_token = quote!{#r};

		return Ok(
			ArgumentsMultipleImport{
				function_names: syntax.names.iter()
				.enumerate()
				.map(|(i, e)| format!("{}", return_str_expr_from(e)))
				.collect::<Vec<_>>(),
				arg_tpes: syntax.args_types.iter()
				.enumerate()
				.map(|(i, e)| format!("{}", return_str_from_field(e)))
				.collect::<Vec<_>>(),
				return_ty : return_token.to_string()
			}
		)
	}
}




#[derive(Debug)]
pub struct ArgumentsStaticDiversification {
	pub exprs: Vec<String>
}


#[derive(Debug)]
pub struct StaticArgumentsMetadata {

}



struct SyntaxArgumentsMetadata {

}
/// Creates a match pattern for the given arguments
impl Parse for StaticArgumentsMetadata {
	// Validate and parse the arguments of the macro
	fn parse(stream: ParseStream) -> Result<Self>{

        let syntax = SyntaxArgumentsMetadata {

		};

		// TODO validate the same type for all arguments

		return Ok(
			StaticArgumentsMetadata{
				
			}
		)
	}
}


struct SyntaxStaticDiversification {
	calls: Punctuated<Expr, Token![,]>,
}


/// Creates a match pattern for the given arguments
impl Parse for ArgumentsStaticDiversification {
	// Validate and parse the arguments of the macro
	fn parse(stream: ParseStream) -> Result<Self>{

		eprintln!("{:}", stream.clone());
		if stream.is_empty() {
            panic!("Write full function signature.");
		}
		
        let syntax = SyntaxStaticDiversification {
			calls: stream.parse_terminated(Expr::parse).unwrap(),
		};

		// TODO validate the same type for all arguments

		return Ok(
			ArgumentsStaticDiversification{
				exprs: syntax.calls.iter()
				.enumerate()
				.map(|(i, e)| format!("{}", return_str_expr_from(e)))
				.collect::<Vec<_>>()
			}
		)
	}
}


fn return_str_expr_from(expr: &Expr) -> String{
	let tokens = quote!{#expr};
	
	tokens.to_string()
}

fn return_str_from_field(expr: &Field) -> String{
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
			return_t: stream.parse().expect("Fail to parse return type"),
			_comma: stream.parse().unwrap(),
			as_function: stream.parse().expect("Provide the name of the new function")
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
				return_ty : return_token.to_string(),
				as_function: syntax.as_function.value()
			}
		)
	}
}