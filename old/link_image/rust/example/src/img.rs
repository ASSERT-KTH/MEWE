
use std::io::Cursor;
use image::DynamicImage;
use image::png::{PngEncoder, PngDecoder};
use image::io::Reader as ImageReader;
use std::io::Write;

extern "Rust" {
    pub fn generate_fractal() -> (Vec<u8>, u32, u32);

    // Following functions are wrappers to provide bcs to MEWE
    pub fn flipv_image(img: DynamicImage) -> DynamicImage;

    pub fn fliph_image(img: DynamicImage) -> DynamicImage;

    pub fn blur_image(img: DynamicImage) -> DynamicImage ;

    pub fn crop_image(img: &mut DynamicImage) -> DynamicImage;

    pub fn grayscale_image(img: &mut DynamicImage) -> DynamicImage;


    pub fn invert_image(img: &mut DynamicImage) -> ();

    pub fn rotate90_image(img: DynamicImage) -> DynamicImage;

    pub fn unsharpen_image(img: DynamicImage) -> DynamicImage;

}


pub fn encode_img(buf: Vec<u8>, width: u32, height: u32) -> Vec<u8>{

    let mut buffer = Vec::new();
    PngEncoder::new(buffer.by_ref())
    .encode(
        &buf,
        width,
        height,
        <image::Rgb<u8> as image::Pixel>::color_type(),
    )
    .unwrap();
    buffer
  }



  pub fn encode_dynimg(img: DynamicImage) -> Vec<u8>{

    let mut buffer = Vec::new();
    img.write_to(&mut buffer, image::ImageOutputFormat::Png);
    
    buffer
  }


pub fn decode_img(buf: Vec<u8>) -> DynamicImage{
    let reader = ImageReader::with_format(Cursor::new(buf), image::ImageFormat::Png);
    reader.decode().unwrap()
}