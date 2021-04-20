#[macro_use]
use diversifier::{static_diversification,dynamic_diversification_body,  dynamic_diversification, multiple_import, expand };
use std::ffi::CString;


/*
	int crypto_sign_edwards25519sha512batch_open(unsigned char *m,
                                             unsigned long long *mlen_p,
                                             const unsigned char *sm,
                                             unsigned long long smlen,
                                             const unsigned char *pk)
*/

multiple_import!(
    (   
        m: *mut libc::c_uchar,
        mlen_p: *mut libc::c_ulonglong,
        sm: *const libc::c_uchar,
        smlen: libc::c_ulonglong,
        pk: *const libc::c_uchar) -> i32, 
    (
        crypto_sign_edwards25519sha512batch_open, 
        /*
        crypto_sign_edwards25519sha512batch_open_0_,
        crypto_sign_edwards25519sha512batch_open_1_,
        crypto_sign_edwards25519sha512batch_open_2_,
        crypto_sign_edwards25519sha512batch_open_3_,
        crypto_sign_edwards25519sha512batch_open_4_,
        crypto_sign_edwards25519sha512batch_open_5_,
        crypto_sign_edwards25519sha512batch_open_6_,
        crypto_sign_edwards25519sha512batch_open_7_,
        crypto_sign_edwards25519sha512batch_open_8_,
        crypto_sign_edwards25519sha512batch_open_9_,
        crypto_sign_edwards25519sha512batch_open_10,
        crypto_sign_edwards25519sha512batch_open_11,
        crypto_sign_edwards25519sha512batch_open_12,
        crypto_sign_edwards25519sha512batch_open_13,
        crypto_sign_edwards25519sha512batch_open_14,
        crypto_sign_edwards25519sha512batch_open_15,
        crypto_sign_edwards25519sha512batch_open_16,
        crypto_sign_edwards25519sha512batch_open_17,
        crypto_sign_edwards25519sha512batch_open_18,
        crypto_sign_edwards25519sha512batch_open_19,
        crypto_sign_edwards25519sha512batch_open_20,
        crypto_sign_edwards25519sha512batch_open_21,
        crypto_sign_edwards25519sha512batch_open_22,
        crypto_sign_edwards25519sha512batch_open_23,
        crypto_sign_edwards25519sha512batch_open_24,
        crypto_sign_edwards25519sha512batch_open_25,
        crypto_sign_edwards25519sha512batch_open_26,
        crypto_sign_edwards25519sha512batch_open_27,
        crypto_sign_edwards25519sha512batch_open_28,
        crypto_sign_edwards25519sha512batch_open_29,
        crypto_sign_edwards25519sha512batch_open_30,
        crypto_sign_edwards25519sha512batch_open_31,
        crypto_sign_edwards25519sha512batch_open_32,
        crypto_sign_edwards25519sha512batch_open_33,
        crypto_sign_edwards25519sha512batch_open_34,
        crypto_sign_edwards25519sha512batch_open_35,
        crypto_sign_edwards25519sha512batch_open_36,
        crypto_sign_edwards25519sha512batch_open_37,
        crypto_sign_edwards25519sha512batch_open_38,
        crypto_sign_edwards25519sha512batch_open_39,
        crypto_sign_edwards25519sha512batch_open_40,
        crypto_sign_edwards25519sha512batch_open_41,
        crypto_sign_edwards25519sha512batch_open_42,
        crypto_sign_edwards25519sha512batch_open_43,
        crypto_sign_edwards25519sha512batch_open_44,
        crypto_sign_edwards25519sha512batch_open_45,
        crypto_sign_edwards25519sha512batch_open_46,
        crypto_sign_edwards25519sha512batch_open_47,
        crypto_sign_edwards25519sha512batch_open_48,
        crypto_sign_edwards25519sha512batch_open_49,
        crypto_sign_edwards25519sha512batch_open_50*/
    )
);

pub fn crypto_sign_edwards25519sha512batch_open_wrapper(dis: u32) -> CString {
    
    unsafe {
        let plain_size = 100;
        let  plain_len: *mut u64 = 0 as *mut u64;
        let mut plain =  libc::malloc(plain_size) as *mut libc::c_uchar; // WATCH OUT, regular Vec::allocate does not work
        
        let mut sinature =  libc::malloc(plain_size) as *mut libc::c_uchar; // WATCH OUT, regular Vec::allocate does not work

        let to_encode3 = CString::new("HelloWorld!").expect("CString::new failed");// publc key
        let to_encode_ptr3 = to_encode3.as_ptr() as *mut u8;

        dynamic_diversification_body!(
            crypto_sign_edwards25519sha512batch_open(plain, plain_len, sinature, plain_size as u64, to_encode_ptr3),
        );

        CString::from_raw(plain as  *mut libc::c_char)
    }
}



multiple_import!(
    (   
        pk: *mut libc::c_uchar,
        sk: *mut libc::c_uchar) -> i32, 
    (
        crypto_sign_edwards25519sha512batch_keypair, 
    )
);

pub fn crypto_sign_edwards25519sha512batch_keypair_wrapper(dis: u32) -> i32 {
    
    unsafe {
       
        let to_encode3 = CString::new("HelloWorld!").expect("CString::new failed");// publc key
        let to_encode_ptr3 = to_encode3.as_ptr() as *mut u8;

        let to_encode4 = CString::new("HelloWorld!").expect("CString::new failed");// publc key
        let to_encode_ptr4 = to_encode3.as_ptr() as *mut u8;

        dynamic_diversification_body!(
            crypto_sign_edwards25519sha512batch_keypair(to_encode_ptr3, to_encode_ptr4),
        )
    }
}



// Return result, elapsed
pub fn main_crypto_sign_edwards25519sha512batch_open(hashValue: u64) -> (CString, u128, u32){

    let now = std::time::Instant::now();
   

    let DIS = (hashValue % 1) as u32;
    (crypto_sign_edwards25519sha512batch_open_wrapper(DIS), now.elapsed().as_nanos(), DIS)
}



// Return result, elapsed
pub fn main_crypto_sign_edwards25519sha512batch_keypair(hashValue: u64) -> (u32, u128, u32){

    let now = std::time::Instant::now();
   

    let DIS = (hashValue % 1) as u32;
    (crypto_sign_edwards25519sha512batch_keypair_wrapper(DIS), now.elapsed().as_nanos(), DIS)
}
