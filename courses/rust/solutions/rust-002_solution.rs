fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let per_box = 4;
        let mut total = 0;
        total += per_box;
        total += per_box;
        assert_eq!(total, 8);
    }

    {
        let count = "12";
        let count: usize = count.len();
        assert_eq!(count, 2);
        let explicit = 3_u64;
        assert_eq!(explicit + 1, 4);
    }

    {
        // Task 3: Independent construction
        let deliveries = [3, 5, 2];
        let mut total = 0;
        for amount in deliveries {
            total += amount;
        }
        assert_eq!(total, 10);
        assert_eq!(deliveries, [3, 5, 2]);
    }
    println!("rust-002: passed");
    Ok(())
}
