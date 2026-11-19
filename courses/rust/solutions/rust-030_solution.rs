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
    println!("rust-030: passed");
    Ok(())
}
