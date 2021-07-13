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

lazy_static! {
   static ref STACKTRACE: Mutex<Vec<i32>> = Mutex::new(vec![]);
}

#[warn(non_snake_case)]
#[no_mangle]
pub fn _cb71P5H47J3A(id: i32) {

   let now =  SystemTime::now().duration_since(SystemTime::UNIX_EPOCH).unwrap().as_nanos();

      let pop = match std::env::var("FASTLY_POP") {
         Ok(val) => val,
         Err(_) => "NO_POP".to_string()
      };


    // Save in global path header
    log::warn!("FLIPH, {}, {}, {}", now, pop, id);
}



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

    match (_req.get_method(), _req.get_path())
    {
        (_, "/flipv") => {
            let fl = unsafe {flipv_image(decoded)};
            let encoded=encode_dynimg(fl);
            let path = STACKTRACE.lock().unwrap();
            let res = Response::from_body(format!("{:?}", path))
            //.with_header("Xpath", format!("{:?}", path))
            .with_header("Xtime", format!("{:?}", now.elapsed().as_nanos()))
            .with_header("Xpop", format!("{:?}", pop))
            .with_header("Content-Type", "image/png")
            //.with_header("XContent", img)
            .with_status(StatusCode::OK);
            Ok(res)
         }
         (_, "/fliph") => {
            let fl = unsafe {fliph_image(decoded)};
            let encoded=encode_dynimg(fl);
            let path = STACKTRACE.lock().unwrap();
            let res = Response::from_body(format!("{:?}", path))
            //.with_header("Xpath", format!("{:?}", path))
            .with_header("Xtime", format!("{:?}", now.elapsed().as_nanos()))
            .with_header("Xpop", format!("{:?}", pop))
            .with_header("Content-Type", "image/png")
            //.with_header("XContent", img)
            .with_status(StatusCode::OK);
            Ok(res)
         }
         (_, "/rotate90") => {
            let fl = unsafe {rotate90_image(decoded)};
            let encoded=encode_dynimg(fl);
            let path = STACKTRACE.lock().unwrap();
            let res = Response::from_body(format!("{:?}", path))
            //.with_header("Xpath", format!("{:?}", path))
            .with_header("Xtime", format!("{:?}", now.elapsed().as_nanos()))
            .with_header("Xpop", format!("{:?}", pop))
            .with_header("Content-Type", "image/png")
            //.with_header("XContent", img)
            .with_status(StatusCode::OK);
            Ok(res)
         }
         (_, "/blur") => {
            let fl = unsafe {blur_image(decoded)};
            let encoded=encode_dynimg(fl);
            let path = STACKTRACE.lock().unwrap();
            let res = Response::from_body(format!("{:?}", path))
            //.with_header("Xpath", format!("{:?}", path))
            .with_header("Xtime", format!("{:?}", now.elapsed().as_nanos()))
            .with_header("Xpop", format!("{:?}", pop))
            .with_header("Content-Type", "image/png")
            //.with_header("XContent", img)
            .with_status(StatusCode::OK);
            Ok(res)
         }
         (_, "/crop") => {
            let fl = unsafe {crop_image(&mut decoded)};
            let encoded=encode_dynimg(fl);
            let path = STACKTRACE.lock().unwrap();
            let res = Response::from_body(format!("{:?}", path))
            .with_header("Xtime", format!("{:?}", now.elapsed().as_nanos()))
            .with_header("Xpop", format!("{:?}", pop))
            .with_header("Content-Type", "image/png")
            //.with_header("XContent", img)
            .with_status(StatusCode::OK);
            Ok(res)
         }
         (_, "/gray") => {
            let fl = unsafe {grayscale_image(&mut decoded)};
            let encoded=encode_dynimg(fl);
            let path = STACKTRACE.lock().unwrap();
            let res = Response::from_body(format!("{:?}", path))
            //.with_header("Xpath", format!("{:?}", path))
            .with_header("Xtime", format!("{:?}", now.elapsed().as_nanos()))
            .with_header("Xpop", format!("{:?}", pop))
            .with_header("Content-Type", "image/png")
            //.with_header("XContent", img)
            .with_status(StatusCode::OK);
            Ok(res)
         }
         (_, "/invert") => {
            unsafe {invert_image(&mut decoded)};
            let encoded=encode_dynimg(decoded);
            let path = STACKTRACE.lock().unwrap();
            let res = Response::from_body(format!("{:?}", path))
            //.with_header("Xpath", format!("{:?}", path))
            .with_header("Xtime", format!("{:?}", now.elapsed().as_nanos()))
            .with_header("Xpop", format!("{:?}", pop))
            .with_header("Content-Type", "image/png")
            //.with_header("XContent", img)
            .with_status(StatusCode::OK);
            Ok(res)
         }
         (_, "/unsharp") => {
            let lt =unsafe {unsharpen_image(decoded)};
            let encoded=encode_dynimg(lt);
            let path = STACKTRACE.lock().unwrap();

            let res = Response::from_body(format!("{:?}", path))
            //.with_header("Xpath", format!("{:?}", path))
            .with_header("Xtime", format!("{:?}", now.elapsed().as_nanos()))
            .with_header("Xpop", format!("{:?}", pop))
            .with_header("Content-Type", "image/png")
            //.with_header("XContent", img)
            .with_status(StatusCode::OK);
            Ok(res)
         }
        _ => 
            Ok(Response::from_body("No valid option"))
    }

    //let lapsed = now.elapsed().as_nanos();
    
}

//ebeeeea1b8c6ceabd5a4f0c80c68ccf312267b3e4d5488442bea9df52f7d3f00cab6dbd45b7e5f884a4895000e94010441ea9070aed86b97f0fe087d19e5f353
//66aa39821189f2cce1ffdad44f3aa60dd276599505f920581350150eda5429d44687a2309d69975ddd6e67c423b91954d0ae3bdb33b19816041716b7c7ef2045


