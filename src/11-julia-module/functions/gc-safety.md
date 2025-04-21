# GC-safety

All the examples we've seen involve trivial code that takes almost no time to run. In realistic scenario's, though, there's a good chance we want to call a function that doesn't call into Julia and takes a long time to run. If we don't call into Julia we won't hit any safepoints. This is a problem if we use multiple threads; if the GC needs to run, any thread that hits a safepoint will wait there until the GC is done, so if one thread is not hitting any safepoints, the other threads will quickly be blocked.

A thread that can call into Julia is normally in a GC-unsafe state, the unsafe here means that the GC must wait until the thread has reached a safepoint before it can run. We can also put it in a GC-safe state where the GC can assume the thread won't call into Julia and doesn't need to wait until that thread has reached a safepoint.

If an exported function doesn't need to call into Julia at all, we can ensure it's called in a GC-safe state by annotating the export with `#[gc_safe]`. To simulate a long-running function we're going to sleep for a few seconds.

```rust,ignore
use std::{thread::sleep, time::Duration};

use jlrs::prelude::*;

fn add(a: f64, b: f64) -> f64 {
    sleep(Duration::from_secs(5));
    a + b
}

julia_module! {
    become julia_module_tutorial_init_fn;

    #[gc_safe]
    fn add(a: f64, b: f64) -> f64;
}
```

We can manually create gc-safe blocks.

```rust,ignore
use std::{thread::sleep, time::Duration};

use jlrs::{data::managed::array::TypedVectorRet, memory::gc::gc_safe, prelude::*, weak_handle};

fn some_operation(len: usize) -> TypedVectorRet<f64> {
    match weak_handle!() {
        Ok(handle) => {
            // Safety: we don't call into Julia in this GC-safe block
            let data = unsafe {
                gc_safe(|| {
                    sleep(Duration::from_secs(5));
                    vec![0.0f64; len]
                })
            };

            TypedVector::from_vec(handle, data, len)
                .expect("size invalid")
                .expect("caught exception")
                .leak()
        }
        _ => panic!("not called from Julia"),
    }
}

julia_module! {
    become julia_module_tutorial_init_fn;

    fn some_operation(len: usize) -> TypedVectorRet<f64>;
}
```

It's possible to revert to a GC-unsafe state in a GC-safe block by inserting a GC-unsafe block with `gc_unsafe`.

```rust,ignore
use std::{thread::sleep, time::Duration};

use jlrs::{
    data::managed::array::TypedVectorRet,
    memory::gc::{gc_safe, gc_unsafe},
    prelude::*,
};

fn some_operation(len: usize) -> TypedVectorRet<f64> {
    // Safety: we don't call into Julia in this GC-safe block except in the GC-unsafe block
    unsafe {
        gc_safe(|| {
            sleep(Duration::from_secs(5));
            let data = vec![0.0f64; len];

            gc_unsafe(|unrooted| {
                TypedVector::from_vec(unrooted, data, len)
                    .expect("size invalid")
                    .expect("caught exception")
                    .leak()
            })
        })
    }
}

julia_module! {
    become julia_module_tutorial_init_fn;

    fn some_operation(len: usize) -> TypedVectorRet<f64>;
}
```
