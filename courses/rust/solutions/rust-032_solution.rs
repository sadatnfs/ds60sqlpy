fn summarize<'a>(rows: &[(&'a str, i32)]) -> (std::collections::BTreeMap<&'a str, i32>, usize) {
    let mut totals = std::collections::BTreeMap::new();
    let mut rejected = 0;
    for &(name, value) in rows {
        if name.is_empty() || value < 0 {
            rejected += 1;
            continue;
        }
        let previous: i32 = *totals.get(name).unwrap_or(&0);
        if let Some(total) = previous.checked_add(value) {
            totals.insert(name, total);
        } else {
            rejected += 1;
        }
    }
    (totals, rejected)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let report = summarize(&[("b", 2), ("a", 3), ("b", 4)]);
        assert_eq!(report.0.get("b"), Some(&6));
        assert_eq!(report.0.keys().copied().collect::<Vec<_>>(), vec!["a", "b"]);
    }

    {
        let report = summarize(&[("", 2), ("a", -1), ("b", 0)]);
        assert_eq!(report.1, 2);
        assert_eq!(report.0.get("b"), Some(&0));
    }
    println!("rust-032: passed");
    Ok(())
}
