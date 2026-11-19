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

    {
        // Task 3: Independent construction
        enum Import {
            Pending { queued: usize },
            Completed { rows: usize },
            Rejected { reason: String },
        }
        fn describe(state: &Import) -> String {
            match state {
                Import::Pending { queued } => format!("pending:{queued}"),
                Import::Completed { rows } => format!("done:{rows}"),
                Import::Rejected { reason } => format!("rejected:{reason}"),
            }
        }
        assert_eq!(describe(&Import::Pending { queued: 2 }), "pending:2");
        assert_eq!(describe(&Import::Completed { rows: 5 }), "done:5");
        let rejected = Import::Rejected {
            reason: String::from("bad header"),
        };
        assert_eq!(describe(&rejected), "rejected:bad header");
    }
    println!("rust-013: passed");
    Ok(())
}
