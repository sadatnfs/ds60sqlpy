fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        fn name_length() -> usize {
            let cell = std::cell::RefCell::new(String::from("pear"));
            cell.borrow().len()
        }
        assert_eq!(name_length(), 4);
    }

    {
        let boxed: Box<[String]> = vec![String::from("a"), String::from("b")].into_boxed_slice();
        let owned: Vec<String> = boxed.into_iter().collect();
        assert_eq!(owned, ["a", "b"]);
    }
    println!("rust-036: passed");
    Ok(())
}
