

use std::hash::{Hash, Hasher};

pub fn main() {
    let (result, lapsed) = unsafe { decrypt::main_crypto_aead_chacha20poly1305_ietf_decrypt_detached()};
    
    println!("Result{:?} in {:?}", result ,lapsed);
}