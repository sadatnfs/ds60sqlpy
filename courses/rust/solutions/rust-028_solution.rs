fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::sync::{Arc, Mutex};
        let count = Arc::new(Mutex::new(0));
        std::thread::scope(|scope| {
            for _ in 0..4 {
                let count = Arc::clone(&count);
                scope.spawn(move || {
                    for _ in 0..100 {
                        *count.lock().unwrap() += 1;
                    }
                });
            }
        });
        assert_eq!(*count.lock().unwrap(), 400);
    }

    {
        let balances = std::sync::Mutex::new((10, 0));
        {
            let mut guard = balances.lock().unwrap();
            guard.0 -= 3;
            guard.1 += 3;
        }
        let guard = balances.lock().unwrap();
        assert_eq!(*guard, (7, 3));
        assert_eq!(guard.0 + guard.1, 10);
    }

    {
        // Task 3: Independent construction
        let stock = std::sync::Mutex::new(5_u32);
        let reserve = |amount: u32| {
            let mut available = stock.lock().unwrap();
            let granted = amount <= *available;
            if granted {
                *available -= amount;
            }
            granted
        };
        let results: Vec<bool> = std::thread::scope(|scope| {
            let handles: Vec<_> = (0..4).map(|_| scope.spawn(|| reserve(2))).collect();
            handles
                .into_iter()
                .map(|handle| handle.join().unwrap())
                .collect()
        });
        assert_eq!(results.iter().filter(|granted| **granted).count(), 2);
        assert_eq!(*stock.lock().unwrap(), 1);
    }
    println!("rust-028: passed");
    Ok(())
}
