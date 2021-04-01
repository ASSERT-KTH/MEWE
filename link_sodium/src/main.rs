//! Default Compute@Edge template program.
// #![feature(asm)]
//#![feature(naked_functions)]
// #![feature(global_asm)]

use fastly::http::{HeaderValue, Method, StatusCode};
use fastly::request::CacheOverride;
use fastly::{Body, Error, Request, RequestExt, Response, ResponseExt};
use std::ffi::CString;
use rand::RngCore;

//use wat2mir_macro::{inject_mir_as_wasm, inject_mir_from_wasm};
use diversifier::{static_diversification,dynamic_diversification_body,  dynamic_diversification};

/// The name of a backend server associated with this service.
///
/// This should be changed to match the name of your own backend. See the the `Hosts` section of
/// the Fastly WASM service UI for more information.
const BACKEND_NAME: &str = "backend_name";

/// The name of a second backend associated with this service.
const OTHER_BACKEND_NAME: &str = "other_backend_name";

/// The entry point for your application.
///
/// This function is triggered when your service receives a client request. It could be used to
/// route based on the request properties (such as method or path), send the request to a backend,
/// make completely new requests, and/or generate synthetic responses.
///
/// If `main` returns an error, a 500 error response will be delivered to the client.
#[fastly::main]
fn main(mut req: Request<Body>) -> Result<impl ResponseExt, Error> {
    // Make any desired changes to the client request.
    req.headers_mut()
        .insert("Host", HeaderValue::from_static("example.com"));

    // We can filter requests that have unexpected methods.
    const VALID_METHODS: [Method; 3] = [Method::HEAD, Method::GET, Method::POST];
    if !(VALID_METHODS.contains(req.method())) {
        return Ok(Response::builder()
            .status(StatusCode::METHOD_NOT_ALLOWED)
            .body(Body::from("This method is not allowed"))?);
    }

	let pop = match std::env::var("FASTLY_POP") {
		Ok(val) => val,
		Err(_) => "NO_POP".to_string()
	};

    let to_encode = CString::new("HelloWorld!").expect("CString::new failed");
    let size = 20 as usize;
    let to_encode_ptr = to_encode.as_ptr() as *mut u8;

    // Pop discriminator

	let DIS = rand::thread_rng().next_u32() % 4;
	//let now = Instant::now();
	//let lapse = now.elapsed().as_nanos();

    // Pattern match on the request method and path.
    match (req.method(), req.uri().path()) {
        // If request is a `GET` to the `/` path, send a default response.
        (&Method::GET, "/") => Ok(Response::builder()
            .status(StatusCode::OK)
            .body(Body::from(format!("POP: {} {:?} Result {:?} ", pop, DIS,
            sodium_bin2base64_wrapper(DIS, 50, to_encode_ptr, size))))?),
        
        // If request is a `GET` to the `/backend` path, send to a named backend.
        (&Method::GET, "/backend") => {
            // Request handling logic could go here...
            // E.g., send the request to an origin backend and then cache the
            // response for one minute.
            *req.cache_override_mut() = CacheOverride::ttl(60);
            Ok(req.send(BACKEND_NAME)?)
        }

        // If request is a `GET` to a path starting with `/other/`.
        (&Method::GET, path) if path.starts_with("/other/") => {
            // Send request to a different backend and don't cache response.
            *req.cache_override_mut() = CacheOverride::Pass;
            Ok(req.send(OTHER_BACKEND_NAME)?)
        }

        // Catch all other requests and return a 404.
        _ => Ok(Response::builder()
            .status(StatusCode::NOT_FOUND)
            .body(Body::from("The page you requested could not be found"))?),
    }
}


extern "C" {
    pub fn sodium_bin2base64(
        b64: *mut libc::c_char,
        b64_maxlen: usize,
        bin: *const libc::c_uchar,
        bin_len: usize,
        variant: libc::c_int,
    ) -> *mut libc::c_char;
}


extern "C" {
    pub fn sodium_bin2base64_3_(
        b64: *mut libc::c_char,
        b64_maxlen: usize,
        bin: *const libc::c_uchar,
        bin_len: usize,
        variant: libc::c_int,
    ) -> *mut libc::c_char;
}


extern "C" {
    pub fn sodium_bin2base64_4_(
        b64: *mut libc::c_char,
        b64_maxlen: usize,
        bin: *const libc::c_uchar,
        bin_len: usize,
        variant: libc::c_int,
    ) -> *mut libc::c_char;
}


extern "C" {
    pub fn sodium_bin2base64_5_(
        b64: *mut libc::c_char,
        b64_maxlen: usize,
        bin: *const libc::c_uchar,
        bin_len: usize,
        variant: libc::c_int,
    ) -> *mut libc::c_char;
}


extern "C" {
    pub fn sodium_bin2base64_6_(
        b64: *mut libc::c_char,
        b64_maxlen: usize,
        bin: *const libc::c_uchar,
        bin_len: usize,
        variant: libc::c_int,
    ) -> *mut libc::c_char;
}


pub fn sodium_bin2base64_wrapper(dis: u32, size: usize, bin: *const libc::c_uchar, bin_len: usize) -> CString{
    unsafe {
        let mut buf =  libc::malloc(size) as *mut libc::c_char;
        //let r = sodium_bin2base64(buf, size, bin, bin_len, 5 ); // 5 for url safe
        let r = match dis {
            0 => sodium_bin2base64(buf, size, bin, bin_len, 1 ),
            1 => sodium_bin2base64_3_(buf, size, bin, bin_len, 1 ),
            2 => sodium_bin2base64_4_(buf, size, bin, bin_len, 1 ),
            3 => sodium_bin2base64_5_(buf, size, bin, bin_len, 1 ),
            4 => sodium_bin2base64_6_(buf, size, bin, bin_len, 1 ),
            _ => panic!("I dont what to do with {}", dis)
        };
        CString::from_raw(buf)
    }
}

/*
sodium_bin2base64_3_
sodium_bin2base64_4_
sodium_bin2base64_5_
sodium_bin2base64_6_
sodium_bin2base64_7_
sodium_bin2base64_8_
sodium_bin2base64_9_
sodium_bin2base64_10_
sodium_bin2base64_11_
sodium_bin2base64_12_
sodium_bin2base64_13_
sodium_bin2base64_14_
sodium_bin2base64_15_
sodium_bin2base64_16_
sodium_bin2base64_17_
sodium_bin2base64_18_
sodium_bin2base64_19_
sodium_bin2base64_20_
sodium_bin2base64_21_
sodium_bin2base64_22_
sodium_bin2base64_23_
sodium_bin2base64_24_
sodium_bin2base64_25_
sodium_bin2base64_26_
sodium_bin2base64_27_
sodium_bin2base64_28_
sodium_bin2base64_29_
sodium_bin2base64_30_
sodium_bin2base64_31_
sodium_bin2base64_32_
sodium_bin2base64_33_
sodium_bin2base64_34_
sodium_bin2base64_35_
sodium_bin2base64_36_
sodium_bin2base64_37_
sodium_bin2base64_38_
sodium_bin2base64_39_
sodium_bin2base64_40_
sodium_bin2base64_41_
sodium_bin2base64_42_
sodium_bin2base64_43_
*/
