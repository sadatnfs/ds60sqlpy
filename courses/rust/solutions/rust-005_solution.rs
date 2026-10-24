

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let count = 3;
        let label = if count > 0 { "present" } else { "empty" };
        assert_eq!(label, "present");
    }

    {
        let classify = |score| match score { 0..=59 => "retry", 60..=100 => "pass", _ => "invalid" };
        assert_eq!(classify(59), "retry");
        assert_eq!(classify(60), "pass");
        assert_eq!(classify(101), "invalid");
    }
    println!("rust-005: passed");
    Ok(())
}
