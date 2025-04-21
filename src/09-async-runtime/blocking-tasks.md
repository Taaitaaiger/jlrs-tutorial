# Blocking tasks

Blocking tasks are the simplest kind of task, they're closures that take a `GcFrame` which are sent to the runtime thread and executed in a dynamic scope. As their name implies, when a blocking task is executed the runtime thread is blocked until the task has completed.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let (async_handle, thread_handle) = Builder::new()
        .n_threads(4)
        .async_runtime(Tokio::<3>::new(false))
        .spawn()
        .expect("cannot init Julia");

    let dispatch = async_handle
        .blocking_task(|mut frame| {
            // Safety: we're just printing a string
            unsafe { Value::eval_string(&mut frame, "println(\"Hello from the async runtime\")") }
                .expect("caught an exception");
        });

    let recv = dispatch
        .try_dispatch()
        .expect("cannot dispatch task");

    recv.blocking_recv()
        .expect("cannot receive result");

    std::mem::drop(async_handle);
    thread_handle.join().expect("runtime thread panicked")
}
```

Sending a task is a two-step process. The `AsyncHandle::blocking_task` method returns an instance of `Dispatch`, which provides sync and async methods to dispatch the task. If the backing channel is full, `Dispatch::try_dispatch` fails but returns itself as an `Err` to allow retrying later.

If the task has been dispatched successfully, the receiving half of tokio's oneshot-channel is returned which will eventually receive the result of that task.
