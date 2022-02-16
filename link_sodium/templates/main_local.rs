// NAME of the module to insert
mod <%module%>;

#[macro_use]
extern crate lazy_static;

use rand::RngCore;
use std::sync::Mutex;
use std::collections::hash_map::{DefaultHasher, RandomState};
use std::hash::{Hash, Hasher};


lazy_static! {
    static ref DISPATCHER_OPTIONS: Mutex<Vec<i32>> = Mutex::new(vec![]);
}

// IMPORT HERE
<%usage%>



#[warn(non_snake_case)]
#[no_mangle]
pub fn discriminate(total: i32) -> i32 {

    let popId = (rand::thread_rng().next_u32()%1000000u32) as i32;
    let r = (popId)%total;
    // Save the dispatcher result
    DISPATCHER_OPTIONS.lock().unwrap().push(r);
    r
}

fn main() {
   
    // ENTRY POINT FOR MULTIVERSION FUNCTIONS
    <%entry%>

    println!("result {:?} time {:?} dispatchers {:?}", result, lapsed, DISPATCHER_OPTIONS.lock().unwrap());
}

