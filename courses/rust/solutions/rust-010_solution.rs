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
        // Task 2: Guided modification
        let mut values = [1, 2, 3, 4];
        let (left, right) = values.split_at_mut(2);
        left[0] = 9;
        right[0] = 8;
        values[3] = 7;
        assert_eq!(values, [9, 2, 8, 7]);
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

    {
        // Task 5: Boundary evidence
        let mut values = [1, 2, 3];
        let (left, right) = values.split_at_mut(0);
        assert!(left.is_empty());
        right[0] = 7;
        let (left, right) = values.split_at_mut(3);
        assert!(right.is_empty());
        left[2] = 9;
        assert_eq!(values, [7, 2, 9]);
        assert!(values.split_at_mut_checked(4).is_none());
        let mut empty: [i32; 0] = [];
        let (left, right) = empty.split_at_mut(0);
        assert!(left.is_empty() && right.is_empty());
    }
    println!("rust-010: passed");
    Ok(())
}
