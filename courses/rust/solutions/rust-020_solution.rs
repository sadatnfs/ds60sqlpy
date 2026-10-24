

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = vec![1, 2, 3, 4];
        let result: Vec<_> = values.iter().copied().filter(|value| value % 2 == 0).map(|value| value * 10).collect();
        assert_eq!(result, vec![20, 40]);
        assert_eq!(values.len(), 4);
    }

    {
        let mut iterator = [2, 3].into_iter();
        assert_eq!(iterator.next(), Some(2));
        assert_eq!(iterator.next(), Some(3));
        assert_eq!(iterator.next(), None);
    }
    println!("rust-020: passed");
    Ok(())
}
