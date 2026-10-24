enum Outcome {
    Ready(u32),
    Failed(String),
}
fn render(value: &Outcome) -> String {
    match value {
        Outcome::Ready(count) => format!("count:{count}"),
        Outcome::Failed(reason) => format!("error:{reason}"),
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let value = Outcome::Ready(4);
        assert_eq!(render(&value), "count:4");
    }

    {
        let value = Outcome::Failed(String::from("invalid"));
        assert_eq!(render(&value), "error:invalid");
        assert!(matches!(value, Outcome::Failed(_)));
    }
    println!("rust-013: passed");
    Ok(())
}
