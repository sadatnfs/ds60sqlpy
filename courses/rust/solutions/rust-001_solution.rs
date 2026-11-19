fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let greeting = "Hello, Rust";
        assert_eq!(greeting, "Hello, Rust");
        println!("{greeting}");
    }

    {
        let rows = 4;
        let seats_per_row = 6;
        let seats = rows * seats_per_row;
        assert_eq!(seats, 24);
        assert_ne!(seats, rows + seats_per_row);
    }

    {
        // Task 3: Independent construction
        let shelves = 3;
        let books_per_shelf = 8;
        let capacity = shelves * books_per_shelf;
        assert_eq!(capacity, 24);
    }
    println!("rust-001: passed");
    Ok(())
}
