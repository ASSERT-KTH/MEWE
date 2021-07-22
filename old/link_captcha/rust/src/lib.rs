//mod zxing;

//use zxing::*;



use captcha::Captcha;
use captcha::filters::{Noise, Wave, Dots};

#[no_mangle]
pub extern "Rust" fn get_captcha() -> Vec<u8>{
  Captcha::new()
    .add_chars(5)
    .apply_filter(Noise::new(0.4))
    .apply_filter(Wave::new(2.0, 20.0).horizontal())
    .apply_filter(Wave::new(2.0, 20.0).vertical())
    .view(220, 120)
    .apply_filter(Dots::new(15))
    .as_png().unwrap()
}
