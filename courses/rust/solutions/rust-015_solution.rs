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

    {
        // Task 2: Guided modification
        const MAX_QUANTITY: i32 = 1_000;
        fn bounded_quantity(text: &str) -> Result<i32, &'static str> {
            let value = parse_quantity(text)?;
            if value > MAX_QUANTITY {
                return Err("quantity above maximum");
            }
            Ok(value)
        }
        assert_eq!(bounded_quantity("1000"), Ok(1_000));
        assert_eq!(bounded_quantity("1001"), Err("quantity above maximum"));
        assert_eq!(bounded_quantity("bad"), Err("not an integer"));
        assert_eq!(bounded_quantity("-1"), Err("negative quantity"));
    }

    {
        // Task 3: Independent construction
        fn doubled_quantity(text: &str) -> Result<i32, &'static str> {
            let value = parse_quantity(text)?;
            value.checked_mul(2).ok_or("quantity too large")
        }
        assert_eq!(doubled_quantity("4"), Ok(8));
        assert_eq!(doubled_quantity("bad"), Err("not an integer"));
        assert_eq!(doubled_quantity("-3"), Err("negative quantity"));
    }

    {
        // Task 5: Boundary evidence
        assert_eq!(parse_quantity(""), Err("not an integer"));
        assert_eq!(parse_quantity("0"), Ok(0));
        assert_eq!(parse_quantity("-5"), Err("negative quantity"));
        assert_eq!(parse_quantity("2147483647"), Ok(i32::MAX));
        assert_eq!(parse_quantity("2147483648"), Err("not an integer"));
        assert_eq!(parse_quantity(" 3"), Err("not an integer"));
    }
    println!("rust-015: passed");
    Ok(())
}
