# Multithreaded runtime

In all examples so far we've used the local runtime, which is limited to a single thread. The multithreaded runtime can be used from any thread, this feature requires using at least Julia 1.9 and enabling the `multi-rt` feature.

Using the multithreaded runtime instead of the local runtime is mostly a matter of starting the runtime differently.

```rust,ignore
use std::thread;

use jlrs::{prelude::*, runtime::builder::Builder};

fn main() {
    let (mut mt_handle, thread_handle) = Builder::new().spawn_mt().expect("cannot init Julia");
    let mut mt_handle2 = mt_handle.clone();

    let t1 = thread::spawn(move || {
        mt_handle.with(|handle| {
            handle.local_scope::<_, 1>(|mut frame| {
                // Safety: we're just printing a string
                unsafe { Value::eval_string(&mut frame, "println(\"Hello from thread 1\")") }
                    .expect("caught exception");
            })
        })
    });

    let t2 = thread::spawn(move || {
        mt_handle2.with(|handle| {
            handle.local_scope::<_, 1>(|mut frame| {
                // Safety: we're just printing a string
                unsafe { Value::eval_string(&mut frame, "println(\"Hello from thread 2\")") }
                    .expect("caught exception");
            })
        })
    });

    t1.join().expect("thread 1 panicked");
    t2.join().expect("thread 2 panicked");
    thread_handle.join().expect("runtime thread panicked")
}
```

Julia is initialized on a background thread when `spawn_mt` is called. This method returns an `MtHandle` that we can use to call into Julia and a handle to the runtime thread. The `MtHandle` can be cloned and sent to other threads, by calling `MtHandle::with` the thread is temporarily put into a state where it can create scopes and call into Julia. The runtime thread shuts down when all `MtHandle`s have been dropped.

Instead of spawning the runtime thread, we can also initialize Julia on the current thread and spawn a new thread that can use an `MtHandle`:

```rust,ignore
use std::thread;

use jlrs::{
    prelude::*,
    runtime::{builder::Builder, handle::mt_handle::MtHandle},
};

fn main_inner(mut mt_handle: MtHandle) {
    let mut mt_handle2 = mt_handle.clone();

    let t1 = thread::spawn(move || {
        mt_handle.with(|handle| {
            handle.local_scope::<_, 1>(|mut frame| {
                // Safety: we're just printing a string
                unsafe { Value::eval_string(&mut frame, "println(\"Hello from thread 1\")") }
                    .expect("caught exception");
            })
        })
    });

    let t2 = thread::spawn(move || {
        mt_handle2.with(|handle| {
            handle.local_scope::<_, 1>(|mut frame| {
                // Safety: we're just printing a string
                unsafe { Value::eval_string(&mut frame, "println(\"Hello from thread 2\")") }
                    .expect("caught exception");
            })
        })
    });

    t1.join().expect("thread 1 panicked");
    t2.join().expect("thread 2 panicked");
}

fn main() {
    Builder::new().start_mt(main_inner).expect("cannot init Julia");
}
```

This is useful if we interact with code in Julia that is picky about being called from the main application thread, e.g. code involving Qt.
