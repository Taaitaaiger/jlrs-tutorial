# Async runtime

The async runtime lets us run Julia on a background thread, its handle lets us send tasks to this thread. We need to enable the `async-rt` feature to use it. Some tasks support async operations, so we'll also need an async executor. A tokio-based executor is available when the `tokio-rt` feature is enabled, this feature automatically enables `async-rt` as well.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let (async_handle, thread_handle) = Builder::new()
        .n_threads(4)
        .async_runtime(Tokio::<3>::new(false))
        .spawn()
        .expect("cannot init Julia");

    std::mem::drop(async_handle);
    thread_handle.join().expect("runtime thread panicked")
}
```

We've configured Julia to use 4 threads.[^1] The builder is upgraded to an `AsyncBuilder` by providing it with the necessary configuration. Here we've configure the runtime to use the tokio-based executor without the I/O driver, and to support 3 concurrent tasks.[^2] If you want to use this driver, enable the `tokio-net` feature and change the argument of `Tokio::new` to `true`.

By default, an unbounded channel is used to let the handles communicate with the runtime thread. A bounded channel can be used by calling `AsyncBuilder::channel_capacity` before spawning the runtime.

After spawning the runtime, we get an `AsyncHandle` that we can use to interact with the runtime thread and a `JoinHandle` to that thread. The runtime thread shuts down when all `AsyncHandle`s have been dropped. It's also possible to manually shut down the runtime by calling `AsyncHandle::close`.

[^1]: Since Julia 1.9 these threads belong to Julia's default thread pool, we can also configure the number of interactive threads with `(Async)Builder::n_interactive_threads`.

[^2]: Multiple tasks that support async operations can be executed concurrently, the runtime can switch to another task while waiting for an async operation to complete. Tasks are not executed in parallel, all tasks are executed on the single runtime thread.
