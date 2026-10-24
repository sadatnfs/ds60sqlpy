fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let first = String::from("pear");
        let second = first;
        assert_eq!(second, "pear");
        // Using first here would be a compile error: ownership moved.
    }

    {
        let first = String::from("pear");
        let mut second = first.clone();
        second.push('s');
        assert_eq!(first, "pear");
        assert_eq!(second, "pears");
    }
    println!("rust-008: passed");
    Ok(())
}
