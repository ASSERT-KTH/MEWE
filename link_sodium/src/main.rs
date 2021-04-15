// NAME of the module to insert
//mod bin2base64;
//mod rotl32;
mod utils;

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
//use bin2base64::*;
//use rotl32::*;
use utils::*;

const BACKEND_NAME: &str = "backend_name";

/// The name of a second backend associated with this service.
const OTHER_BACKEND_NAME: &str = "other_backend_name";

lazy_static! {
    static ref STACKTRACE: Mutex<Vec<String>> = Mutex::new(vec![]);
}

#[warn(non_snake_case)]
#[no_mangle]
pub fn _cb71P5H47J3A(id: i32) {
    // Save in global path header
    STACKTRACE.lock().unwrap().push(format!("{}",id));
}

/// The entry point for your application.
///
/// This function is triggered when your service receives a client request. It could be used to
/// route based on the request properties (such as method or path), send the request to a backend,
/// make completely new requests, and/or generate synthetic responses.
///
/// If `main` returns an error, a 500 error response will be delivered to the client.
#[fastly::main]
fn main(mut req: Request<Body>) -> Result<impl ResponseExt, Error> {
   
    let mut hasher = DefaultHasher::new();

	let pop = match std::env::var("FASTLY_POP") {
		Ok(val) => val,
		Err(_) => "NO_POP".to_string()
	};

    // PoP discriminator
    pop.hash(&mut hasher);
    let hashValue = hasher.finish();
	
    // ENTRY POINT FOR MULTIVERSION FUNCTIONS
    // ==============================================
    // bin2base64
    // let (result, lapsed, DIS) = main_bin2base64(hashValue);
    // sodium_increment
    // let (result, lapsed, DIS) = main_rotl32(hashValue);
    let (result, lapsed, DIS) = main_sodium_increment(hashValue);
    // ==============================================


    // get path and send thourgh header
    let path = STACKTRACE.lock().unwrap().join(",");

    // Pattern match on the request method and path.
    match (req.method(), req.uri().path()) {
        // If request is a `GET` to the `/` path, send a default response.
        (&Method::GET, "/") => Ok(Response::builder()
            .status(StatusCode::OK)
            .header("XPop", format!("{}", pop))
            .header("XPopHash", format!("{}", hashValue))
            .header("Xdis", format!("{}", DIS))
            .header("Xtime", format!("{}", lapsed))
            .header("Xpath", format!("{}", path))
            .body(Body::from(format!("POP: {} {:?} Result {:?} ", pop, DIS, result
            )))?),
      
        // Catch all other requests and return a 404.
        _ => Ok(Response::builder()
            .status(StatusCode::NOT_FOUND)
            .body(Body::from("The page you requested could not be found"))?),
    }
}


