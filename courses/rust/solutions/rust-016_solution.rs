fn import_rows(lines: &[&str]) -> (std::collections::BTreeMap<String, u32>, usize) { let mut totals = std::collections::BTreeMap::new(); let mut rejected = 0; for line in lines { let Some((name, quantity)) = line.split_once(',') else { rejected += 1; continue; }; let Ok(quantity) = quantity.parse::<u32>() else { rejected += 1; continue; }; if name.trim().is_empty() { rejected += 1; continue; } let previous: u32 = *totals.get(name).unwrap_or(&0); let Some(total) = previous.checked_add(quantity) else { rejected += 1; continue; }; totals.insert(name.to_owned(), total); } (totals, rejected) }

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let (totals, rejected) = import_rows(&["pear,2", "apple,3", "pear,4"]);
        assert_eq!(totals.get("pear"), Some(&6));
        assert_eq!(totals.get("apple"), Some(&3));
        assert_eq!(rejected, 0);
    }

    {
        let (totals, rejected) = import_rows(&["pear,0", "bad", "apple,-1", "pear,no"]);
        assert_eq!(totals.get("pear"), Some(&0));
        assert_eq!(rejected, 3);
        assert!(import_rows(&[]).0.is_empty());
    }
    println!("rust-016: passed");
    Ok(())
}
