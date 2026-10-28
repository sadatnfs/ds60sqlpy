use arrow::array::{Array, Int64Array, StringArray};
use arrow::ipc::reader::StreamReader;
use arrow::ipc::writer::StreamWriter;
use std::io::{self, BufReader};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut reader = StreamReader::try_new(BufReader::new(io::stdin()), None)?;
    let schema = reader.schema();
    let mut writer = StreamWriter::try_new(io::stdout(), &schema)?;
    let mut rows = 0;
    for next in &mut reader {
        let batch = next?;
        rows += batch.num_rows();
        if rows > 3 || batch.num_columns() != 3 {
            return Err("Unexpected fixture size".into());
        }
        let ids = batch
            .column(0)
            .as_any()
            .downcast_ref::<Int64Array>()
            .ok_or("Expected int64 IDs")?;
        let regions = batch
            .column(1)
            .as_any()
            .downcast_ref::<StringArray>()
            .ok_or("Expected UTF8 regions")?;
        let amounts = batch
            .column(2)
            .as_any()
            .downcast_ref::<Int64Array>()
            .ok_or("Expected int64 amounts")?;
        if ids.values().as_ref() != [1, 2, 3] || regions.value(1) != "west" || !amounts.is_null(1) {
            return Err("Fixture values or null bitmap changed".into());
        }
        writer.write(&batch)?;
    }
    if rows != 3 {
        return Err("Expected exactly three rows".into());
    }
    writer.finish()?;
    eprintln!("Actual Rust Arrow reader/writer verified three rows and nulls");
    Ok(())
}
