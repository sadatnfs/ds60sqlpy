

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, Int32Array};
        let values = Int32Array::from(vec![2, 4, 6]);
        assert_eq!(values.len(), 3);
        assert_eq!(values.value(1), 4);
        assert_eq!(values.null_count(), 0);
    }

    {
        use arrow::array::{Array, StringArray};
        let labels = StringArray::from(vec!["a", "longer", "é"]);
        assert_eq!(labels.len(), 3);
        assert_eq!(labels.value(1), "longer");
        assert_eq!(labels.value(2), "é");
    }
    println!("rust-037: passed");
    Ok(())
}
