

extern "Rust"
{
    pub fn run_qr_str(code: String) -> String;
} 

pub fn main() {
    let img = unsafe { run_qr_str(String::from("Hello world form MEWE !")) };
    
    println!("{}", img);
    //println!("Hej !");
}