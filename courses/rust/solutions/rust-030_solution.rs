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
    println!("rust-030: passed");
    Ok(())
}
