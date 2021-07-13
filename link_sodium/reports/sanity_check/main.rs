


extern "C" {
    pub fn sodium_bin2base64(b64: *mut libc::c_char,
        b64_maxlen: usize,
        bin: *const libc::c_uchar,
        bin_len: usize,
        variant: libc::c_int) -> *mut libc::c_char;
}


fn main(){

}