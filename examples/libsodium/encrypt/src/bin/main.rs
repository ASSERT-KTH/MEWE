

use std::hash::{Hash, Hasher};

pub fn main() {
    let (result, lapsed) = unsafe { encrypt::main_crypto_aead_chacha20poly1305_ietf_encrypt_detached()};
    
    println!("Base46 encoding {:?} in {:?}", result ,lapsed);
}