

pub fn main() {
    let img = unsafe { qrcode_simple::run_qr_str(String::from("Hello world form MEWE !")) };
    
    println!("{}", img);
    //println!("Hej !");
}