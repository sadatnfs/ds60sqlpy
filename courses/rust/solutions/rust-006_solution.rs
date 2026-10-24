

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = vec![2, 4, 6];
        let mut total = 0;
        for value in &values { total += value; }
        assert_eq!(total, 12);
        assert_eq!(values.len(), 3);
    }

    {
        let values = [3, 8, 8];
        assert_eq!(values.iter().position(|value| *value == 8), Some(1));
        assert_eq!(values.iter().position(|value| *value == 9), None);
    }
    println!("rust-006: passed");
    Ok(())
}
