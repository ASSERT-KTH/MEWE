

use std::hash::{Hash, Hasher};

pub fn main() {
    let (result, lapsed) = unsafe { random::main_crypto_core_ed25519_scalar_random()};
    
    println!("Result {:?} in {:?}", result ,lapsed);
}