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
    println!("rust-010: passed");
    Ok(())
}
