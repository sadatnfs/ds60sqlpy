struct Inventory {
    stock: u32,
}
impl Inventory {
    fn new(stock: u32) -> Self {
        Self { stock }
    }
    fn stock(&self) -> u32 {
        self.stock
    }
    fn reserve(&mut self, amount: u32) -> bool {
        if amount > self.stock {
            return false;
        }
        self.stock -= amount;
        true
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut inventory = Inventory::new(5);
        assert!(inventory.reserve(2));
        assert_eq!(inventory.stock(), 3);
    }

    {
        let mut inventory = Inventory::new(3);
        assert!(!inventory.reserve(4));
        assert_eq!(inventory.stock(), 3);
        assert!(inventory.reserve(0));
    }
    println!("rust-012: passed");
    Ok(())
}
