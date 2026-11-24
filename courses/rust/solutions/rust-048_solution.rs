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
        // Task 2: Guided modification
        use arrow::array::{Array, Int32Array};
        let input = [Some(2), None, Some(3), Some(-1), Some(0), Some(4)];
        let values = Int32Array::from(input.to_vec());
        let accepted: Vec<i32> = values
            .iter()
            .flatten()
            .filter(|value| *value >= 0)
            .collect();
        let (mut sum, mut kept, mut nulls, mut rejected) = (0, 0, 0, 0);
        for item in input {
            match item {
                None => nulls += 1,
                Some(value) if value < 0 => rejected += 1,
                Some(value) => {
                    sum += value;
                    kept += 1;
                }
            }
        }
        assert_eq!((accepted.iter().sum::<i32>(), accepted.len()), (sum, kept));
        assert_eq!((values.null_count(), rejected), (nulls, 1));
        assert_eq!((sum, kept, nulls, rejected), (9, 4, 1, 1));
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

    {
        // Task 5: Boundary evidence
        use arrow::array::{Array, Int32Array};
        fn report(values: &Int32Array) -> Result<(i32, usize, usize, usize), String> {
            let mut sum = 0_i32;
            let (mut accepted, mut rejected) = (0, 0);
            for value in values.iter().flatten() {
                if value < 0 {
                    rejected += 1;
                    continue;
                }
                sum = sum.checked_add(value).ok_or("total overflows i32")?;
                accepted += 1;
            }
            Ok((sum, accepted, values.null_count(), rejected))
        }
        assert_eq!(report(&Int32Array::from(Vec::<i32>::new()))?, (0, 0, 0, 0));
        assert_eq!(report(&Int32Array::from(vec![None, None]))?, (0, 0, 2, 0));
        assert_eq!(report(&Int32Array::from(vec![-1, -2]))?, (0, 0, 0, 2));
        assert!(report(&Int32Array::from(vec![i32::MAX, 1])).is_err());
        let parsed: Result<Vec<i32>, _> =
            ["2", "x"].iter().map(|text| text.parse::<i32>()).collect();
        assert!(parsed.is_err());
    }
    println!("rust-048: passed");
    Ok(())
}
