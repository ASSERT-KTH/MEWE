use rand::RngCore;


#[warn(non_snake_case)]
#[no_mangle]
pub fn discriminate(total: i32) -> i32 {

    let popId = (rand::thread_rng().next_u32()%1000000u32) as i32;
    let r = (popId)%total;
    r
}

extern "Rust" {
    pub fn {{name}}();
}

pub fn main(){
    unsafe { {{name}}() };
}