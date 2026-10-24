#[derive(Debug)]
enum InputError {
    Malformed,
    Negative,
}
impl std::fmt::Display for InputError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "{}",
            match self {
                Self::Malformed => "quantity is not an integer",
                Self::Negative => "quantity must be nonnegative",
            }
        )
    }
}
impl std::error::Error for InputError {}
fn validated(text: &str) -> Result<i32, InputError> {
    let value = text.parse().map_err(|_| InputError::Malformed)?;
    if value < 0 {
        Err(InputError::Negative)
    } else {
        Ok(value)
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        assert!(matches!(validated("-1"), Err(InputError::Negative)));
        assert!(matches!(validated("bad"), Err(InputError::Malformed)));
    }

    {
        let error = InputError::Negative;
        assert_eq!(error.to_string(), "quantity must be nonnegative");
        assert_eq!(validated("3").unwrap(), 3);
    }
    println!("rust-022: passed");
    Ok(())
}
