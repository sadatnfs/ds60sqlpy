fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        assert_eq!(255_u8.checked_add(1), None);
        assert_eq!(255_u8.wrapping_add(1), 0);
        assert_eq!(255_u8.saturating_add(1), 255);
        assert_eq!(2_u8.checked_add(3), Some(5));
    }

    {
        let cents_per_item: u64 = 125;
        let quantity: u64 = 3;
        assert_eq!(cents_per_item.checked_mul(quantity), Some(375));
        let approximate = 0.1_f64 + 0.2;
        assert!((approximate - 0.3).abs() < 1e-12);
    }

    {
        // Task 3: Independent construction
        fn total_cents(price: u64, quantity: u64) -> Result<u64, String> {
            price
                .checked_mul(quantity)
                .ok_or_else(|| String::from("total overflows u64"))
        }
        assert_eq!(total_cents(125, 3), Ok(375));
        assert!(total_cents(u64::MAX, 2).is_err());
    }
    println!("rust-003: passed");
    Ok(())
}
