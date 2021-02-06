//! Default Compute@Edge template progra

use fastly::http::{HeaderValue, Method, StatusCode};
use fastly::request::CacheOverride;
use fastly::{Body, Error, Request, RequestExt, Response, ResponseExt};
use std::{thread, time};

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
    // Pattern match on the request method and path.
    match (req.method(), req.uri().path()) {
        // If request is a `GET` to the `/` path, send a default response.
        (&Method::GET, "/") => Ok(Response::builder()
            .status(StatusCode::OK)
            .body(Body::from(format!("Regular OK")))?),
        
        // If request is a `GET` to the `/backend` path, send to a named backend.
        (&Method::GET, "/reallylongkeythatmaytakesometimetoprocessbeacuseisquitelargeandcomplex") => 
        {
            Ok(Response::builder()
            .status(StatusCode::OK)
            .body(Body::from(format!("Gotcha")))?)
        },
        (&Method::GET, "/time") => 
        {

            let ten_millis = time::Duration::from_millis(10);
            let now = time::Instant::now();

            thread::sleep(ten_millis);
            
            Ok(Response::builder()
            .status(StatusCode::OK)
            .body(Body::from(format!("Time")))?)
        },

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
