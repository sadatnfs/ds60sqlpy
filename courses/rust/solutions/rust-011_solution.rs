

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        fn total(values: &[i32]) -> i32 { values.iter().sum() }
        assert_eq!(total(&[2, 3, 4]), 9);
        assert_eq!(total(&vec![1, 2]), 3);
        assert_eq!(total(&[]), 0);
    }

    {
        let mut values: Vec<i32> = Vec::with_capacity(10);
        assert_eq!(values.len(), 0);
        assert!(values.capacity() >= 10);
        values.push(7);
        assert_eq!(values.get(0), Some(&7));
        assert_eq!(values.get(1), None);
    }
    println!("rust-011: passed");
    Ok(())
}
