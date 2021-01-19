

pub struct Wat2MirConfig {
	pub convert_end_to_mir: bool,
	pub skip: u32,
	pub leave: u32,
 }
 

 impl Wat2MirConfig {
	 pub fn new() -> Wat2MirConfig {
		Wat2MirConfig {
			convert_end_to_mir: true,
			skip: 0,
			leave: 0
		 }
	 }
 }
 