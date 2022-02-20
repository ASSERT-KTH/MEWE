
#[no_mangle]
pub fn func(cond: bool, z: i32) -> i32 {
   let mut x = 0;
   let mut y  = 0;
   if (cond) {
      x = 3 * z;
      y = z;
   } else {
      x = 2 * z;
      y = 2 * z;
   }

   return x + y;
}

pub fn main() {
    
    println!("Result {}", func(true, 190));
}