
extern "Rust" {
    pub fn run_qr(code: String) -> Vec<u8>;
    pub fn run_qr_str(code: String) ->String;
}