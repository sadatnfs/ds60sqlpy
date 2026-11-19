fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let cases = [(-2, 0), (0, 0), (3, 3)];
        for (input, expected) in cases {
            assert_eq!(input.max(0), expected);
        }
    }

    {
        let wrong = |value: i32| if value <= 0 { 1 } else { value };
        assert_ne!(wrong(0), 0);
        assert_eq!((-4_i32).max(0).max(0), (-4_i32).max(0));
    }

    {
        // Task 3: Independent construction
        fn valid_quantity(value: i32) -> bool {
            (0..=1000).contains(&value)
        }
        let cases = [(-1, false), (0, true), (1000, true), (1001, false)];
        for (input, expected) in cases {
            assert_eq!(valid_quantity(input), expected, "input {input}");
        }
    }
    println!("rust-024: passed");
    Ok(())
}
