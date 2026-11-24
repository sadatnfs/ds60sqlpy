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
        // Task 2: Guided modification
        use arrow::array::{Array, AsArray};
        use arrow::datatypes::{DataType, Field, Schema};
        use std::sync::Arc;
        let schema = Arc::new(Schema::new(vec![
            Field::new("name", DataType::Utf8, false),
            Field::new("quantity", DataType::Int32, false),
        ]));
        let input = b"name,quantity\n\"pear, ripe\",2\napple,3\n";
        let mut reader = arrow::csv::ReaderBuilder::new(schema)
            .with_header(true)
            .build(std::io::Cursor::new(&input[..]))?;
        let batch = reader.next().unwrap()?;
        let names = batch.column(0).as_string::<i32>();
        assert_eq!(batch.num_rows(), 2);
        assert_eq!(names.value(0), "pear, ripe");
        assert_eq!(names.len(), 2);
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

    {
        // Task 5: Boundary evidence
        use arrow::array::Array;
        use arrow::datatypes::{DataType, Field, Schema};
        use std::io::Cursor;
        use std::sync::Arc;
        let schema = Arc::new(Schema::new(vec![
            Field::new("name", DataType::Utf8, false),
            Field::new("quantity", DataType::Int32, true),
        ]));
        let bad = b"name,quantity\npear,2\nfig,x\n";
        let mut reader = arrow::csv::ReaderBuilder::new(schema.clone())
            .with_header(true)
            .build(Cursor::new(&bad[..]))?;
        assert!(reader.next().unwrap().is_err());
        let input = b"name,quantity\npear,2\nfig,\nkiwi,4\n";
        let reader = arrow::csv::ReaderBuilder::new(schema)
            .with_header(true)
            .with_batch_size(2)
            .build(Cursor::new(&input[..]))?;
        let mut sizes = Vec::new();
        let mut nulls = 0;
        for batch in reader {
            let batch = batch?;
            sizes.push(batch.num_rows());
            nulls += batch.column(1).null_count();
        }
        assert_eq!(sizes, vec![2, 1]);
        assert_eq!(nulls, 1);
    }
    println!("rust-043: passed");
    Ok(())
}
