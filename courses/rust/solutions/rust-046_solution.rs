struct Event {
    operation: &'static str,
    stage: &'static str,
    outcome: &'static str,
    count: usize,
}
impl Event {
    fn render(&self) -> String {
        format!(
            "{} {} {} count={}",
            self.operation, self.stage, self.outcome, self.count
        )
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let event = Event {
            operation: "fixture-1",
            stage: "validate",
            outcome: "rejected",
            count: 2,
        };
        assert_eq!(event.render(), "fixture-1 validate rejected count=2");
    }

    {
        let allowed = ["report:read", "report:list"];
        assert!(allowed.contains(&"report:read"));
        assert!(!allowed.contains(&"report:delete"));
    }

    {
        // Task 3: Independent construction
        let inputs = ["2", "x", "5", "-1"];
        let mut accepted = 0;
        let mut rejected = 0;
        for text in inputs {
            match text.parse::<u32>() {
                Ok(_) => accepted += 1,
                Err(_) => rejected += 1,
            }
        }
        let submitted = inputs.len();
        let counts = format!("accepted={accepted} rejected={rejected}");
        let event = format!("submitted={submitted} {counts}");
        assert_eq!(event, "submitted=4 accepted=2 rejected=2");
        assert_eq!(accepted + rejected, submitted);
    }
    println!("rust-046: passed");
    Ok(())
}
