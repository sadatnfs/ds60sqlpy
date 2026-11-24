fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::future::Future;
        use std::task::{Context, Poll, Waker};
        let mut future = Box::pin(async { 7 });
        let mut context = Context::from_waker(Waker::noop());
        assert_eq!(future.as_mut().poll(&mut context), Poll::Ready(7));
    }

    {
        use std::future::Future;
        use std::task::{Context, Poll, Waker};
        let mut future = Box::pin(std::future::pending::<i32>());
        let mut context = Context::from_waker(Waker::noop());
        assert_eq!(future.as_mut().poll(&mut context), Poll::Pending);
    }

    {
        // Task 2: Guided modification
        use std::future::Future;
        use std::task::{Context, Poll, Waker};
        let left = async { 3 };
        let right = async { 4 };
        let mut combined = Box::pin(async { left.await + right.await });
        let mut context = Context::from_waker(Waker::noop());
        assert_eq!(combined.as_mut().poll(&mut context), Poll::Ready(7));
    }

    {
        // Task 5: Boundary evidence
        use std::future::Future;
        use std::task::{Context, Poll, Waker};
        struct Note<'a>(&'a std::cell::RefCell<Vec<&'static str>>);
        impl Drop for Note<'_> {
            fn drop(&mut self) {
                self.0.borrow_mut().push("dropped");
            }
        }
        let mut context = Context::from_waker(Waker::noop());
        let mut ready = Box::pin(async { 1 });
        assert_eq!(ready.as_mut().poll(&mut context), Poll::Ready(1));
        let mut waiting = Box::pin(std::future::pending::<i32>());
        assert_eq!(waiting.as_mut().poll(&mut context), Poll::Pending);
        let log = std::cell::RefCell::new(Vec::new());
        let mut unfinished = Box::pin(async {
            let _note = Note(&log);
            log.borrow_mut().push("started");
            std::future::pending::<()>().await;
            log.borrow_mut().push("finished");
        });
        assert_eq!(unfinished.as_mut().poll(&mut context), Poll::Pending);
        drop(unfinished);
        assert_eq!(*log.borrow(), vec!["started", "dropped"]);
    }
    println!("rust-033: passed");
    Ok(())
}
