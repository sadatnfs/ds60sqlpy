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
    println!("rust-033: passed");
    Ok(())
}
