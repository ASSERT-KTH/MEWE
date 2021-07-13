#[macro_use]
use diversifier::{static_diversification,dynamic_diversification_body,  dynamic_diversification, multiple_import, expand };
use core::slice;
use std::ffi::CString;
use libc::*;


extern "C" {
    pub fn crypto_aead_chacha20poly1305_ietf_decrypt_detached (   
        m: *mut c_uchar, 
        nsec: *mut c_uchar, 
        c: *const c_uchar, 
        clen: c_ulonglong, 
        mac: *const c_uchar, 
        ad: *const c_uchar, 
        adlen: c_ulonglong, 
        npub: *const c_uchar, 
        k: *const c_uchar
    ) -> i32;
}


pub fn crypto_aead_chacha20poly1305_ietf_decrypt_detached_wrapper() -> i32 {
    
    unsafe {

        
        let key_hex = CString::new("46f0254965f769d52bdb4a70b443199f8ef207520d1220c55e4b70f0fda620ee").expect("CString::new failed");// publc key
        let key_hex_ptr = key_hex.as_ptr() as *mut u8;

        let nonce_hex = CString::new("ab0dca716ee051d2782f4403").expect("CString::new failed");// publc key
        let nonce_hex_ptr = nonce_hex.as_ptr() as *mut u8;

        
        let ad_hex = CString::new("91ca6c592cbcca53").expect("CString::new failed");// publc key
        let ad_hex_ptr = ad_hex.as_ptr() as *mut u8;

        let message_hex = CString::new("51").expect("CString::new failed");// publc key
        let message_hex_ptr = message_hex.as_ptr() as *mut u8;

        let detached_cypher_text_hex = CString::new("c4").expect("CString::new failed");// publc key
        let detached_cypher_text_hex_ptr = detached_cypher_text_hex.as_ptr() as *mut u8;

        let mac_hex = CString::new("168310ca45b1f7c66cad4e99e43f72b9").expect("CString::new failed");// publc key
        let mac_hex_ptr = mac_hex.as_ptr() as *mut u8;

        let outcome = CString::new("valid").expect("CString::new failed");// publc key
        let outcome_ptr = outcome.as_ptr() as *mut u8;

        let nsec = CString::new("valid").expect("");// publc key
        let nsec_ptr = nsec.as_ptr() as *mut u8;

        crypto_aead_chacha20poly1305_ietf_decrypt_detached(outcome_ptr, nsec_ptr, detached_cypher_text_hex_ptr, 2, mac_hex_ptr, ad_hex_ptr, 8, nonce_hex_ptr, key_hex_ptr)

    }
}

static  FIRST_KEY: [u8;32] = [
    0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87,
    0x88, 0x89, 0x8a, 0x8b, 0x8c, 0x8d, 0x8e, 0x8f,
    0x90, 0x91, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97,
    0x98, 0x99, 0x9a, 0x9b, 0x9c, 0x9d, 0x9e, 0x9f
];




extern "C" {
    pub fn crypto_aead_chacha20poly1305_ietf_encrypt_detached (   

        c: *mut c_uchar, 
        mac: *mut c_uchar, 
        maclen_p: *mut c_ulonglong, 
        m: *const c_uchar, 
        mlen: c_ulonglong, 
        ad: *const c_uchar, 
        adlen: c_ulonglong, 
        nsec: *const c_uchar, 
        npub: *const c_uchar, 
        k: *const c_uchar
    ) -> i32;
}


pub fn crypto_aead_chacha20poly1305_ietf_encrypt_detached_wrapper() -> i32 {
    
    unsafe {

        let message = "Diversification is cool!";// message 24 characters
        let slice = slice::from_raw_parts(message.as_ptr(), 24);
        let mut detached_c = [0u8; 24];

        let mut mac =  [0u8; 16];

        // The way to allocate changes the final Wasm !
        let found_maclen: *mut c_ulonglong = libc::malloc(std::mem::size_of::<u64>()) as *mut c_ulonglong;

        let nonce: [u8;12]  = [0x50, 0x51, 0x52, 0x53, 0xc0, 0xc1, 0xc2, 0xc3, 0xc4, 0xc5, 0xc6, 0xc7];
        let ad: [u8;12]  = [
            0x07, 0x00, 0x00, 0x00,
            0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47];

            crypto_aead_chacha20poly1305_ietf_encrypt_detached(
                detached_c.as_mut_ptr(), 
                mac.as_mut_ptr(), 
                found_maclen, 
                slice.as_ptr(), 
                slice.len() as u64, 
                ad.as_ptr(), ad.len() as u64, 
                std::ptr::null(), 
                nonce.as_ptr(), FIRST_KEY.as_ptr())

    }
}


// Return result, elapsed
pub fn main_crypto_aead_chacha20poly1305_ietf_decrypt_detached() -> (i32, u128){

    let now = std::time::Instant::now();
   

    (crypto_aead_chacha20poly1305_ietf_decrypt_detached_wrapper(), now.elapsed().as_nanos())
}

pub fn main_crypto_aead_chacha20poly1305_ietf_encrypt_detached() -> (i32, u128){

    let now = std::time::Instant::now();
   
    (crypto_aead_chacha20poly1305_ietf_encrypt_detached_wrapper(), now.elapsed().as_nanos())
}