

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        for a in 0_i32..10 { for b in 0_i32..10 { assert_eq!(a + b, b + a); } }
        assert_eq!(10 * 10, 100);
    }

    {
        let original = vec![3, 1, 3, 2];
        let mut sorted = original.clone(); sorted.sort();
        assert!(sorted.windows(2).all(|pair| pair[0] <= pair[1]));
        for value in 1..=3 { assert_eq!(original.iter().filter(|item| **item == value).count(), sorted.iter().filter(|item| **item == value).count()); }
    }
    println!("rust-047: passed");
    Ok(())
}
