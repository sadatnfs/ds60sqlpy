fn longer<'a>(left: &'a str, right: &'a str) -> &'a str {
    if left.len() >= right.len() {
        left
    } else {
        right
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let left = String::from("pear");
        let right = String::from("watermelon");
        assert_eq!(longer(&left, &right), "watermelon");
    }

    {
        let result = {
            let temporary = String::from("retained");
            temporary.to_owned()
        };
        assert_eq!(result, "retained");
    }
    println!("rust-019: passed");
    Ok(())
}
