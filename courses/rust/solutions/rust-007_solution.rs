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

    {
        // Task 3: Independent construction
        /// Area of a rectangle; both sides must be at most 65_535.
        fn area(width: u32, height: u32) -> u32 {
            assert!(width <= 65_535 && height <= 65_535);
            width * height
        }
        assert_eq!(area(3, 4), 12);
        assert_eq!(area(0, 9), 0);
        assert_eq!(area(65_535, 65_535), 4_294_836_225);
    }
    println!("rust-007: passed");
    Ok(())
}
