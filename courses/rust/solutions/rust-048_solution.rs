

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, Int32Array};
        let values = Int32Array::from(vec![Some(2), None, Some(3), Some(-1), Some(0)]);
        let accepted: Vec<_> = values.iter().flatten().filter(|value| *value >= 0).collect();
        assert_eq!(accepted.iter().sum::<i32>(), 5);
        assert_eq!(accepted.len(), 3);
        assert_eq!(values.null_count(), 1);
        assert_eq!(values.len() - values.null_count() - accepted.len(), 1);
    }

    {
        use arrow::array::{Array, Int32Array};
        let empty = Int32Array::from(Vec::<Option<i32>>::new());
        let missing = Int32Array::from(vec![None::<i32>, None]);
        assert_eq!((empty.len(), empty.null_count()), (0, 0));
        assert_eq!((missing.len(), missing.null_count()), (2, 2));
    }
    println!("rust-048: passed");
    Ok(())
}
