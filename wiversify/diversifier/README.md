## Procedural macros for diversification

> Procedural macros allow you to run code at compile time that operates over Rust syntax, both consuming and producing Rust syntax. You can sort of think of procedural macros as functions from an AST to another AST.

We create two main procedural macros in order to provide diversification in Rust code.

- Static diversifier: This macro receive several expressions separated by comma. At compilation time a random expression will be choose and injected in the final code. Next, how to use it

	```rs
	use diversifier::{static_diversification};

	static_diversification!(babbage1(), babbage2(), 42);

	```

You can run `cargo expand` to see which expression is injected at compilation time.

- Dynamic diversifier: This macro receive several expressions separated by comma. At compilation time a huge switch case (Rust `match` construction) template is created containing all the cases. The template operates on a `dis` (discrimator variable), ideally coming from a random call. Following an example of usage.

	```rs
	use diversifier::{dynamic_diversification};

	dynamic_diversification!((
		unsafe{
			babbage1()
		}, 
		unsafe{
			babbage2()
		}, 
		1, 
		2) -> i32, "myfunction");

	```


	This macro will create the following code:


	```rs

	myfunction(dis: i32) -> i32 {

		match dis {
			0 => unsafe{
					babbage1()
				},
			1 => unsafe{
					babbage2()
				},
			2 => 1,
			3 => 2,
			_ => panic!("Dont know what to do with {{}} value", dis)
		}

	}

	```