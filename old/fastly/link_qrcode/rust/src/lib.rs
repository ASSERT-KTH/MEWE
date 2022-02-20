use qrcode::{EcLevel, QrCode, Version, Color};

#[no_mangle]
pub extern "Rust" fn run_qr(code: String) -> Vec<u8>{
    let code = QrCode::new(code).unwrap();
    // Render the bits into an image.
    let output_size = code.width();
    
    let imgdata: Vec<u8> = code.into_vec()
    .into_iter()
    .flat_map(|b| {
      if b { vec![0u8; 3] } else { vec![255u8; 3] }
    })
    .collect();

    imgdata
}


#[no_mangle]
pub extern "Rust" fn run_qr_str(code: String) -> String{
    let code = QrCode::new(code).unwrap();
    // Render the bits into an image.
    code.render::<char>().quiet_zone(false).module_dimensions(2, 1).build()
}


#[no_mangle]
pub extern "Rust" fn test1() -> i32 {
  return 42;
}