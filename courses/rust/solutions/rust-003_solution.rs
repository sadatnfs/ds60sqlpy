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
    println!("rust-003: passed");
    Ok(())
}
