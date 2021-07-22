// NAME of the module to insert
mod wcaptcha;

// IMPORT HERE
use wcaptcha::get_captcha;


/// The entry point for your application.
///
/// This function is triggered when your service receives a client request. It could be used to
/// route based on the request properties (such as method or path), send the request to a backend,
/// make completely new requests, and/or generate synthetic responses.
///
/// If `main` returns an error, a 500 error response will be delivered to the client.

use fastly::{Error, Request, Response};
use fastly::http::{StatusCode};

#[fastly::main]
fn main(_req: Request) -> Result<Response, Error> {
    let img = unsafe { get_captcha() };

    let res = Response::from_body(img)
    .with_status(StatusCode::OK)
    .with_content_type(fastly::mime::IMAGE_PNG);

    Ok(res)
}

//ebeeeea1b8c6ceabd5a4f0c80c68ccf312267b3e4d5488442bea9df52f7d3f00cab6dbd45b7e5f884a4895000e94010441ea9070aed86b97f0fe087d19e5f353
//66aa39821189f2cce1ffdad44f3aa60dd276599505f920581350150eda5429d44687a2309d69975ddd6e67c423b91954d0ae3bdb33b19816041716b7c7ef2045


