# Combining the multithreaded and async runtimes

It's possible to combine the functionality of the multithreaded and async runtimes.

The `AsyncBuilder` provides `start_mt` and `spawn_mt` methods that let us use both an `MtHandle` and an `AsyncHandle` when both the `async-rt` and `multi-rt` features have been enabled. The  `AsyncHandle` lets us send tasks to the main runtime thread, which is useful if we have some code that we must be called from that thread.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let (mt_handle, async_handle, thread_handle) = Builder::new()
        .n_threads(4)
        .async_runtime(Tokio::<3>::new(false))
        .spawn_mt()
        .expect("cannot init Julia");

    std::mem::drop(async_handle);
    std::mem::drop(mt_handle);
    thread_handle.join().expect("runtime thread panicked")
}
```

We can also create thread pools where each worker thread can call into Julia and runs an async runtime.[^1] We can configure and create new pools with `MtHandle::pool_builder`. When a pool is spawned, an `AsyncHandle` to the pool is returned. Taslks are sent to this pool instead of a specific thread, it can be handled by any of its workers. If a worker dies due to a panic a new worker is automatically spawned.[^2]

Workers can be dynamically added and removed with `AsyncHandle::try_add_worker` and `AsyncHandle::try_remove_worker`. The pool shuts down when all workers have been removed, all handles have been dropped, or if its closed explicitly. It's not possible to add workers to the async runtime itself, only to pools.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let (mt_handle, thread_handle) = Builder::new()
        .n_threads(4)
        .spawn_mt()
        .expect("cannot init Julia");

    let pool_handle = mt_handle
        .pool_builder(Tokio::<3>::new(false))
        .n_workers(3.try_into().unwrap())
        .spawn();

    assert!(pool_handle.try_add_worker());
    assert!(pool_handle.try_remove_worker());

    std::mem::drop(pool_handle);
    std::mem::drop(mt_handle);
    thread_handle.join().expect("runtime thread panicked")
}
```

One additional advantage that pools have over the async runtime thread is that the latency is typically much lower. If we don't need code to run on the main thread specifically, it's more effective to use the multithreaded runtime and create a pool instead.

[^1]: More precisely, not an async runtime but an instance of an executor.

[^2]: While it's still recommended to abort on panics, it's safe to panic on a worker thread as long as we don't unwind into Julia code by panicking in a function called with `ccall`.
