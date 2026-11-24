fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, Int32Builder, ListBuilder};
        let mut builder = ListBuilder::new(Int32Builder::new());
        builder.values().append_value(2);
        builder.values().append_null();
        builder.append(true);
        builder.append(true);
        builder.append(false);
        let lists = builder.finish();
        assert_eq!(lists.len(), 3);
        assert_eq!(lists.value_length(0), 2);
        assert_eq!(lists.value_length(1), 0);
        assert!(lists.is_null(2));
    }

    {
        use arrow::array::{Array, StringArray};
        let values = StringArray::from(vec!["first", "middle", "last"]);
        let slice = values.slice(1, 1);
        let typed = slice.as_any().downcast_ref::<StringArray>().unwrap();
        assert_eq!(typed.len(), 1);
        assert_eq!(typed.value(0), "middle");
    }

    {
        // Task 2: Guided modification
        use arrow::array::{Array, AsArray, Int32Builder, ListBuilder};
        use arrow::datatypes::Int32Type;
        let mut builder = ListBuilder::new(Int32Builder::new());
        builder.values().append_value(2);
        builder.values().append_null();
        builder.append(true);
        builder.append(true);
        builder.append(false);
        builder.values().append_value(7);
        builder.values().append_value(9);
        builder.append(true);
        let lists = builder.finish();
        assert_eq!(lists.len(), 4);
        assert!(lists.is_valid(3));
        assert_eq!(lists.value_length(3), 2);
        let added = lists.value(3);
        let children = added.as_primitive::<Int32Type>();
        assert_eq!(children.null_count(), 0);
        assert_eq!(children.values().to_vec(), vec![7, 9]);
    }

    {
        // Task 3: Independent construction
        use arrow::array::{Array, Int32Builder, ListBuilder};
        let rows = [vec![1, 2], vec![], vec![3]];
        let mut builder = ListBuilder::new(Int32Builder::new());
        for row in &rows {
            for value in row {
                builder.values().append_value(*value);
            }
            builder.append(true);
        }
        let lists = builder.finish();
        assert_eq!(lists.len(), 3);
        let lengths: Vec<i32> = (0..3).map(|i| lists.value_length(i)).collect();
        assert_eq!(lengths, [2, 0, 1]);
    }

    {
        // Task 5: Boundary evidence
        use arrow::array::{Array, StringArray};
        let values = StringArray::from(vec![Some("first"), None, Some("middle"), Some("last")]);
        let nothing = values.slice(2, 0);
        assert_eq!((nothing.len(), nothing.null_count()), (0, 0));
        let tail = values.slice(1, 3);
        let typed = tail.as_any().downcast_ref::<StringArray>().unwrap();
        assert_eq!(typed.len(), 3);
        assert!(typed.is_null(0));
        assert_eq!(typed.value(1), "middle");
        assert_eq!(
            typed.iter().collect::<Vec<_>>(),
            vec![None, Some("middle"), Some("last")]
        );
        let end = values.slice(values.len(), 0);
        assert!(end.is_empty());
    }
    println!("rust-041: passed");
    Ok(())
}
