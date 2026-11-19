mod domain {
    pub fn double(value: i32) -> i32 {
        value * 2
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        assert_eq!(domain::double(4), 8);
        assert_eq!(domain::double(0), 0);
    }

    {
        use domain::double;
        assert_eq!(double(3), 6);
    }

    {
        // Task 3: Independent construction
        mod pricing {
            pub fn total(unit: u32, quantity: u32) -> Option<u32> {
                unit.checked_mul(quantity)
            }
        }
        assert_eq!(pricing::total(4, 5), Some(20));
        assert_eq!(pricing::total(u32::MAX, 2), None);
    }
    println!("rust-023: passed");
    Ok(())
}
