fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut count = 0;
        {
            let mut add = |value| {
                count += value;
            };
            add(2);
            add(3);
        }
        assert_eq!(count, 5);
    }

    {
        let text = String::from("owned");
        let consume = move || text;
        let result = consume();
        assert_eq!(result, "owned");
    }
    println!("rust-021: passed");
    Ok(())
}
