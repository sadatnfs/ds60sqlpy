fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = [1_i32, 2, 3, 4, 5];
        let mut total = 0;
        let mut rows = 0;
        for batch in values.chunks(2) {
            rows += batch.len();
            total += batch.iter().sum::<i32>();
        }
        assert_eq!((rows, total), (5, 15));
    }

    {
        let values = [2, -1, 0, 3];
        let accepted: Vec<_> = values.iter().copied().filter(|value| *value >= 0).collect();
        let rejected = values.len() - accepted.len();
        assert_eq!(accepted, vec![2, 0, 3]);
        assert_eq!(accepted.len() + rejected, values.len());
    }

    {
        // Task 2: Guided modification
        let values = [1_i32, 2, 3, 4, 5];
        let mut results = Vec::new();
        for size in 1..=6 {
            let mut rows = 0;
            let mut total = 0;
            let mut chunks = 0;
            for batch in values.chunks(size) {
                chunks += 1;
                rows += batch.len();
                total += batch.iter().sum::<i32>();
            }
            assert_eq!(chunks, values.len().div_ceil(size));
            results.push((rows, total));
        }
        assert!(results.iter().all(|result| *result == (5, 15)));
    }

    {
        // Task 3: Independent construction
        use arrow::array::{ArrayRef, AsArray, Int32Array};
        use arrow::datatypes::Int32Type;
        use arrow::record_batch::{RecordBatch, RecordBatchIterator};
        use std::sync::Arc;
        let mut batches = Vec::new();
        for chunk in [vec![2, -1], vec![0, 3, -4]] {
            let column: ArrayRef = Arc::new(Int32Array::from(chunk));
            batches.push(RecordBatch::try_from_iter(vec![("qty", column)])?);
        }
        let schema = batches[0].schema();
        let reader = RecordBatchIterator::new(batches.into_iter().map(Ok), schema);
        let (mut rows, mut accepted) = (0, 0);
        for batch in reader {
            let batch = batch?;
            let values = batch.column(0).as_primitive::<Int32Type>();
            rows += values.len();
            accepted += values.iter().flatten().filter(|v| *v >= 0).count();
        }
        assert_eq!((rows, accepted, rows - accepted), (5, 3, 2));
    }

    {
        // Task 5: Boundary evidence
        fn account(values: &[i32], size: usize) -> (usize, usize, usize) {
            let (mut rows, mut accepted) = (0, 0);
            for batch in values.chunks(size) {
                rows += batch.len();
                accepted += batch.iter().filter(|value| **value >= 0).count();
            }
            (rows, accepted, rows - accepted)
        }
        assert_eq!(account(&[], 2), (0, 0, 0));
        assert_eq!(account(&[-1, -2], 2), (2, 0, 2));
        assert_eq!(account(&[1, 2, 3, -4, 0], 2), (5, 4, 1));
        assert_eq!([1, 2, 3, -4, 0].chunks(2).last(), Some(&[0][..]));
    }
    println!("rust-045: passed");
    Ok(())
}
