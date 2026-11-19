fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut count = 0;
        {
            let mut add = |value| {
                count += value;
            };
            add(2);
            add(3);
        }
        assert_eq!(count, 5);
    }

    {
        let text = String::from("owned");
        let consume = move || text;
        let result = consume();
        assert_eq!(result, "owned");
    }

    {
        // Task 3: Independent construction
        fn apply_times(times: usize, mut step: impl FnMut()) {
            for _ in 0..times {
                step();
            }
        }
        let mut value = 1;
        apply_times(3, || value *= 2);
        assert_eq!(value, 8);
    }
    println!("rust-021: passed");
    Ok(())
}
