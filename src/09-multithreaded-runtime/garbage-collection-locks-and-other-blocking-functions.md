# Garbage collection, locks, and other blocking functions

Way back when we first discussed managed data and rooting, it was said that the GC can be triggered by allocating managed data. When the GC is triggered by some thread, that thread will block until all other threads that can call into Julia have reached a safepoint. A safepoint is normally reached by allocating managed data, recent versions of Julia will also reach one when a Julia function is called. When a safepoint is reached, the thread promises that all managed data it still needs to use is rooted, or at least reachable from a root.

This isn't a problem if only one thread is used, but can easily become an issue when multiple threads can call into Julia. The problem is most obvious with locks. Let's say we have the following situation: thread A and B can call into Julia, these threads acquire a lock and allocate some Julia data. If one of the threads triggers the garbage collector while the other thread is waiting for the lock we run into a deadlock situation. The other thread will never hit a safepoint because it's waiting on a lock that will never be released.

To solve this particular issue, jlrs provides several GC-safe lock types. GC-safe means that it is safe to run the GC even without hitting an explicit safepoint. If we use GC-safe locks in the problem above, the deadlock is resolved because the GC can run while we wait for the lock. The following GC-safe locks are provided:

- `GcSafeMutex`
- `GcSafeFairMutex`
- `GcSafeRwLock`
- `GcSafeOnceLock`

These GC-safe alternatives are adapted from similarly-named types found in parking_lot and once_cell, the only difference is that blocking operations are called in a GC-safe block.

A similar issue arises if we call arbitrary long-running code that doesn't all into Julia: it doesn't reach a safepoint, if the GC needs to run it needs to wait until this operation has completed. Since the operation doesn't need to call into Julia, it's safe to execute it in a GC-safe block. We can use the `gc_safe` function to do so, it's unsound to interact with Julia any way inside a GC-safe block.

```rust,ignore
use std::{thread, time::Duration};

use jlrs::{memory::gc::gc_safe, prelude::*, runtime::builder::Builder};

fn long_running_op() {
    thread::sleep(Duration::from_secs(5));
}

fn main() {
    let (mut mt_handle, thread_handle) = Builder::new().spawn_mt().expect("cannot init Julia");
    let mut mt_handle2 = mt_handle.clone();

    let t1 = thread::spawn(move || {
        mt_handle.with(|handle| {
            handle.local_scope::<_, 1>(|mut frame| {
                // Safety: long_running_op doesn't interact with Julia
                unsafe { gc_safe(long_running_op) };

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
