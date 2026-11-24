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
        // Task 2: Guided modification
        assert_eq!(0_u8.checked_sub(1), None);
        assert_eq!(0_u8.wrapping_sub(1), 255);
        assert_eq!(0_u8.saturating_sub(1), 0);
        assert_eq!(5_u8.checked_sub(3), Some(2));
        let stock: u32 = 2;
        let ordered: u32 = 3;
        assert_eq!(stock.checked_sub(ordered), None);
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

    {
        // Task 5: Boundary evidence
        fn accept_quantity(quantity: u32) -> Result<u32, String> {
            if quantity <= 1_000 {
                Ok(quantity)
            } else {
                Err(format!("quantity {quantity} exceeds 1000"))
            }
        }
        assert_eq!(accept_quantity(0), Ok(0));
        assert_eq!(accept_quantity(1_000), Ok(1_000));
        assert_eq!(
            accept_quantity(1_001),
            Err(String::from("quantity 1001 exceeds 1000"))
        );
        assert_eq!(u8::try_from(255_u32), Ok(255));
        assert!(u8::try_from(256_u32).is_err());
        assert_eq!(300_i32 as u8, 44);
    }
    println!("rust-003: passed");
    Ok(())
}
