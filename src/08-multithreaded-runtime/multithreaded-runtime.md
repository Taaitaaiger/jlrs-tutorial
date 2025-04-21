# Multithreaded runtime

In all examples so far we've used the local runtime, which is limited to a single thread. The multithreaded runtime can be used from any thread, this feature requires enabling the `multi-rt` feature.

Using the multithreaded runtime instead of the local runtime is mostly a matter of starting the runtime differently.

```rust,ignore
use jlrs::{prelude::*, runtime::builder::Builder};

fn main() {
    Builder::new().start_mt(|mt_handle| {
        let t1 = mt_handle.spawn(move |mut mt_handle| {
            mt_handle.with(|handle| {
                handle.local_scope::<1>(|mut frame| {
                    // Safety: we're just printing a string
                    unsafe { Value::eval_string(&mut frame, "println(\"Hello from thread 1\")") }
                        .expect("caught exception");
                })
            })
        });

        let t2 = mt_handle.spawn(move |mut mt_handle| {
            mt_handle.with(|handle| {
                handle.local_scope::<1>(|mut frame| {
                    // Safety: we're just printing a string
                    unsafe { Value::eval_string(&mut frame, "println(\"Hello from thread 2\")") }
                        .expect("caught exception");
                })
            })
        });

        t1.join().expect("thread 1 panicked");
        t2.join().expect("thread 2 panicked");
    }).expect("cannot init Julia");
}
```

Julia is initialized on the current thread when `start_mt` is called, the closure is called on a new thread. This method returns an `MtHandle` that we can use to call into Julia. The `MtHandle` can be cloned, we can create new scoped threads with `MtHandle::spawn`, and by calling `MtHandle::with` the thread is temporarily put into a state where it can create scopes and call into Julia. The runtime thread shuts down when all `MtHandle`s have been dropped.
