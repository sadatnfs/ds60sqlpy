use arrow::array::{Array, Int32Array};
fn main() {
    let values = Int32Array::from(vec![Some(20), None, Some(22)]);
    assert_eq!(values.len(), 3);
    assert!(values.is_null(1));
    assert_eq!(values.value(0) + values.value(2), 42);
}
