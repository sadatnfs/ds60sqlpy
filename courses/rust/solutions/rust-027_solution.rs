

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = vec![2, 3, 4];
        let total = std::thread::scope(|scope| { let handle = scope.spawn(|| values.iter().sum::<i32>()); handle.join().expect("fixture worker") });
        assert_eq!(total, 9);
        assert_eq!(values.len(), 3);
    }

    {
        let total = std::thread::scope(|scope| { let left = scope.spawn(|| 2 + 3); let right = scope.spawn(|| 4 + 5); left.join().unwrap() + right.join().unwrap() });
        assert_eq!(total, 14);
    }
    println!("rust-027: passed");
    Ok(())
}
