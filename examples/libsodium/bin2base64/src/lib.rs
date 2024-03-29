
#[macro_use]
use std::ffi::CString;


extern "C" {
    pub fn sodium_bin2base64(b64: *mut libc::c_char,
        b64_maxlen: usize,
        bin: *const libc::c_uchar,
        bin_len: usize,
        variant: libc::c_int) -> *mut libc::c_char;
}


pub fn sodium_bin2base64_wrapper(size: usize, bin: *const libc::c_uchar, bin_len: usize) -> CString{
    unsafe {
        let mut buf = vec![0i8;size];
        sodium_bin2base64(buf.as_mut_ptr(), size, bin, bin_len, 5);
        CString::from_raw(buf.as_mut_ptr())
    }
}


pub fn sodium_bin2base64_original_wrapper(size: usize, bin: *const libc::c_uchar, bin_len: usize) -> CString{
    unsafe {
        let mut buf = vec![0i8;size];
        sodium_bin2base64(buf.as_mut_ptr(), size, bin, bin_len, 5);
        CString::from_raw(buf.as_mut_ptr())
    }
}

pub fn main_bin2base64() -> (CString, u128){

    let to_encode = CString::new("El feliz murcielago ...!").expect("CString::new failed");
    let size = 20 as usize;
    let to_encode_ptr = to_encode.as_ptr() as *mut u8;

    let now = std::time::Instant::now();

    (sodium_bin2base64_wrapper(50, to_encode_ptr, size), now.elapsed().as_nanos())
}
