fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let text = String::from("owned");
        let worker = std::thread::spawn(move || text.len());
        assert_eq!(worker.join().unwrap(), 5);
    }

    {
        fn require_send<T: Send>() {}
        fn require_sync<T: Sync>() {}
        require_send::<String>();
        require_sync::<String>();
        require_send::<std::sync::Arc<std::sync::Mutex<i32>>>();
        assert_eq!(std::sync::Arc::strong_count(&std::sync::Arc::new(1)), 1);
    }

    {
        // Task 2: Guided modification
        let readings = vec![4, 8, 15, 16];
        let worker = std::thread::spawn(move || {
            let total: i32 = readings.iter().sum();
            (readings.len(), total)
        });
        assert_eq!(worker.join().unwrap(), (4, 43));
    }

    {
        // Task 3: Independent construction
        use std::sync::Arc;
        use std::sync::atomic::{AtomicUsize, Ordering};
        let counter = Arc::new(AtomicUsize::new(0));
        let mut handles = Vec::new();
        for _ in 0..4 {
            let counter = Arc::clone(&counter);
            handles.push(std::thread::spawn(move || {
                for _ in 0..100 {
                    counter.fetch_add(1, Ordering::Relaxed);
                }
            }));
        }
        for handle in handles {
            handle.join().unwrap();
        }
        assert_eq!(counter.load(Ordering::Relaxed), 400);
    }

    {
        // Task 5: Boundary evidence
        let rows = vec![String::from("a"), String::from("bc")];
        let total = std::thread::scope(|scope| {
            let worker = scope.spawn(|| rows.iter().map(String::len).sum::<usize>());
            worker.join().unwrap()
        });
        assert_eq!(total, 3);
        assert_eq!(rows.len(), 2);
        let empty: Vec<String> = Vec::new();
        let count = std::thread::scope(|scope| scope.spawn(|| empty.len()).join().unwrap());
        assert_eq!(count, 0);
    }
    println!("rust-030: passed");
    Ok(())
}
