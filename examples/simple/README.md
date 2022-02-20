# Example

We pass the following rust program to MEWE

```rust
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
```

1. Run `source mewe.sh` in the root folder of the repo
2. Run `mewerustc --llvm-version 12` (version 13 depends on your system config).
3. Run `wasmer main.wasm` to execute the wasm32-wasi file ;)