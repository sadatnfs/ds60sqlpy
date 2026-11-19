trait Pricer {
    fn cost(&self, units: u32) -> u32;
}
struct FlatPrice(u32);
impl Pricer for FlatPrice {
    fn cost(&self, units: u32) -> u32 {
        self.0 * units
    }
}
struct CappedPrice(u32, u32);
impl Pricer for CappedPrice {
    fn cost(&self, units: u32) -> u32 {
        (self.0 * units).min(self.1)
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let price = FlatPrice(3);
        let view: &dyn Pricer = &price;
        assert_eq!(view.cost(4), 12);
    }

    {
        let flat = FlatPrice(3);
        let capped = CappedPrice(3, 10);
        let prices: [&dyn Pricer; 2] = [&flat, &capped];
        assert_eq!(prices.map(|price| price.cost(4)), [12, 10]);
    }

    {
        // Task 3: Independent construction
        trait Formatter {
            fn format(&self, value: u32) -> String;
        }
        struct Units;
        impl Formatter for Units {
            fn format(&self, value: u32) -> String {
                format!("{value} units")
            }
        }
        let formatter: &dyn Formatter = &Units;
        assert_eq!(formatter.format(3), "3 units");
        assert_eq!(formatter.format(3), formatter.format(3));
    }
    println!("rust-017: passed");
    Ok(())
}
