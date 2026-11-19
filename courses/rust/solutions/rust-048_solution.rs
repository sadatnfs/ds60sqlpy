fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, Int32Array};
        let values = Int32Array::from(vec![Some(2), None, Some(3), Some(-1), Some(0)]);
        let accepted: Vec<_> = values
            .iter()
            .flatten()
            .filter(|value| *value >= 0)
            .collect();
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

    {
        // Task 3: Independent construction
        use arrow::array::{ArrayRef, Int32Array, StringArray};
        use arrow::ipc::{reader::StreamReader, writer::StreamWriter};
        use arrow::record_batch::RecordBatch;
        use std::sync::Arc;
        let names: ArrayRef = Arc::new(StringArray::from(vec!["apple", "pear"]));
        let totals: ArrayRef = Arc::new(Int32Array::from(vec![5, 2]));
        let report = RecordBatch::try_from_iter(vec![("name", names), ("total", totals)])?;
        let mut bytes = Vec::new();
        {
            let mut writer = StreamWriter::try_new(&mut bytes, &report.schema())?;
            writer.write(&report)?;
            writer.finish()?;
        }
        let mut reader = StreamReader::try_new(std::io::Cursor::new(bytes), None)?;
        assert_eq!(reader.next().unwrap()?, report);
        assert!(reader.next().is_none());
    }
    println!("rust-048: passed");
    Ok(())
}
