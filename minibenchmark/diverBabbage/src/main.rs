//! Default Compute@Edge template program.
#![feature(asm)]
//#![feature(naked_functions)]
#![feature(global_asm)]
use std::time::{Duration, Instant};
use fastly::http::{HeaderValue, Method, StatusCode};
use fastly::request::CacheOverride;
use fastly::{Body, Error, Request, RequestExt, Response, ResponseExt};

use rand::RngCore;
//use rand::RngCore;
use wat2mir_macro::{inject_mir_as_wasm, inject_mir_from_wasm};
use diversifier::{static_diversification,dynamic_diversification_body,  dynamic_diversification};

//inject_mir_from_wasm!("resources/v1.wasm", // relative to Cargo.toml
//"__original_main", "babbage1", 0, 0);

//inject_mir_from_wasm!("resources/v2.wasm", // relative to Cargo.toml
//"__original_main", "v2", 5, 12);

//inject_mir_from_wasm!("resources/v3.wasm", // relative to Cargo.toml
//"__original_main", "v3", 5, 11);

//inject_mir_from_wasm!("resources/v4.wasm", // relative to Cargo.toml
//"__original_main", "v4", 6, 12);


inject_mir_as_wasm!("resources/v1.wasm.wat", // relative to Cargo.toml
"babbage1");

inject_mir_as_wasm!("resources/v2.wasm.wat", // relative to Cargo.toml
"babbage2");

inject_mir_as_wasm!("resources/v3.wasm.wat", // relative to Cargo.toml
"babbage3");

inject_mir_as_wasm!("resources/v4.wasm.wat", // relative to Cargo.toml
"babbage4");

dynamic_diversification!((
	unsafe{babbage1()},
	unsafe{babbage2()},
	unsafe{babbage3()},
	unsafe{babbage4()}) -> i32, "babbage");

#[fastly::main]
fn main(mut req: Request<Body>) -> Result<impl ResponseExt, Error> {
    
	let pop = match std::env::var("FASTLY_POP") {
		Ok(val) => val,
		Err(_) => "NO_POP".to_string()
	};

	let DIS = rand::thread_rng().next_u32() % 4;
	let now = Instant::now();
	let ret = babbage(DIS).to_string();
	let lapse = now.elapsed().as_nanos();

	Ok(Response::builder()
            .status(StatusCode::OK)
            .body(Body::from(format!("POP: {} DIS {} Result {} TIME {}", pop, DIS,ret, lapse
                )))?)
}


