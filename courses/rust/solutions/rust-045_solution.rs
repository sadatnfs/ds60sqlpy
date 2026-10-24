

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = [1_i32, 2, 3, 4, 5];
        let mut total = 0;
        let mut rows = 0;
        for batch in values.chunks(2) { rows += batch.len(); total += batch.iter().sum::<i32>(); }
        assert_eq!((rows, total), (5, 15));
    }

    {
        let values = [2, -1, 0, 3];
        let accepted: Vec<_> = values.iter().copied().filter(|value| *value >= 0).collect();
        let rejected = values.len() - accepted.len();
        assert_eq!(accepted, vec![2, 0, 3]);
        assert_eq!(accepted.len() + rejected, values.len());
    }
    println!("rust-045: passed");
    Ok(())
}
