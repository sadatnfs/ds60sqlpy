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
    println!("rust-042: passed");
    Ok(())
}
