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
        // Task 2: Guided modification
        fn labeled_length(label: &str, text: &str) -> String {
            format!("{label}: {} bytes", text.len())
        }
        let owned = String::from("pear");
        assert_eq!(labeled_length("fruit", &owned), "fruit: 4 bytes");
        assert_eq!(labeled_length("note", "café"), "note: 5 bytes");
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

    {
        // Task 5: Boundary evidence
        fn labeled_length(text: &str) -> String {
            format!("length={}", text.len())
        }
        fn area(width: u32, height: u32) -> u32 {
            width * height
        }
        assert_eq!(labeled_length(""), "length=0");
        assert_eq!(labeled_length(&String::new()), "length=0");
        assert_eq!(area(0, 0), 0);
        assert_eq!(area(0, 65_535), 0);
        assert_eq!(area(65_535, 0), 0);
    }
    println!("rust-007: passed");
    Ok(())
}
