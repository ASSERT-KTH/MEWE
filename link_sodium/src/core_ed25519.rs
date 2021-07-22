#[macro_use]
use std::ffi::CString;

extern "C" {
    pub fn crypto_core_ed25519_scalar_random(   
        m: *mut libc::c_uchar) -> ();
}


extern "C" {
    pub fn crypto_core_ed25519_scalar_complement(   
        m: *mut libc::c_uchar,
        sc: *const libc::c_uchar) -> ();
}

extern "C" {
    pub fn crypto_core_ed25519_scalar_invert(   
        m: *mut libc::c_uchar,
        sc: *const libc::c_uchar) -> i32;
}


pub fn crypto_core_ed25519_scalar_invert_wrapper() -> (i32) {
    
    unsafe {
        let mut plain = [0u8;100];
        crypto_core_ed25519_scalar_invert(plain.as_mut_ptr(), plain.as_mut_ptr())
    }
}

pub fn crypto_core_ed25519_scalar_complement_wrapper() -> (CString) {
    
    unsafe {
        let mut plain = [0u8;100];
        crypto_core_ed25519_scalar_complement(plain.as_mut_ptr(), plain.as_mut_ptr());
        CString::from_raw(plain.as_mut_ptr() as *mut libc::c_char)
    }
}


pub fn crypto_core_ed25519_scalar_random_wrapper() -> (CString) {
    
    unsafe {
        let mut plain = [0u8;100];
        crypto_core_ed25519_scalar_random(plain.as_mut_ptr());
        CString::from_raw(plain.as_mut_ptr() as *mut libc::c_char)
    }
}







// Return result, elapsed
pub fn main_crypto_core_ed25519_scalar_random() -> (CString, u128){

    let now = std::time::Instant::now();
   
    (crypto_core_ed25519_scalar_random_wrapper(), now.elapsed().as_nanos())
}


// Return result, elapsed
pub fn main_crypto_core_ed25519_scalar_complement() -> (CString, u128){

    let now = std::time::Instant::now();
   
    (crypto_core_ed25519_scalar_complement_wrapper(), now.elapsed().as_nanos())
}


// Return result, elapsed
pub fn main_crypto_core_ed25519_scalar_invert() -> (i32, u128){

    let now = std::time::Instant::now();
   
    (crypto_core_ed25519_scalar_invert_wrapper(), now.elapsed().as_nanos())
}
