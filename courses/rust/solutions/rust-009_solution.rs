

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let text = String::from("pear");
        let first = &text;
        let second = &text;
        assert_eq!(first.len() + second.len(), 8);
        assert_eq!(text, "pear");
    }

    {
        fn first_word(text: &str) -> &str { text.split_whitespace().next().unwrap_or("") }
        let sentence = String::from("pear apple");
        assert_eq!(first_word(&sentence), "pear");
        assert_eq!(first_word(""), "");
    }
    println!("rust-009: passed");
    Ok(())
}
