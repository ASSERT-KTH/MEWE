extern "Rust" {
    pub fn {{name}}();
}

pub fn main(){
    unsafe { {{name}}() };
}