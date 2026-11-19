fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::sync::Arc;
        use std::io::Cursor;
        use arrow::datatypes::{DataType, Field, Schema};
        let schema = Arc::new(Schema::new(vec![
            Field::new("name", DataType::Utf8, false),
            Field::new("quantity", DataType::Int32, false),
        ]));
        let input = b"name,quantity\npear,2\napple,3\n";
        let mut reader = arrow::csv::ReaderBuilder::new(schema)
            .with_header(true)
            .with_batch_size(8)
            .build(Cursor::new(input))?;
        let batch = reader.next().unwrap()?;
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
        use std::io::Cursor;
        use arrow::array::Int32Array;
        use arrow::datatypes::{DataType, Field, Schema};
        let schema = Arc::new(Schema::new(vec![Field::new(
            "quantity",
            DataType::Int32,
            true,
        )]));
        let input = b"{\"quantity\":2}\n{\"quantity\":null}\n";
        let mut reader = arrow::json::ReaderBuilder::new(schema)
            .with_batch_size(8)
            .build(Cursor::new(input))?;
        let batch = reader.next().unwrap()?;
        let values = batch
            .column(0)
            .as_any()
            .downcast_ref::<Int32Array>()
            .unwrap();
        assert_eq!(values.iter().collect::<Vec<_>>(), vec![Some(2), None]);
    }

    {
        // Task 3: Independent construction
        use arrow::array::{Array, AsArray};
        use arrow::datatypes::{DataType, Field, Int32Type, Schema};
        use std::sync::Arc;
        let field = Field::new("quantity", DataType::Int32, true);
        let schema = Arc::new(Schema::new(vec![field]));
        let input = b"{\"quantity\":2}\n{\"quantity\":null}\n{\"quantity\":-1}\n";
        let mut reader = arrow::json::ReaderBuilder::new(schema).build(&input[..])?;
        let batch = reader.next().unwrap()?;
        let values = batch.column(0).as_primitive::<Int32Type>();
        let negative = values.iter().flatten().filter(|v| *v < 0).count();
        assert_eq!((values.len(), values.null_count(), negative), (3, 1, 1));
    }
    println!("rust-043: passed");
    Ok(())
}
