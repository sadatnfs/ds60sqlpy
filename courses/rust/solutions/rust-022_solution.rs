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

    {
        // Task 3: Independent construction
        #[derive(Debug)]
        enum ImportError {
            Syntax { line: usize },
            Storage(std::io::Error),
        }
        impl std::fmt::Display for ImportError {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                match self {
                    Self::Syntax { line } => write!(f, "syntax error on line {line}"),
                    Self::Storage(_) => write!(f, "storage failed"),
                }
            }
        }
        impl std::error::Error for ImportError {
            fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
                match self {
                    Self::Syntax { .. } => None,
                    Self::Storage(cause) => Some(cause),
                }
            }
        }
        use std::error::Error;
        let syntax = ImportError::Syntax { line: 3 };
        assert_eq!(syntax.to_string(), "syntax error on line 3");
        assert!(syntax.source().is_none());
        let cause = std::io::Error::other("disk full");
        let storage = ImportError::Storage(cause);
        assert_eq!(storage.source().unwrap().to_string(), "disk full");
    }
    println!("rust-022: passed");
    Ok(())
}
