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
        // Task 2: Guided modification
        let mut exact: Vec<i32> = Vec::new();
        exact.reserve_exact(10);
        let mut loose: Vec<i32> = Vec::new();
        loose.reserve(10);
        assert_eq!((exact.len(), loose.len()), (0, 0));
        assert!(exact.capacity() >= 10 && loose.capacity() >= 10);
        exact.extend(0..10);
        loose.extend(0..10);
        assert_eq!(exact, loose);
        let before = exact.capacity();
        exact.reserve(0);
        assert_eq!(exact.capacity(), before);
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

    {
        // Task 5: Boundary evidence
        fn checksum_fast(values: &[u32]) -> u64 {
            values.iter().map(|&value| u64::from(value)).sum()
        }
        fn checksum_oracle(values: &[u32]) -> u64 {
            let mut total = 0_u64;
            for value in values {
                total += u64::from(*value);
            }
            total
        }
        let empty: Vec<u32> = Vec::new();
        let large = vec![u32::MAX; 100_000];
        for input in [&empty[..], &[7][..], &large[..]] {
            assert_eq!(checksum_fast(input), checksum_oracle(input));
        }
        assert_eq!(checksum_fast(&empty), 0);
        assert_eq!(checksum_fast(&large), 100_000 * u64::from(u32::MAX));
    }
    println!("rust-035: passed");
    Ok(())
}
