use qrcode::{EcLevel, QrCode, Version, Color};

#[no_mangle]
pub extern "Rust" fn run_qr_str(code: String) -> String{
    let code = QrCode::new(code).unwrap();
    // Render the bits into an image.
    code.render::<char>().quiet_zone(false).module_dimensions(2, 1).build()
}
