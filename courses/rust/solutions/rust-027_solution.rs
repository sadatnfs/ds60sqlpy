fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = vec![2, 3, 4];
        let total = std::thread::scope(|scope| {
            let handle = scope.spawn(|| values.iter().sum::<i32>());
            handle.join().expect("fixture worker")
        });
        assert_eq!(total, 9);
        assert_eq!(values.len(), 3);
    }

    {
        let total = std::thread::scope(|scope| {
            let left = scope.spawn(|| 2 + 3);
            let right = scope.spawn(|| 4 + 5);
            left.join().unwrap() + right.join().unwrap()
        });
        assert_eq!(total, 14);
    }

    {
        // Task 2: Guided modification
        let values = [3, 1, 4, 1, 5];
        let (left, right) = values.split_at(values.len() / 2);
        assert_eq!((left.len(), right.len()), (2, 3));
        let total = std::thread::scope(|scope| {
            let low = scope.spawn(|| left.iter().sum::<i32>());
            let high = scope.spawn(|| right.iter().sum::<i32>());
            low.join().expect("left half") + high.join().expect("right half")
        });
        assert_eq!(total, 14);
        assert_eq!(total, values.iter().sum::<i32>());
    }

    {
        // Task 3: Independent construction
        let values = [1, 2, 3, 4, 5, 6];
        let (left, right) = values.split_at(3);
        let (a, b) = std::thread::scope(|scope| {
            let first = scope.spawn(|| left.iter().sum::<i32>());
            let second = scope.spawn(|| right.iter().sum::<i32>());
            (first.join().unwrap(), second.join().unwrap())
        });
        assert_eq!((a, b), (6, 15));
        assert_eq!(a + b, values.iter().sum::<i32>());
    }

    {
        // Task 5: Boundary evidence
        let empty: [i32; 0] = [];
        let (left, right) = empty.split_at(0);
        let total = std::thread::scope(|scope| {
            let low = scope.spawn(|| left.iter().sum::<i32>());
            let high = scope.spawn(|| right.iter().sum::<i32>());
            low.join().expect("left half") + high.join().expect("right half")
        });
        assert_eq!(total, 0);
        let previous = std::panic::take_hook();
        std::panic::set_hook(Box::new(|_| {}));
        let outcome = std::thread::scope(|scope| {
            let worker = scope.spawn(|| -> i32 { panic!("worker failed") });
            worker.join()
        });
        std::panic::set_hook(previous);
        assert!(outcome.is_err());
    }
    println!("rust-027: passed");
    Ok(())
}
