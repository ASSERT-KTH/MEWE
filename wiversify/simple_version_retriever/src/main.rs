//! Default Compute@Edge template program.
#![feature(asm)]
//#![feature(naked_functions)]
#![feature(global_asm)]

use fastly::http::{HeaderValue, Method, StatusCode};
use fastly::request::CacheOverride;
use fastly::{Body, Error, Request, RequestExt, Response, ResponseExt};
use diversifier::{static_version_metadata};

/// The name of a backend server associated with this service.
///
/// This should be changed to match the name of your own backend. See the the `Hosts` section of
/// the Fastly WASM service UI for more information.
const BACKEND_NAME: &str = "hosts.secretcdn.net";

/// The name of a second backend associated with this service.
const OTHER_BACKEND_NAME: &str = "hosts.secretcdn.net";

/// The entry point for your application.
///
/// This function is triggered when your service receives a client request. It could be used to
/// route based on the request properties (such as method or path), send the request to a backend,
/// make completely new requests, and/or generate synthetic responses.
///
/// If `main` returns an error, a 500 error response will be delivered to the client.
#[fastly::main]
fn main(mut req: Request<Body>) -> Result<impl ResponseExt, Error> {
    
	let pop = match std::env::var("FASTLY_POP") {
		Ok(val) => val,
		Err(_) => "NO_POP".to_string()
    };
    
    let compile_time_version = static_version_metadata!();
    
    Ok(Response::builder()
            .status(StatusCode::OK)
            .body(Body::from(format!("POP: {}, Version: {}", pop,compile_time_version)))?)
}
