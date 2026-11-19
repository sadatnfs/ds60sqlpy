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
    println!("rust-006: passed");
    Ok(())
}
