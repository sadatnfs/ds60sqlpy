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

    {
        // Task 3: Independent construction
        use arrow::array::{ArrayRef, AsArray, BooleanArray, Int32Array, StringArray};
        use arrow::record_batch::RecordBatch;
        use std::sync::Arc;
        let names: ArrayRef = Arc::new(StringArray::from(vec!["pear", "fig", "kiwi"]));
        let qty: ArrayRef = Arc::new(Int32Array::from(vec![2, 0, 5]));
        let batch = RecordBatch::try_from_iter(vec![("name", names), ("qty", qty)])?;
        let mask = BooleanArray::from(vec![true, false, true]);
        let kept = arrow::compute::filter_record_batch(&batch, &mask)?;
        assert_eq!(kept.num_rows(), 2);
        let kept_names = kept.column(0).as_string::<i32>();
        assert_eq!(kept_names.value(1), "kiwi");
    }
    println!("rust-040: passed");
    Ok(())
}
