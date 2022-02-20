

use std::hash::{Hash, Hasher};

pub fn main() {
    let (result, lapsed) = unsafe { invert::main_crypto_core_ed25519_scalar_invert()};
    
    println!("Result {:?} in {:?}", result ,lapsed);
}