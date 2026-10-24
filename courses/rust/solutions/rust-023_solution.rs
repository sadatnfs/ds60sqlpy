mod domain { pub fn double(value: i32) -> i32 { value * 2 } }

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        assert_eq!(domain::double(4), 8);
        assert_eq!(domain::double(0), 0);
    }

    {
        use domain::double;
        assert_eq!(double(3), 6);
    }
    println!("rust-023: passed");
    Ok(())
}
