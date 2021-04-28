#[macro_use]
use diversifier::{static_diversification,dynamic_diversification_body,  dynamic_diversification, multiple_import, expand };
use std::ffi::CString;

extern "C" {
    pub fn sodium_increment__n1(   
        n: *mut libc::c_char,
        nlen: usize) -> ();
}


pub fn sodium_increment_wrapper() -> (){
   
    let to_encode = CString::new("HelloWorld!").expect("CString::new failed");
    let size = 11 as usize;
    let to_encode_ptr = to_encode.as_ptr() as *mut i8;

    unsafe {
            sodium_increment__n1(to_encode_ptr, size)
    }
}

extern "C" {
    pub fn sodium_memcmp__n1(n: *mut libc::c_char,
        n1: *mut libc::c_char,
        nlen: usize) -> i32;
}


pub fn sodium_memcmp_wrapper() -> i32 {
   
    let to_encode = CString::new("HelloWorld!").expect("CString::new failed");
    let to_encode2 = CString::new("HelloWorld!").expect("CString::new failed");

    let size = 11 as usize;
    let to_encode_ptr = to_encode.as_ptr() as *mut i8;
    let to_encode_ptr2 = to_encode2.as_ptr() as *mut i8;

    unsafe {
        sodium_memcmp__n1(to_encode_ptr, to_encode_ptr2, size)
    }
}


extern "C" {
    pub fn sodium_is_zero__n1(n: *mut libc::c_char,
        nlen: usize) -> i32;
}


pub fn sodium_is_zero_wrapper() -> i32 {
   
    let to_encode = CString::new("HelloWorld!").expect("CString::new failed");

    let size = 11 as usize;
    let to_encode_ptr = to_encode.as_ptr() as *mut i8;

    unsafe {
            sodium_is_zero__n1(to_encode_ptr, size)
        
    }
}

extern "C" {
    pub fn sodium_add__n1(   n: *mut libc::c_char,
        n2: *mut libc::c_char,
        nlen: usize) -> ();
}

pub fn sodium_add_wrapper() -> () {
   
    let to_encode = CString::new("HelloWorld!").expect("CString::new failed");
    let to_encode2 = CString::new("HelloWorld!").expect("CString::new failed");

    let size = 11 as usize;
    let to_encode_ptr = to_encode.as_ptr() as *mut i8;
    let to_encode_ptr2 = to_encode2.as_ptr() as *mut i8;

    unsafe {
        sodium_add__n1(to_encode_ptr, to_encode_ptr2, size)
        
    };
}



extern "C" {
    pub fn sodium_free__n1(   n: *mut libc::c_char) -> ();
}


pub fn sodium_free_wrapper() -> () {
   
    unsafe {
        let to_encode = libc::malloc(100) as *mut libc::c_char;

        sodium_free__n1(to_encode)
    };
}

// Return result, elapsed
pub fn main_sodium_increment() -> (u32, u128){

    let now = std::time::Instant::now();
   
    sodium_increment_wrapper();
    (1, now.elapsed().as_nanos())
}



// Return result, elapsed
pub fn main_sodium_memcmp() -> (i32, u128){
    let now = std::time::Instant::now();
    (sodium_memcmp_wrapper(), now.elapsed().as_nanos())
}



// Return result, elapsed
pub fn main_sodium_is_zero() -> (i32, u128){
    let now = std::time::Instant::now();
    (sodium_is_zero_wrapper(), now.elapsed().as_nanos())
}

// Return result, elapsed
pub fn main_sodium_add() -> (i32, u128){
    let now = std::time::Instant::now();
    sodium_add_wrapper();
    (1, now.elapsed().as_nanos())
}


// Return result, elapsed
pub fn main_sodium_free() -> (i32, u128){
    let now = std::time::Instant::now();
    sodium_free_wrapper();
    (1, now.elapsed().as_nanos())
}