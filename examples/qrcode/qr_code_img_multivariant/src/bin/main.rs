
use std::path::Path;
extern crate lodepng;

extern "Rust" {
    pub fn run_qr(code: String) -> (Vec<u8>, usize);
}

pub fn main() {
    let (img, output_size) = unsafe { run_qr(String::from("Hello world form MEWE !")) };
    
    let path = &Path::new("write_test.png");

    // Use number of QR modules to specify the image dimensions.
    if let Err(e) = lodepng::encode_file(path, &img, output_size, output_size, lodepng::LCT_RGB, 8) {
        panic!("failed to write png: {:?}", e);
    }

    println!("Written to {}", path.display());
}