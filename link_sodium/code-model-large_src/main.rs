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

             use std::ffi::CString;

            extern "C" {
                pub fn sodium_bin2base64(b64: *mut libc::c_char,
                    b64_maxlen: usize,
                    bin: *const libc::c_uchar,
                    bin_len: usize,
                    variant: libc::c_int) -> *mut libc::c_char;
            }
            
            

            pub fn sodium_bin2base64_original_wrapper(size: usize, bin: *const libc::c_uchar, bin_len: usize) -> CString{
                unsafe {
                    let mut buf = vec![0i8;size];
                    sodium_bin2base64(buf.as_mut_ptr(), size, bin, bin_len, 5);
                    CString::from_raw(buf.as_mut_ptr())
                }
            }


            pub fn main_bin2base64_time() -> (CString, u128){
            
                let now = std::time::Instant::now();
            
                let to_encode = CString::new("HelloWorld!").expect("CString::new failed");
                let size = 20 as usize;
                let to_encode_ptr = to_encode.as_ptr() as *mut u8;
            
                (sodium_bin2base64_original_wrapper(50, to_encode_ptr, size), now.elapsed().as_nanos())
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
    
         let (result, lapsed) = main_bin2base64_time();
         

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

