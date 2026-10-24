fn parse_quantity(text: &str) -> Result<i32, &'static str> {
    let value: i32 = text.parse().map_err(|_| "not an integer")?;
    if value < 0 {
        return Err("negative quantity");
    }
    Ok(value)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        assert_eq!(parse_quantity("3"), Ok(3));
        assert_eq!(parse_quantity("bad"), Err("not an integer"));
        assert_eq!(parse_quantity("-1"), Err("negative quantity"));
    }

    {
        let inputs = ["2", "bad", "3"];
        let accepted: Vec<_> = inputs
            .iter()
            .filter_map(|text| parse_quantity(text).ok())
            .collect();
        assert_eq!(accepted, vec![2, 3]);
        assert_eq!(inputs.len() - accepted.len(), 1);
    }
    println!("rust-015: passed");
    Ok(())
}
