pub fn cat<T: Clone>(a: &[T], b: &[T]) -> Vec<T> {
	[a, b].concat()
}