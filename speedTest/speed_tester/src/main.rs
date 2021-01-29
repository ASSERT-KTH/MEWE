
#[macro_use]
extern crate log;
extern crate structopt;

use std::thread;
use std::time::Duration;


use structopt::StructOpt;

#[derive(StructOpt, Debug)]
#[structopt(name = "speedtester")]
pub struct Opt {

    #[structopt(long = "fastly-api-token")]
    fastly_api_token: Option<String>,

    /*
    /// Input wasm file
    #[structopt(name = "input", parse(from_os_str))]
    input: PathBuf,

    /// Output bc file
    #[structopt(short = "o", long = "output")]
    output: Option<String>,

    /// Force inlining of constant globals
    #[structopt(short = "i", long = "inline-constant-globals")]
    inline_constant_globals: bool,

    /// Allow unsafe instruction implementations that may be faster
    #[structopt(short = "u", long = "fast-unsafe-implementations")]
    use_fast_unsafe_implementations: bool,

    /// Don't generate native globals, let the runtime handle it
    #[structopt(long = "runtime-globals")]
    use_runtime_global_handling: bool,

    /// Set compilation target
    #[structopt(long = "target")]
    target: Option<String>,

    /// Set compilation data layout
    #[structopt(long = "layout")]
    layout: Option<String>,


    /// Generate rotl operations as pure math
    #[structopt(long = "expand-rot")]
    expand_rot: Option<bool>,
    */

}

fn main() {
    let opt = Opt::from_args();
    println!("Hello, world!");
}
