// NAME of the module to insert
mod img;

#[macro_use]
extern crate lazy_static;
// IMPORT HERE
use img::*;
use rand::RngCore;
use std::sync::Mutex;
use std::collections::hash_map::{DefaultHasher, RandomState};
use std::hash::{Hash, Hasher};

#[warn(non_snake_case)]
#[no_mangle]
pub fn discriminate(total: i32) -> i32 {
    
    let popId = (rand::thread_rng().next_u32()%1000000u32) as i32;
    popId%total
}

/// The entry point for your application.
///
/// This function is triggered when your service receives a client request. It could be used to
/// route based on the request properties (such as method or path), send the request to a backend,
/// make completely new requests, and/or generate synthetic responses.
///
/// If `main` returns an error, a 500 error response will be delivered to the client.

use fastly::{Error, Request, Response};
use fastly::http::{StatusCode};
use std::time::{Duration, SystemTime};

/*
#[fastly::main]
fn main(_req: Request) -> Result<Response, Error> {


	let pop = match std::env::var("FASTLY_POP") {
		Ok(val) => val,
		Err(_) => "NO_POP".to_string()
	};
    let now = std::time::Instant::now();
    let img = unsafe { generate_fractal() };
    let lapsed = now.elapsed().as_nanos();

    let (buff, w, h) = img;
    let png = encode_img(buff, w, h);
    let res = Response::from_body(png)
    .with_header("Xtime", format!("{:?}", now.elapsed().as_nanos()))
    .with_header("Xpop", format!("{:?}", pop))
    .with_header("Content-Type", "image/png")
    //.with_header("XContent", img)
    .with_status(StatusCode::OK);
    Ok(res)
}
*/


#[fastly::main]
fn main(mut _req: Request) -> Result<Response, Error> {

    let new_req = _req.clone_with_body();
    let incoming = new_req.into_body_bytes();
    //let res = Response::from_body(incoming)
    //.with_header("Content-Type", "image/png")
    //.with_header("XContent", img)
    //.with_status(StatusCode::OK);

    
	let pop = match std::env::var("FASTLY_POP") {
		Ok(val) => val,
		Err(_) => "NO_POP".to_string()
	};
    let mut decoded = decode_img(incoming);
    let now = std::time::Instant::now();
    let fl = unsafe {flipv_image(decoded)};
    let encoded=encode_dynimg(fl);
    let lapsed=now.elapsed().as_nanos();
    let res = Response::from_body(encoded)
    .with_header("Xtime", format!("{:?}", lapsed))
    .with_header("Xpop", format!("{:?}", pop))
    .with_header("Content-Type", "image/png")
    //.with_header("XContent", img)
    .with_status(StatusCode::OK);
    Ok(res)
    //let lapsed = now.elapsed().as_nanos();
    
}

//ebeeeea1b8c6ceabd5a4f0c80c68ccf312267b3e4d5488442bea9df52f7d3f00cab6dbd45b7e5f884a4895000e94010441ea9070aed86b97f0fe087d19e5f353
//66aa39821189f2cce1ffdad44f3aa60dd276599505f920581350150eda5429d44687a2309d69975ddd6e67c423b91954d0ae3bdb33b19816041716b7c7ef2045


