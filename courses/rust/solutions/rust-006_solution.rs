fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = vec![2, 4, 6];
        let mut total = 0;
        for value in &values {
            total += value;
        }
        assert_eq!(total, 12);
        assert_eq!(values.len(), 3);
    }

    {
        let values = [3, 8, 8];
        assert_eq!(values.iter().position(|value| *value == 8), Some(1));
        assert_eq!(values.iter().position(|value| *value == 9), None);
    }

    {
        // Task 2: Guided modification
        let values = [4, -2, 5, -7, 1];
        let mut total = 0;
        let mut skipped = 0;
        for value in values {
            if value < 0 {
                skipped += 1;
                continue;
            }
            total += value;
        }
        assert_eq!(total, 10);
        assert_eq!(skipped, 2);
        assert_eq!(
            total,
            values.iter().filter(|value| **value >= 0).sum::<i32>()
        );
    }

    {
        // Task 3: Independent construction
        fn first_index(values: &[i32], target: i32) -> Option<usize> {
            for (index, value) in values.iter().enumerate() {
                if *value == target {
                    return Some(index);
                }
            }
            None
        }
        assert_eq!(first_index(&[5, 7, 7], 7), Some(1));
        assert_eq!(first_index(&[5, 7], 9), None);
        assert_eq!(first_index(&[], 1), None);
    }

    {
        // Task 5: Boundary evidence
        let empty: [i32; 0] = [];
        assert_eq!(empty.iter().position(|value| *value == 8), None);
        assert_eq!(empty.iter().sum::<i32>(), 0);
        assert_eq!([8].iter().position(|value| *value == 8), Some(0));
        assert_eq!([3].iter().position(|value| *value == 8), None);
        let repeated = [8, 8, 8];
        assert_eq!(repeated.iter().position(|value| *value == 8), Some(0));
        assert_eq!(repeated.iter().rposition(|value| *value == 8), Some(2));
        assert_eq!(repeated.iter().filter(|value| **value == 8).count(), 3);
    }
    println!("rust-006: passed");
    Ok(())
}
