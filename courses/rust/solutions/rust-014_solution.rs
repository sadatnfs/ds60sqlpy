

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let measured = Some(0);
        let missing: Option<i32> = None;
        assert_ne!(measured, missing);
        assert_eq!(measured.map(|value| value + 1), Some(1));
    }

    {
        let values = [2, 4];
        assert_eq!(values.get(9).map(|value| value * 2), None);
        assert_eq!(values.get(9).copied().unwrap_or(-1), -1);
    }
    println!("rust-014: passed");
    Ok(())
}
