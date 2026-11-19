fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::sync::Arc;
        use arrow::array::{ArrayRef, Int32Array, StringArray};
        use arrow::datatypes::{DataType, Field, Schema};
        use arrow::record_batch::RecordBatch;
        let schema = Arc::new(Schema::new(vec![
            Field::new("name", DataType::Utf8, false),
            Field::new("quantity", DataType::Int32, false),
        ]));
        let columns: Vec<ArrayRef> = vec![
            Arc::new(StringArray::from(vec!["pear", "apple"])),
            Arc::new(Int32Array::from(vec![2, 3])),
        ];
        let batch = RecordBatch::try_new(schema, columns)?;
        assert_eq!((batch.num_rows(), batch.num_columns()), (2, 2));
        assert_eq!(
            batch
                .column(0)
                .as_any()
                .downcast_ref::<arrow::array::StringArray>()
                .unwrap()
                .value(0),
            "pear"
        );
    }

    {
        use std::sync::Arc;
        use arrow::array::{ArrayRef, Int32Array};
        use arrow::datatypes::{DataType, Field, Schema};
        use arrow::record_batch::RecordBatch;
        let schema = Arc::new(Schema::new(vec![
            Field::new("a", DataType::Int32, false),
            Field::new("b", DataType::Int32, false),
        ]));
        let columns: Vec<ArrayRef> = vec![
            Arc::new(Int32Array::from(vec![1, 2])),
            Arc::new(Int32Array::from(vec![3])),
        ];
        assert!(RecordBatch::try_new(schema, columns).is_err());
    }

    {
        // Task 3: Independent construction
        use arrow::array::{ArrayRef, Int32Array, StringArray};
        use arrow::datatypes::{DataType, Field, Schema};
        use arrow::record_batch::RecordBatch;
        use std::sync::Arc;
        let rows = [("pear", 2), ("apple", -1), ("fig", 4)];
        let valid: Vec<_> = rows.iter().filter(|(_, qty)| *qty >= 0).collect();
        let names: Vec<&str> = valid.iter().map(|(name, _)| *name).collect();
        let quantities: Vec<i32> = valid.iter().map(|(_, qty)| *qty).collect();
        let schema = Schema::new(vec![
            Field::new("name", DataType::Utf8, false),
            Field::new("quantity", DataType::Int32, false),
        ]);
        let columns: Vec<ArrayRef> = vec![
            Arc::new(StringArray::from(names)),
            Arc::new(Int32Array::from(quantities)),
        ];
        let batch = RecordBatch::try_new(Arc::new(schema), columns)?;
        assert_eq!((batch.num_rows(), batch.num_columns()), (2, 2));
    }
    println!("rust-039: passed");
    Ok(())
}
