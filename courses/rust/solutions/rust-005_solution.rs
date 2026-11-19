fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let count = 3;
        let label = if count > 0 { "present" } else { "empty" };
        assert_eq!(label, "present");
    }

    {
        let classify = |score| match score {
            0..=59 => "retry",
            60..=100 => "pass",
            _ => "invalid",
        };
        assert_eq!(classify(59), "retry");
        assert_eq!(classify(60), "pass");
        assert_eq!(classify(101), "invalid");
    }

    {
        // Task 3: Independent construction
        fn classify(value: i32) -> &'static str {
            match value {
                i32::MIN..=-1 => "negative",
                0 => "zero",
                1..=i32::MAX => "positive",
            }
        }
        assert_eq!(classify(-4), "negative");
        assert_eq!(classify(0), "zero");
        assert_eq!(classify(9), "positive");
    }
    println!("rust-005: passed");
    Ok(())
}
