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
    println!("rust-024: passed");
    Ok(())
}
