

use std::hash::{Hash, Hasher};

pub fn main() {
    let (result, lapsed) = unsafe { bin2base64::main_bin2base64()};
    
    println!("Base46 encoding {:?} in {:?}", result ,lapsed);
}