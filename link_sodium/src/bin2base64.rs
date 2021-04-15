
#[macro_use]
use diversifier::{static_diversification,dynamic_diversification_body,  dynamic_diversification, multiple_import, expand };
use std::ffi::CString;



multiple_import!(
    (
        b64: *mut libc::c_char,
        b64_maxlen: usize,
        bin: *const libc::c_uchar,
        bin_len: usize,
        variant: libc::c_int) -> *mut libc::c_char, 
    (
        sodium_bin2base64,
        sodium_bin2base64_0_,
        sodium_bin2base64_1_,
        sodium_bin2base64_2_,
        sodium_bin2base64_3_,
        sodium_bin2base64_4_,
        sodium_bin2base64_5_,
        sodium_bin2base64_6_,
        sodium_bin2base64_7_,
        sodium_bin2base64_8_,
        sodium_bin2base64_9_,
        sodium_bin2base64_10_,
        sodium_bin2base64_11_,
        sodium_bin2base64_12_,
        sodium_bin2base64_13_,
        sodium_bin2base64_14_,
        sodium_bin2base64_15_,
        sodium_bin2base64_16_,
        sodium_bin2base64_17_,
        sodium_bin2base64_18_,
        sodium_bin2base64_19_,
        sodium_bin2base64_20_,
        sodium_bin2base64_21_,
        sodium_bin2base64_22_,
        sodium_bin2base64_23_,
        sodium_bin2base64_24_,
        sodium_bin2base64_25_,
        sodium_bin2base64_26_,
        sodium_bin2base64_27_,
        sodium_bin2base64_28_,
        sodium_bin2base64_29_,
        sodium_bin2base64_30_,
        sodium_bin2base64_31_,
        sodium_bin2base64_32_,
        sodium_bin2base64_33_,
        sodium_bin2base64_34_,
        sodium_bin2base64_35_,
        sodium_bin2base64_36_,
        sodium_bin2base64_37_,
        sodium_bin2base64_38_,
        sodium_bin2base64_39_,
        sodium_bin2base64_40_
    )
);

pub fn sodium_bin2base64_wrapper(dis: u32, size: usize, bin: *const libc::c_uchar, bin_len: usize) -> CString{
    unsafe {
        let mut buf =  libc::malloc(size) as *mut libc::c_char; // WATCH OUT, regular Vec::allocate does not work
        //let r = sodium_bin2base64(buf, size, bin, bin_len, 5 ); // 5 for url safe

        dynamic_diversification_body!(
            sodium_bin2base64(buf, size, bin, bin_len, 5),
            sodium_bin2base64_0_ (buf, size, bin, bin_len, 5),
            sodium_bin2base64_1_ (buf, size, bin, bin_len, 5),
            sodium_bin2base64_2_ (buf, size, bin, bin_len, 5),
            sodium_bin2base64_3_ (buf, size, bin, bin_len, 5),
            sodium_bin2base64_4_ (buf, size, bin, bin_len, 5),
            sodium_bin2base64_5_ (buf, size, bin, bin_len, 5),
            sodium_bin2base64_6_ (buf, size, bin, bin_len, 5),
            sodium_bin2base64_7_ (buf, size, bin, bin_len, 5),
            sodium_bin2base64_8_ (buf, size, bin, bin_len, 5),
            sodium_bin2base64_9_ (buf, size, bin, bin_len, 5),
            sodium_bin2base64_10_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_11_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_12_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_13_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_14_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_15_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_16_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_17_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_18_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_19_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_20_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_21_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_22_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_23_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_24_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_25_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_26_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_27_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_28_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_29_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_30_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_31_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_32_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_33_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_34_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_35_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_36_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_37_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_38_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_39_(buf, size, bin, bin_len, 5),
            sodium_bin2base64_40_(buf, size, bin, bin_len, 5),
        );
        CString::from_raw(buf)
    }
}

// Return result, elapsed
pub fn main_bin2base64(hashValue: u64) -> (CString, u128, u32){

    let now = std::time::Instant::now();

    let to_encode = CString::new("HelloWorld!").expect("CString::new failed");
    let size = 20 as usize;
    let to_encode_ptr = to_encode.as_ptr() as *mut u8;

    let DIS = (hashValue % 42) as u32;

    (sodium_bin2base64_wrapper(DIS, 50, to_encode_ptr, size), now.elapsed().as_nanos(), DIS)
}


/*,
            */