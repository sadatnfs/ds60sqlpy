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
    println!("rust-046: passed");
    Ok(())
}
