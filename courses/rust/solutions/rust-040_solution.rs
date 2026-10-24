fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{BooleanArray, Int32Array};
        let values = Int32Array::from(vec![2, 4, 6]);
        let mask = BooleanArray::from(vec![true, false, true]);
        let result = arrow::compute::filter(&values, &mask)?;
        let typed = result.as_any().downcast_ref::<Int32Array>().unwrap();
        assert_eq!(typed.iter().collect::<Vec<_>>(), vec![Some(2), Some(6)]);
    }

    {
        use arrow::array::{Int32Array, UInt32Array};
        let values = Int32Array::from(vec![2, 4, 6]);
        let indices = UInt32Array::from(vec![2, 0, 2]);
        let result = arrow::compute::take(&values, &indices, None)?;
        let typed = result.as_any().downcast_ref::<Int32Array>().unwrap();
        assert_eq!(
            typed.iter().collect::<Vec<_>>(),
            vec![Some(6), Some(2), Some(6)]
        );
    }
    println!("rust-040: passed");
    Ok(())
}
