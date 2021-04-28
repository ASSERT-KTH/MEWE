// NAME of the module to insert
mod bin2base64_r;
mod utils;
mod core_ed25519;
mod aead_chacha20poly1305;

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
use bin2base64_r::*;
use utils::*;
use core_ed25519::*;
use aead_chacha20poly1305::*;

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

#[warn(non_snake_case)]
#[no_mangle]
pub fn discriminate(total: i32) -> i32 {
   
    let mut hasher = DefaultHasher::new();

	
	let pop = match std::env::var("FASTLY_POP") {
		Ok(val) => val,
		Err(_) => "NO_POP".to_string()
	};

    // PoP discriminator
    pop.hash(&mut hasher);
    (hasher.finish() as i32)%total
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
   
    // ENTRY POINT FOR MULTIVERSION FUNCTIONS
    // ==============================================
    
    //let (result, lapsed) = main_bin2base64();

    // let (result, lapsed) = main_sodium_increment();
    //let (result, lapsed) = main_sodium_memcmp();
    // let (result, lapsed) = main_sodium_is_zero();
    // let (result, lapsed) = main_sodium_add();
    //let (result, lapsed) = main_sodium_free(); // It is getting erros probably due to free

    
    //let (result, lapsed) = main_crypto_core_ed25519_scalar_invert();
    // let (result, lapsed) = main_crypto_core_ed25519_scalar_complement();
    // let (result, lapsed) = main_crypto_core_ed25519_scalar_random();
    
    // let (result, lapsed) = main_crypto_aead_chacha20poly1305_ietf_decrypt_detached();
    // let (r2, lapsed2) = main_crypto_aead_chacha20poly1305_ietf_encrypt_detached();
    // ==============================================


    let mut hasher = DefaultHasher::new();

	
	let pop = match std::env::var("FASTLY_POP") {
		Ok(val) => val,
		Err(_) => "NO_POP".to_string()
	};

    // PoP discriminator
    pop.hash(&mut hasher);
    // get path and send thourgh header
    let path = STACKTRACE.lock().unwrap().join(",");

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
            .header("Xpath", format!("{}", path))
            .body(Body::from(format!("POP: {} Result {:?} ", pop, result
            )))?),
      
        // Catch all other requests and return a 404.
        _ => Ok(Response::builder()
            .status(StatusCode::NOT_FOUND)
            .body(Body::from("The page you requested could not be found"))?),
    }
}

//ebeeeea1b8c6ceabd5a4f0c80c68ccf312267b3e4d5488442bea9df52f7d3f00cab6dbd45b7e5f884a4895000e94010441ea9070aed86b97f0fe087d19e5f353
//66aa39821189f2cce1ffdad44f3aa60dd276599505f920581350150eda5429d44687a2309d69975ddd6e67c423b91954d0ae3bdb33b19816041716b7c7ef2045


