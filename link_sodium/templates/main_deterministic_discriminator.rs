// NAME of the module to insert
mod <%module%>;

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

#[warn(non_snake_case)]
#[no_mangle]
pub fn discriminate(total: i32) -> i32 {

	let pop = match std::env::var("FASTLY_POP") {
		Ok(val) => val,
		Err(_) => "NO_POP".to_string()
	};

    let popId = match pop.as_str(){
        "AMS" => 0,
        "IAD" => 1,
        "WDC" => 2,
        "BWI" => 3,
        "DCA" => 4,
        "FTY" => 5,
        "PDK" => 6,
        "AKL" => 7,
        "BOG" => 8,
        "BOS" => 9,
        "BNE" => 10,
        "EZE" => 11,
        "CPT" => 12,
        "MAA" => 13,
        "ORD" => 14,
        "CHI" => 15,
        "MDW" => 16,
        "PWK" => 17,
        "CMH" => 18,
        "LCK" => 19,
        "CPH" => 20,
        "CWB" => 21,
        "DFW" => 22,
        "DAL" => 23,
        "DEL" => 24,
        "DEN" => 25,
        "DUB" => 26,
        "FRA" => 27,
        "HHN" => 28,
        "FJR" => 29,
        "HEL" => 30,
        "HKG" => 31,
        "IAH" => 32,
        "JAX" => 33,
        "JNB" => 34,
        "MCI" => 35,
        "LCY" => 36,
        "LHR" => 37,
        "LON" => 38,
        "LGB" => 39,
        "BUR" => 40,
        "LAX" => 41,
        "MAD" => 42,
        "MAN" => 43,
        "MRS" => 44,
        "MEL" => 45,
        "MIA" => 46,
        "MXP" => 47,
        "MSP" => 48,
        "STP" => 49,
        "YUL" => 50,
        "BOM" => 51,
        "JFK" => 52,
        "LGA" => 53,
        "EWR" => 54,
        "ITM" => 55,
        "OSL" => 56,
        "PAO" => 57,
        "CDG" => 58,
        "PER" => 59,
        "PHX" => 60,
        "PDX" => 61,
        "GIG" => 62,
        "SJC" => 63,
        "SCL" => 64,
        "CGH" => 65,
        "GRU" => 66,
        "SEA" => 67,
        "QPG" => 68,
        "SIN" => 69,
        "STL" => 70,
        "BMA" => 71,
        "SYD" => 72,
        "TYO" => 73,
        "HND" => 74,
        "YYZ" => 75,
        "YVR" => 76,
        "VIE" => 77,
        "WLG" => 78,
        _ => 79

    };
    popId%total
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

//ebeeeea1b8c6ceabd5a4f0c80c68ccf312267b3e4d5488442bea9df52f7d3f00cab6dbd45b7e5f884a4895000e94010441ea9070aed86b97f0fe087d19e5f353
//66aa39821189f2cce1ffdad44f3aa60dd276599505f920581350150eda5429d44687a2309d69975ddd6e67c423b91954d0ae3bdb33b19816041716b7c7ef2045


