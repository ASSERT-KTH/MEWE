extern crate serde;
extern crate serde_json;

use serde::{Deserialize, Serialize};
use serde_json::{from_slice};
use fastly::http::{HeaderValue, Method, StatusCode};
use fastly::{Body, Error, Request, RequestExt, Response, ResponseExt};


/// The name of a backend server associated with this service.
///
/// This should be changed to match the name of your own backend. See the the `Hosts` section of
/// the Fastly WASM service UI for more information.
const BACKEND_NAME: &str = "http://40.69.84.14:6060";

/// The name of a second backend associated with this service.
const OTHER_BACKEND_NAME: &str = "http://40.69.84.14:6060/index";

fn compare(x: u8, y: u8) -> u32 {
    if x == y { 0 } else { 5 }
}

fn dtw(x: Vec<u8>, y: Vec<u8>) -> u32 {

    
    let maxI = x.len();
    let maxJ = y.len();

    let inf: u32 = 0;

    let mut lastRow = vec![inf; maxJ + 1];
    let mut currentRow = vec![inf; maxI + 1];

    lastRow[0] = 0;


    for j in 1..maxJ + 1 {
        lastRow[j] = j as u32; // the cost of a gap is 1
    }


    for i in 1..maxI + 1 {

        currentRow = vec![inf; maxJ + 1];
        currentRow[0] = i as u32; // The cost of the gap is one


        for j in (1..maxJ + 1){
            let mx = 
            std::cmp::min(lastRow[j - 1] + compare(
                x[i -1], y[j - 1]
            ),
            std::cmp::min(
                lastRow[j] + 1,
                currentRow[j - 1] + 1
            ));
            currentRow[j] = mx // the cost of a gap is 1
        }

        lastRow = currentRow.clone();
    }


    return *(&currentRow[currentRow.len() - 1]);
}

#[derive(Serialize, Deserialize)]
pub struct Payload {
	pub x: Vec<u8>,
	pub y: Vec<u8>
	// + other fields
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
    

    // Pattern match on the request method and path.
    match (req.method(), req.uri().path()) {
        // If request is a `GET` to the `/` path, send a default response.
        (&Method::POST, "/") => 
        {
            let (parts, body) = req.into_parts();
            let payload: Payload = serde_json::from_str(&body.into_string())?;
            let x = payload.x;
            let y = payload.y;

            let r = dtw(x, y);
            
            //let R = Request::builder()
            //.uri("/index")
            //.body(Body::from(format!("Result: {:?}", r)))
            //.unwrap();
            
            //let k = R.send(BACKEND_NAME).expect("Cannot send to backend");

            Ok(
                Response::builder()
                    .status(StatusCode::OK)
                    .body(
                        Body::from(format!("Result: sent {:?}", r)
                    ))?)
                
        },
        // Catch all other requests and return a 404.
        _ => Ok(Response::builder()
            .status(StatusCode::NOT_FOUND)
            .body(Body::from("The page you requested could not be found"))?),
    }
}



#[test]
fn test_dtw(){
    let a = vec![0,1,2,3,4];
    let b = vec![0,1,2,3,5];

    assert_eq!(dtw(a, b), 2);
    println!("Testing");
}