//mod zxing;

//use zxing::*;
extern crate image;
extern crate num_complex;

use image::{GenericImage, GenericImageView, ImageBuffer, RgbImage, DynamicImage};
use image::png::PngEncoder;

#[no_mangle]
pub extern "Rust" fn generate_fractal() -> (Vec<u8>, u32, u32){
  let imgx = 800;
    let imgy = 800;

    let scalex = 3.0 / imgx as f32;
    let scaley = 3.0 / imgy as f32;

    // Create a new ImgBuf with width: imgx and height: imgy
    let mut imgbuf = image::ImageBuffer::new(imgx, imgy);

    // Iterate over the coordinates and pixels of the image
    for (x, y, pixel) in imgbuf.enumerate_pixels_mut() {
        let r = (0.3 * x as f32) as u8;
        let b = (0.3 * y as f32) as u8;
        *pixel = image::Rgb([r, 0, b]);
    }

    // A redundant loop to demonstrate reading image data
    for x in 0..imgx {
        for y in 0..imgy {
            let cx = y as f32 * scalex - 1.5;
            let cy = x as f32 * scaley - 1.5;

            let c = num_complex::Complex::new(-0.4, 0.6);
            let mut z = num_complex::Complex::new(cx, cy);

            let mut i = 0;
            while i < 255 && z.norm() <= 2.0 {
                z = z * z + c;
                i += 1;
            }

            let pixel = imgbuf.get_pixel_mut(x, y);
            let image::Rgb(data) = *pixel;
            *pixel = image::Rgb([data[0], i as u8, data[2]]);
        }
    }

    let dims = imgbuf.dimensions();
    // Save the image as “fractal.png”, the format is deduced from the path
    (imgbuf.into_raw(), dims.0, dims.1)
}


// Following functions are wrappers to provide bcs to MEWE
#[no_mangle]
pub extern "Rust" fn flipv_image(img: DynamicImage) -> DynamicImage {
  img.flipv()
}

#[no_mangle]
pub extern "Rust" fn fliph_image(img: DynamicImage) -> DynamicImage {
  img.fliph()
}

#[no_mangle]
pub extern "Rust" fn blur_image(img: DynamicImage) -> DynamicImage {
  img.blur(10.0)
}

#[no_mangle]
pub extern "Rust" fn crop_image(img: &mut DynamicImage) -> DynamicImage {
  img.crop(0,0,100,100)
}

#[no_mangle]
pub extern "Rust" fn grayscale_image(img: &mut DynamicImage) -> DynamicImage {
  img.grayscale()
}


#[no_mangle]
pub extern "Rust" fn invert_image(img: &mut DynamicImage) -> () {
  img.invert()
}


#[no_mangle]
pub extern "Rust" fn rotate90_image(img: DynamicImage) -> DynamicImage {
  img.rotate90()
}


#[no_mangle]
pub extern "Rust" fn unsharpen_image(img: DynamicImage) -> DynamicImage {
  img.unsharpen(0.2, 100)
}