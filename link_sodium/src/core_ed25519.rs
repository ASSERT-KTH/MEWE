#[macro_use]
use diversifier::{static_diversification,dynamic_diversification_body,  dynamic_diversification, multiple_import, expand };
use std::ffi::CString;

multiple_import!(
    (   
        m: *mut libc::c_uchar) -> (), 
    (
        crypto_core_ed25519_scalar_random, 
    )
);


multiple_import!(
    (   
        m: *mut libc::c_uchar,
        sc: *const libc::c_uchar) -> (), 
    (
        crypto_core_ed25519_scalar_complement, 
    )
);


multiple_import!(
    (   
        m: *mut libc::c_uchar,
        sc: *const libc::c_uchar) -> i32, 
    (
        crypto_core_ed25519_scalar_invert, 
    )
);

pub fn crypto_core_ed25519_scalar_invert_wrapper(dis: u32) -> (i32) {
    
    unsafe {
        let plain_size = 100;
        let mut plain =  libc::malloc(plain_size) as *mut libc::c_uchar; // WATCH OUT, regular Vec::allocate does not work
        
        dynamic_diversification_body!(
            crypto_core_ed25519_scalar_invert(plain, plain),
        )
    }
}

pub fn crypto_core_ed25519_scalar_complement_wrapper(dis: u32) -> (CString) {
    
    unsafe {
        let plain_size = 100;
        let mut plain =  libc::malloc(plain_size) as *mut libc::c_uchar; // WATCH OUT, regular Vec::allocate does not work
        
        dynamic_diversification_body!(
            crypto_core_ed25519_scalar_complement(plain, plain),
        );
        CString::from_raw(plain as  *mut libc::c_char)
    }
}


pub fn crypto_core_ed25519_scalar_random_wrapper(dis: u32) -> (CString) {
    
    unsafe {
        let plain_size = 100;
        let mut plain =  libc::malloc(plain_size) as *mut libc::c_uchar; // WATCH OUT, regular Vec::allocate does not work
        
        dynamic_diversification_body!(
            crypto_core_ed25519_scalar_random(plain),
        );
        CString::from_raw(plain as  *mut libc::c_char)
    }
}







// Return result, elapsed
pub fn main_crypto_core_ed25519_scalar_random(hashValue: u64) -> (CString, u128, u32){

    let now = std::time::Instant::now();
   

    let DIS = (hashValue % 1) as u32;
    (crypto_core_ed25519_scalar_random_wrapper(DIS), now.elapsed().as_nanos(), DIS)
}


// Return result, elapsed
pub fn main_crypto_core_ed25519_scalar_complement(hashValue: u64) -> (CString, u128, u32){

    let now = std::time::Instant::now();
   

    let DIS = (hashValue % 1) as u32;
    (crypto_core_ed25519_scalar_complement_wrapper(DIS), now.elapsed().as_nanos(), DIS)
}


// Return result, elapsed
pub fn main_crypto_core_ed25519_scalar_invert(hashValue: u64) -> (i32, u128, u32){

    let now = std::time::Instant::now();
   

    let DIS = (hashValue % 1) as u32;
    (crypto_core_ed25519_scalar_invert_wrapper(DIS), now.elapsed().as_nanos(), DIS)
}
