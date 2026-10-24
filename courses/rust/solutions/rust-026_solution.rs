fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut counts = std::collections::BTreeMap::new();
        for label in ["b", "a", "b"] {
            *counts.entry(label).or_insert(0) += 1;
        }
        assert_eq!(counts.get("b"), Some(&2));
        assert_eq!(counts.keys().copied().collect::<Vec<_>>(), vec!["a", "b"]);
    }

    {
        let mut seen = std::collections::HashSet::new();
        assert!(seen.insert("pear"));
        assert!(!seen.insert("pear"));
        assert!(!seen.contains("apple"));
    }
    println!("rust-026: passed");
    Ok(())
}
