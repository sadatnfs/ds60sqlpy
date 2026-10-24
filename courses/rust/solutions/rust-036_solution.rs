

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let policy = ["edition=2024", "locked", "offline-after-preparation"];
        assert!(policy.contains(&"edition=2024"));
        assert_ne!(policy[0], "compiler-version");
    }

    {
        let checks = [true, true, false];
        assert!(!checks.iter().all(|passed| *passed));
        assert_eq!(checks.iter().filter(|passed| !**passed).count(), 1);
    }
    println!("rust-036: passed");
    Ok(())
}
