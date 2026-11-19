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
    println!("rust-045: passed");
    Ok(())
}
