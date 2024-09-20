# Persistent tasks

Persistent tasks let us set up a task that we can send messages to indepently of the async runtime. When a persistent task is executed, it sets up its internal state and returns a handle that lets us call the task with some input data. The internal state is allowed to reference managed data. The task lives until all handles have been dropped.

To create a persistent task we'll need to implement the `PersistentTask` trait. Let's implement a task that accumulates a sum of floating point numbers.

```rust,ignore
use jlrs::prelude::*;

struct AccumulatorTask {
    init_value: f64,
}

#[async_trait(?Send)]
impl PersistentTask for AccumulatorTask {
    type State<'state> = Value<'state, 'static>;
    type Input = f64;
    type Output = JlrsResult<f64>;

    async fn init<'frame>(
        &mut self,
        frame: AsyncGcFrame<'frame>,
    ) -> JlrsResult<Self::State<'frame>> {
        frame.with_local_scope::<_, _, 2>(|mut async_frame, mut local_frame| {
            let ref_ctor = Module::base(&local_frame).global(&mut local_frame, "Ref")?;
            let init_v = Value::new(&mut local_frame, self.init_value);

            // Safety: we're just calling the constructor of `Ref`, which is safe.
            let state = unsafe { ref_ctor.call1(&mut async_frame, init_v) }.into_jlrs_result()?;
            Ok(state)
        })
    }

    async fn run<'frame, 'state: 'frame>(
        &mut self,
        mut frame: AsyncGcFrame<'frame>,
        state: &mut Self::State<'state>,
        input: Self::Input,
    ) -> Self::Output {
        let getindex_func = Module::base(&frame).global(&mut frame, "getindex")?;
        let setindex_func = Module::base(&frame).global(&mut frame, "setindex!")?;

        // Safety: Calling getindex with state is equivalent to calling `state[]`.
        let current_sum = unsafe { getindex_func.call1(&mut frame, *state) }
            .into_jlrs_result()?
            .unbox::<f64>()?;

        let new_sum = current_sum + input;
        let new_value = Value::new(&mut frame, new_sum);

        // Safety: Calling setindex! with state and new_value is equivalent to calling
        // `state[] = new_value`.
        unsafe { setindex_func.call2(&mut frame, *state, new_value) }.into_jlrs_result()?;

        Ok(new_sum)
    }
}

fn main() {
    let (async_handle, thread_handle) = Builder::new()
        .n_threads(4)
        .async_runtime(Tokio::<3>::new(false))
        .spawn()
        .expect("cannot init Julia");

    let acc_task_handle = async_handle
        .persistent(AccumulatorTask { init_value: 1.0 })
        .try_dispatch()
        .expect("runtime has shut down")
        .blocking_recv()
        .expect("cannot receive result")
        .expect("AccumulatorTask::init failed");

    let recv = acc_task_handle
        .call(2.0)
        .try_dispatch()
        .expect("runtime has shut down");

    let res = recv
        .blocking_recv()
        .expect("cannot receive result")
        .expect("AccumulatorTask::run failed");

    assert_eq!(res, 3.0);

    std::mem::drop(acc_task_handle);
    std::mem::drop(async_handle);
    thread_handle.join().expect("runtime thread panicked")
}
```

When the persistent task is started by the async runtime, the `init` method is called to initialize the state of the task. In this case the state is an instance of `Ref{Float64}`, We can't use a `Float64` directly because `Float64` isn't a mutable type. Any data rooted in the async frame provided to `init` function remains rooted until the task has shut down, a local scope is used to root temporary data so we only need to root the state in the async frame.

If the task is initialized successfully a `PersistentHandle` is returned. This handle provides a `call` method which lets us call the task's `run` method with some input data. This works just like dispatching a task to the async runtime.

Like an `AsyncHandle`, a `PersistentHandle` can be cloned and shared across threads. The task shuts down when all of its handles have been dropped.
