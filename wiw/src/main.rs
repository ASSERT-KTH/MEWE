//! Default Compute@Edge template program.
#![feature(asm)]
//#![feature(naked_functions)]
#![feature(global_asm)]
use std::time::{Duration, Instant};
use fastly::http::{HeaderValue, Method, StatusCode};
use fastly::request::CacheOverride;
use fastly::{Body, Error, Request, RequestExt, Response, ResponseExt};


extern {
	fn templ() -> i32;
}

#[fastly::main]
fn main(mut req: Request<Body>) -> Result<impl ResponseExt, Error> {
    
	Ok(Response::builder()
            .status(StatusCode::OK)
            .body(Body::from(format!("POP: {} Result {:?}", 1, unsafe{templ()}
                )))?)
}


