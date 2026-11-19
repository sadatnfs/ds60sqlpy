fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::sync::mpsc::{sync_channel, TrySendError};
        let (send, receive) = sync_channel(1);
        send.try_send(4)?;
        assert!(matches!(send.try_send(5), Err(TrySendError::Full(5))));
        assert_eq!(receive.recv()?, 4);
    }

    {
        let (send, receive) = std::sync::mpsc::sync_channel(2);
        let worker = std::thread::spawn(move || {
            send.send(2).unwrap();
            send.send(3).unwrap();
        });
        let total: i32 = receive.iter().sum();
        worker.join().unwrap();
        assert_eq!(total, 5);
    }

    {
        // Task 3: Independent construction
        let (send, receive) = std::sync::mpsc::sync_channel::<u32>(2);
        let producer = std::thread::spawn(move || {
            for quantity in [3, 5, 2] {
                send.send(quantity).unwrap();
            }
        });
        let mut report = Vec::new();
        for quantity in receive {
            report.push(format!("qty={quantity}"));
        }
        producer.join().unwrap();
        assert_eq!(report, ["qty=3", "qty=5", "qty=2"]);
    }
    println!("rust-029: passed");
    Ok(())
}
