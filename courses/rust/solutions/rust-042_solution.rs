fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::sync::Arc;
        use std::io::Cursor;
        use arrow::array::{ArrayRef, Int32Array};
        use arrow::record_batch::RecordBatch;
        use arrow::ipc::{reader::StreamReader, writer::StreamWriter};
        let batch = RecordBatch::try_from_iter(vec![(
            "quantity",
            Arc::new(Int32Array::from(vec![2, 3])) as ArrayRef,
        )])?;
        let mut bytes = Vec::new();
        {
            let mut writer = StreamWriter::try_new(&mut bytes, &batch.schema())?;
            writer.write(&batch)?;
            writer.finish()?;
        }
        let mut reader = StreamReader::try_new(Cursor::new(bytes), None)?;
        let restored = reader.next().unwrap()?;
        assert_eq!(restored, batch);
        assert!(reader.next().is_none());
    }

    {
        use std::io::Cursor;
        use arrow::ipc::reader::StreamReader;
        assert!(StreamReader::try_new(Cursor::new(vec![1_u8, 2, 3]), None).is_err());
    }

    {
        // Task 2: Guided modification
        use arrow::array::{ArrayRef, Int32Array};
        use arrow::ipc::{reader::StreamReader, writer::StreamWriter};
        use arrow::record_batch::RecordBatch;
        use std::sync::Arc;
        let first = RecordBatch::try_from_iter(vec![(
            "quantity",
            Arc::new(Int32Array::from(vec![2, 3])) as ArrayRef,
        )])?;
        let second = RecordBatch::try_from_iter(vec![(
            "quantity",
            Arc::new(Int32Array::from(vec![5])) as ArrayRef,
        )])?;
        assert_eq!(first.schema(), second.schema());
        let mut bytes = Vec::new();
        {
            let mut writer = StreamWriter::try_new(&mut bytes, &first.schema())?;
            writer.write(&first)?;
            writer.write(&second)?;
            writer.finish()?;
        }
        let reader = StreamReader::try_new(std::io::Cursor::new(bytes), None)?;
        let mut batches = 0;
        let mut rows = 0;
        for batch in reader {
            let batch = batch?;
            batches += 1;
            rows += batch.num_rows();
        }
        assert_eq!((batches, rows), (2, 3));
    }

    {
        // Task 3: Independent construction
        use arrow::array::{Array, ArrayRef, Int32Array};
        use arrow::ipc::{reader::StreamReader, writer::StreamWriter};
        use arrow::record_batch::RecordBatch;
        use std::sync::Arc;
        let values: ArrayRef = Arc::new(Int32Array::from(vec![Some(4), None, Some(6)]));
        let batch = RecordBatch::try_from_iter(vec![("qty", values)])?;
        let mut bytes = Vec::new();
        {
            let mut writer = StreamWriter::try_new(&mut bytes, &batch.schema())?;
            writer.write(&batch)?;
            writer.finish()?;
        }
        let mut reader = StreamReader::try_new(std::io::Cursor::new(bytes), None)?;
        let restored = reader.next().unwrap()?;
        assert_eq!(restored.column(0).null_count(), 1);
        assert_eq!(restored, batch);
    }

    {
        // Task 5: Boundary evidence
        use arrow::array::{ArrayRef, Int32Array};
        use arrow::ipc::{reader::StreamReader, writer::StreamWriter};
        use arrow::record_batch::RecordBatch;
        use std::io::Cursor;
        use std::sync::Arc;
        assert!(StreamReader::try_new(Cursor::new(Vec::<u8>::new()), None).is_err());
        assert!(StreamReader::try_new(Cursor::new(vec![0xFF_u8; 8]), None).is_err());
        let template = RecordBatch::try_from_iter(vec![(
            "quantity",
            Arc::new(Int32Array::from(vec![1])) as ArrayRef,
        )])?;
        let schema = template.schema();
        let mut bytes = Vec::new();
        {
            let mut writer = StreamWriter::try_new(&mut bytes, &schema)?;
            writer.write(&template.slice(0, 0))?;
            writer.finish()?;
        }
        let mut reader = StreamReader::try_new(Cursor::new(bytes), None)?;
        assert_eq!(reader.schema(), schema);
        let empty = reader.next().unwrap()?;
        assert_eq!(empty.num_rows(), 0);
        assert!(reader.next().is_none());
    }
    println!("rust-042: passed");
    Ok(())
}
