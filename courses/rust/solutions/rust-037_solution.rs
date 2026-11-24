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

    {
        // Task 2: Guided modification
        use arrow::array::{Array, Int32Array};
        let values = Int32Array::from(vec![2, 4, 6, 8]);
        assert_eq!(values.len(), 4);
        let fourth: i32 = values.value(3);
        assert_eq!(fourth, 8);
        assert!(values.is_valid(3));
        assert_eq!(values.values().iter().sum::<i32>(), 20);
    }

    {
        // Task 3: Independent construction
        use arrow::array::{Array, Int32Array, StringArray};
        let names = StringArray::from(vec!["pear", "apple", "fig"]);
        let quantities = Int32Array::from(vec![2, 5, 1]);
        assert_eq!(names.len(), quantities.len());
        assert_eq!(names.value(1), "apple");
        assert_eq!(quantities.value(1), 5);
    }

    {
        // Task 5: Boundary evidence
        use arrow::array::{Array, Int32Array, StringArray};
        let empty = Int32Array::from(Vec::<i32>::new());
        assert_eq!((empty.len(), empty.null_count()), (0, 0));
        assert!(empty.is_empty());
        assert_eq!(empty.iter().count(), 0);
        let labels = StringArray::from(vec!["é", "日本", "a"]);
        assert_eq!(labels.len(), 3);
        assert_eq!(labels.value(0), "é");
        assert_eq!(
            (labels.value(0).len(), labels.value(0).chars().count()),
            (2, 1)
        );
        assert_eq!(
            (labels.value_length(1), labels.value(1).chars().count()),
            (6, 2)
        );
    }
    println!("rust-037: passed");
    Ok(())
}
