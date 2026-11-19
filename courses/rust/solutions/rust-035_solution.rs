fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let small = String::from("a");
        let large = "x".repeat(1000);
        assert_eq!(std::mem::size_of_val(&small), std::mem::size_of_val(&large));
        assert_ne!(small.len(), large.len());
    }

    {
        let mut values = Vec::with_capacity(100);
        values.extend(0..10);
        assert_eq!(values.len(), 10);
        assert!(values.capacity() >= 100);
        assert_eq!(values.iter().sum::<i32>(), 45);
    }

    {
        // Task 3: Independent construction
        fn total_cloned(rows: &[String]) -> usize {
            rows.iter().map(|row| row.clone().len()).sum()
        }
        fn total_borrowed(rows: &[String]) -> usize {
            rows.iter().map(|row| row.len()).sum()
        }
        let rows: Vec<String> = (0..100).map(|i| format!("row-{i}")).collect();
        assert_eq!(total_cloned(&rows), total_borrowed(&rows));
    }
    println!("rust-035: passed");
    Ok(())
}
