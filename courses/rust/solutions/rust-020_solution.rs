fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = vec![1, 2, 3, 4];
        let result: Vec<_> = values
            .iter()
            .copied()
            .filter(|value| value % 2 == 0)
            .map(|value| value * 10)
            .collect();
        assert_eq!(result, vec![20, 40]);
        assert_eq!(values.len(), 4);
    }

    {
        let mut iterator = [2, 3].into_iter();
        assert_eq!(iterator.next(), Some(2));
        assert_eq!(iterator.next(), Some(3));
        assert_eq!(iterator.next(), None);
    }

    {
        // Task 3: Independent construction
        fn upper_names(names: &[&str]) -> Vec<String> {
            names.iter().map(|name| name.to_uppercase()).collect()
        }
        let names = ["pear", "fig"];
        assert_eq!(upper_names(&names), vec!["PEAR", "FIG"]);
        assert_eq!(names, ["pear", "fig"]);
    }
    println!("rust-020: passed");
    Ok(())
}
