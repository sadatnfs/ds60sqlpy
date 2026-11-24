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

    {
        // Task 3: Independent construction
        fn shout(mut text: String) -> String {
            text.push('!');
            text
        }
        let original = String::from("ready");
        let louder = shout(original);
        assert_eq!(louder, "ready!");
    }

    {
        // Task 5: Boundary evidence
        let count = 5_i32;
        let copied = count;
        assert_eq!(count + copied, 10);
        let name = String::from("pear");
        let address = name.as_ptr();
        let moved = name;
        assert_eq!(moved.as_ptr(), address);
        let cloned = moved.clone();
        assert_ne!(cloned.as_ptr(), address);
        assert_eq!(moved, cloned);
    }
    println!("rust-008: passed");
    Ok(())
}
