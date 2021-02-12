//! Default Compute@Edge template program.
#![feature(asm)]
//#![feature(naked_functions)]
#![feature(global_asm)]

use fastly::http::{HeaderValue, Method, StatusCode,Response as HTTPResponse};
use fastly::request::CacheOverride;
use fastly::{Body, Error, Request, RequestExt, Response, ResponseExt};

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
    

    let mut loop_sum = 0;
    // Pattern match on the request method and path.
    match (req.method(), req.uri().path()) {

        // If request is a `GET` to the `/backend` path, send to a named backend.
        (&Method::GET, "/") => {
        
            let now = std::time::Instant::now();

            Ok(Response::builder()
            .status(StatusCode::OK)
            .header("Xtime", format!("{}", now.elapsed().as_nanos()))
            .body(Body::from("HOME"))?)
        },


        (&Method::GET, "/sleep200u") => {

            let now = std::time::Instant::now();
            let duration = std::time::Duration::from_micros(200);

            while true {
                if (now.elapsed() >= duration)
                {    break;}
            }

            Ok(Response::builder()
            .status(StatusCode::OK)
            .header("Xtime", format!("{}", now.elapsed().as_nanos()))
            .body(Body::from("SLEEP"))?)

        },


        (&Method::GET, "/sleep10u") => {

            let now = std::time::Instant::now();
            let duration = std::time::Duration::from_micros(10);

            while true {
                if (now.elapsed() >= duration)
                {    break;}
            }

            Ok(Response::builder()
            .status(StatusCode::OK)
            .header("Xtime", format!("{}", now.elapsed().as_nanos()))
            .body(Body::from("SLEEP"))?)

        },

        (&Method::GET, "/sleep50u") => {

            let now = std::time::Instant::now();
            let duration = std::time::Duration::from_micros(50);

            while true {
                if (now.elapsed() >= duration)
                {    break;}
            }

            Ok(Response::builder()
            .status(StatusCode::OK)
            .header("Xtime", format!("{}", now.elapsed().as_nanos()))
            .body(Body::from("SLEEP"))?)

        },


        (&Method::GET, "/sleep100u") => {

            let now = std::time::Instant::now();
            let duration = std::time::Duration::from_micros(100);

            while true {
                if (now.elapsed() >= duration)
                {    break;}
            }

            Ok(Response::builder()
            .status(StatusCode::OK)
            .header("Xtime", format!("{}", now.elapsed().as_nanos()))
            .body(Body::from("SLEEP"))?)

        },



        (&Method::GET, "/sleep02") => {

            let now = std::time::Instant::now();
            let duration = std::time::Duration::from_millis(200);

            while true {
                if (now.elapsed() >= duration)
                {    break;}
            }

            Ok(Response::builder()
            .status(StatusCode::OK)
            .header("Xtime", format!("{}", now.elapsed().as_nanos()))
            .body(Body::from("SLEEP"))?)

        },

        (&Method::GET, "/sleep05") => {

            let now = std::time::Instant::now();
            let duration = std::time::Duration::from_millis(500);

            while true {
                if (now.elapsed() >= duration)
                {    break;}
            }

            Ok(Response::builder()
            .status(StatusCode::OK)
            .header("Xtime", format!("{}", now.elapsed().as_nanos()))
            .body(Body::from("SLEEP"))?)

        },

        (&Method::GET, "/sleep1") => {

            let now = std::time::Instant::now();
            let duration = std::time::Duration::from_millis(1000);

            while true {
                if (now.elapsed() >= duration)
                {    break;}
            }

            Ok(Response::builder()
            .status(StatusCode::OK)
            .header("Xtime", format!("{}", now.elapsed().as_nanos()))
            .body(Body::from("SLEEP"))?)

        },

        (&Method::GET, "/sleep2") => {

            let now = std::time::Instant::now();
            let duration = std::time::Duration::from_millis(2000);

            while true {
                if (now.elapsed() >= duration)
                {    break;}
            }

            Ok(Response::builder()
            .status(StatusCode::OK)
            .header("Xtime", format!("{}", now.elapsed().as_nanos()))
            .body(Body::from("SLEEP"))?)

        },

        // Catch all other requests and return a 404.
        _ => Ok(Response::builder()
            .status(StatusCode::NOT_FOUND)
            .body(Body::from("The page you requested could not be found"))?),
    }
}