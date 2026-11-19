fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        fn append_mark(text: &mut String) {
            text.push('!');
        }
        let mut text = String::from("ready");
        append_mark(&mut text);
        assert_eq!(text, "ready!");
    }

    {
        let mut values = [1, 2, 3, 4];
        let (left, right) = values.split_at_mut(2);
        left[0] = 9;
        right[0] = 8;
        assert_eq!(values, [9, 2, 8, 4]);
    }

    {
        // Task 3: Independent construction
        fn swap_ends(values: &mut [i32]) {
            if let Some(last) = values.len().checked_sub(1) {
                values.swap(0, last);
            }
        }
        let mut values = [1, 2, 3];
        swap_ends(&mut values);
        assert_eq!(values, [3, 2, 1]);
        let mut empty: [i32; 0] = [];
        swap_ends(&mut empty);
        assert!(empty.is_empty());
    }
    println!("rust-010: passed");
    Ok(())
}
