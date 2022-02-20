/* 
extern "Rust" {
    pub fn run_qr(code: String) -> Vec<u8>;
    pub fn run_qr_str(code: String) ->String;
}
pub fn main(){
   let r =  unsafe { run_qr_str(String::from("Hello world!")) };

   println!("{}", r);
}
*/


extern "Rust" {
    pub fn internal_main();
}
pub fn main(){
    unsafe { internal_main() };
}