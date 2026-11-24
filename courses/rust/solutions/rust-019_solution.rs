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

    {
        // Task 2: Guided modification
        let first = String::from("pear");
        let second = String::from("plum");
        let chosen = longer(&first, &second);
        assert!(std::ptr::eq(chosen, first.as_str()));
        assert_eq!(longer("fig", "kiwi"), "kiwi");
        assert_eq!(longer("", ""), "");
    }

    {
        // Task 3: Independent construction
        fn split_prefix<'a>(text: &'a str, prefix: &str) -> Option<&'a str> {
            text.strip_prefix(prefix)
        }
        let line = String::from("qty:42");
        let rest = {
            let prefix = String::from("qty:");
            split_prefix(&line, &prefix)
        };
        assert_eq!(rest, Some("42"));
    }

    {
        // Task 5: Boundary evidence
        assert_eq!(longer("", "x"), "x");
        assert_eq!(longer("x", ""), "x");
        let outer = String::from("outer value");
        let kept = {
            let inner = String::from("in");
            longer(&outer, &inner).to_owned()
        };
        assert_eq!(kept, "outer value");
    }
    println!("rust-019: passed");
    Ok(())
}
