

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let owned = String::from("pear");
        let borrowed: &str = &owned;
        assert_eq!(borrowed, "pear");
        assert_eq!(owned.len(), 4);
    }

    {
        let text = "é";
        assert_eq!(text.len(), 2);
        assert_eq!(text.chars().count(), 1);
        assert_eq!(text.get(0..1), None);
        assert_eq!(text.get(0..2), Some("é"));
    }
    println!("rust-004: passed");
    Ok(())
}
