

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::sync::{Arc, Mutex};
        let count = Arc::new(Mutex::new(0));
        std::thread::scope(|scope| { for _ in 0..4 { let count = Arc::clone(&count); scope.spawn(move || { for _ in 0..100 { *count.lock().unwrap() += 1; } }); } });
        assert_eq!(*count.lock().unwrap(), 400);
    }

    {
        let balances = std::sync::Mutex::new((10, 0));
        { let mut guard = balances.lock().unwrap(); guard.0 -= 3; guard.1 += 3; }
        let guard = balances.lock().unwrap();
        assert_eq!(*guard, (7, 3));
        assert_eq!(guard.0 + guard.1, 10);
    }
    println!("rust-028: passed");
    Ok(())
}
