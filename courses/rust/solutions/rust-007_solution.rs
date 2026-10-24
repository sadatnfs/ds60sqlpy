fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        fn double(value: i32) -> i32 {
            value * 2
        }
        let original = 7;
        assert_eq!(double(original), 14);
        assert_eq!(original, 7);
    }

    {
        fn starts_with_p(text: &str) -> bool {
            text.starts_with('p')
        }
        let owned = String::from("pear");
        assert!(starts_with_p(&owned));
        assert!(!starts_with_p("apple"));
        assert_eq!(owned, "pear");
    }
    println!("rust-007: passed");
    Ok(())
}
