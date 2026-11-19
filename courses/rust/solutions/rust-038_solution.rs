fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, Int32Array};
        let values = Int32Array::from(vec![Some(0), None, Some(4)]);
        assert_eq!(values.null_count(), 1);
        assert!(values.is_valid(0) && values.is_null(1));
        assert_eq!(
            values.iter().collect::<Vec<_>>(),
            vec![Some(0), None, Some(4)]
        );
    }

    {
        use arrow::array::{Array, Float64Array};
        let values = Float64Array::from(vec![Some(f64::NAN), None, Some(2.0)]);
        assert_eq!(values.null_count(), 1);
        assert!(values.is_valid(0) && values.value(0).is_nan());
        assert_eq!(
            values
                .iter()
                .flatten()
                .filter(|value| value.is_finite())
                .count(),
            1
        );
    }

    {
        // Task 3: Independent construction
        use arrow::array::{Array, Float64Array};
        fn summary(values: &Float64Array) -> (usize, usize, usize) {
            let valid = values.len() - values.null_count();
            let finite = values.iter().flatten().filter(|v| v.is_finite()).count();
            (valid, values.null_count(), finite)
        }
        let values = Float64Array::from(vec![Some(1.5), None, Some(f64::NAN), Some(2.0)]);
        assert_eq!(summary(&values), (3, 1, 2));
    }
    println!("rust-038: passed");
    Ok(())
}
