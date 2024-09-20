# When to leave things unrooted

In this tutorial we've mostly used rooting targets to ensure the managed data we created would remain valid as long as we didn't leave the scope it was tied to. In many cases, though, we don't need to root managed data and can use a non-rooting target without running into any problems.

Some data is globally rooted, most importantly constants defined in modules. When we access such constant data with `Module::get_global`, we can safely skip rooting it and convert the `Ref`-type to a managed type if we want to use it. If the data is global but not constant, it's safe to use it without rooting it if we can guarantee its value never changes as long as we use it from Rust.

If a function returns an instance of a zero-sized type like `nothing` we don't need to root the result; there's only one, globally-rooted instance of a zero-sized type. Symbols and instances of booleans and 8-bit integers are also globally rooted.

Finally, it's safe to leave data unrooted if we can guarantee the GC won't run until we're done using the data. The GC can be triggered whenever new managed data is allocated.[^1] If the GC determines it needs to run, every thread will be suspended when it reaches a safepoint. The GC runs when all threads have been suspended. If we don't call into Julia while we access the data, we won't hit a safepoint so we can leave it unrooted.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 1>(|mut frame| {
        let func = Module::base(&frame)
            .global(&frame, "println")
            .expect("cannot find println in Base");

        // Safety: println is globally rooted
        let func = unsafe { func.as_value() };

        let a = Value::new(&mut frame, 1.0);

        // Safety: We're just calling println with a Float64 argument
        let res = unsafe { func.call1(&frame, a).expect("caught exception") };

        // Safety: println returns nothing, which is globally rooted
        let res = unsafe { res.as_value() };
        assert!(res.is::<Nothing>());
    });
}
```

[^1]: The GC can also be triggered manually with `Gc::gc_collect`, all targets implement this trait.
