# Async tasks

Async tasks can call async functions, and while awaiting an async function the runtime can switch to another async task. It's possible to call any Julia function as a new Julia task with the methods of the `CallAsync` trait and await its completion. For this to be effective Julia must be configured to use multiple threads.

The easiest way to use async tasks is with an async closure. Let's implement a simple task that adds two numbers.

<!-- DOCTEST START -->
```rust,ignore
use jlrs::prelude::*;

fn main() {
        let (async_handle, thread_handle) = Builder::new()
            .n_threads(4)
            .async_runtime(Tokio::<3>::new(false))
            .spawn()
            .expect("cannot init Julia");

        let a = 1.0;
        let b = 2.0;
        let recv = async_handle
            .task(async move |mut frame: AsyncGcFrame| {
                let v1 = Value::new(&mut frame, a);
                let v2 = Value::new(&mut frame, b);
                let add_fn = Module::base(&frame)
                    .global(&mut frame, "+")
                    .expect("cannot find Base.+");

                // Safety: we're just adding two floating-point numbers
                unsafe { add_fn.call_async(&mut frame, [v1, v2]) }
                    .await
                    .expect("caught an exception")
                    .unbox::<f64>()
                    .expect("cannot unbox as f64")
            })
            .try_dispatch()
            .expect("runtime has shut down");

        let res = recv.blocking_recv().expect("cannot receive result");

        assert_eq!(res, 3.0);

        std::mem::drop(async_handle);
        thread_handle.join().expect("runtime thread panicked")
}
```
<!-- DOCTEST END -->

This is very similar to the closures we've used with scopes so far, the major difference as that it's an async and that it takes an `AsyncGcFrame` that we haven't used before.

An `AsyncGcFrame` is a `GcFrame` that provides some extra features. In particular, the methods of the `CallAsync` trait, e.g. `call_async`, don't take an arbitrary target but must be called with a mutable reference to an `AsyncGcFrame`. These methods execute a function as a new Julia task in a way that lets us await its completion, the runtime thread can switch to other tasks while it's waiting for this task to be completed.

Dispatching an async task to the runtime is very similar to dispatching a blocking task, we just need to replace `AsyncHandle::blocking_task` with `AsyncHandle::task`.

We can also use the `AsyncTask` trait. Let's express the previous example with an `AsyncTask`.

<!-- DOCTEST START -->
```rust,ignore
use jlrs::prelude::*;

struct AdditionTask {
    a: f64,
    b: f64,
}

impl AsyncTask for AdditionTask {
    type Output = f64;

    async fn run<'frame>(self, mut frame: AsyncGcFrame<'frame>) -> Self::Output {
        let v1 = Value::new(&mut frame, self.a);
        let v2 = Value::new(&mut frame, self.b);
        let add_fn = Module::base(&frame)
            .global(&mut frame, "+")
            .expect("cannot find Base.+");

        // Safety: we're just adding two floating-point numbers
        unsafe { add_fn.call_async(&mut frame, [v1, v2]) }
            .await
            .expect("caught an exception")
            .unbox::<f64>()
            .expect("cannot unbox as f64")
    }
}

fn main() {
    let (async_handle, thread_handle) = Builder::new()
        .n_threads(4)
        .async_runtime(Tokio::<3>::new(false))
        .spawn()
        .expect("cannot init Julia");

    let recv = async_handle
        .task(AdditionTask { a: 1.0, b: 2.0 })
        .try_dispatch()
        .expect("runtime has shut down");

    let res = recv
        .blocking_recv()
        .expect("cannot receive result");

    assert_eq!(res, 3.0);

    std::mem::drop(async_handle);
    thread_handle.join().expect("runtime thread panicked")
}
```
<!-- DOCTEST END -->
