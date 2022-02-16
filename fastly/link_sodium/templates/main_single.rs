#[macro_use]
extern crate lazy_static;

use fastly::http::{HeaderValue, Method, StatusCode};
use fastly::request::CacheOverride;
use fastly::{Body, Error, Request, RequestExt, Response, ResponseExt};
use rand::RngCore;
use std::sync::Mutex;
use std::collections::hash_map::{DefaultHasher, RandomState};
use std::hash::{Hash, Hasher};

// IMPORT HERE
<%usage%>

/// The entry point for your application.
///
/// This function is triggered when your service receives a client request. It could be used to
/// route based on the request properties (such as method or path), send the request to a backend,
/// make completely new requests, and/or generate synthetic responses.
///
/// If `main` returns an error, a 500 error response will be delivered to the client.
#[fastly::main]
fn main(mut req: Request<Body>) -> Result<impl ResponseExt, Error> {
   
    // ENTRY POINT FOR MULTIVERSION FUNCTIONS
    <%entry%>

    let mut hasher = DefaultHasher::new();

	
	let pop = match std::env::var("FASTLY_POP") {
		Ok(val) => val,
		Err(_) => "NO_POP".to_string()
	};

    // PoP discriminator
    pop.hash(&mut hasher);
    // get path and send thourgh header
    let hashValue = hasher.finish() as i32;
    // Pattern match on the request method and path.
    match (req.method(), req.uri().path()) {
        // If request is a `GET` to the `/` path, send a default response.
        (&Method::GET, "/") => Ok(Response::builder()
            .status(StatusCode::OK)
            .header("XPop", format!("{}", pop))
            .header("XPopHash", format!("{}", hashValue))
            //.header("Xdis", format!("{}", DIS))
            .header("Xtime", format!("{}", lapsed))
            //.header("Xpath", format!("{}", path))
            .body(Body::from(format!("POP: {} Result {:?} ", pop, result
            )))?),
      
        // Catch all other requests and return a 404.
        _ => Ok(Response::builder()
            .status(StatusCode::NOT_FOUND)
            .body(Body::from("The page you requested could not be found"))?),
    }
}

