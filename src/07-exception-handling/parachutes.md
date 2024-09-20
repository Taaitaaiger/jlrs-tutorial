# Parachutes

If we can't avoid data that must be dropped, it might be possible to attach a parachute to this data to ensure it's dropped safely even if an exception is thrown. When we attach a parachute to data, we move it from Rust to Julia by converting it to managed data, which makes the GC responsible for dropping it.

A parachute can be attached by calling `AttachParachute::attach_parachute`, this trait is implemented for any type that is `Sized + Send + Sync + 'static`. The resulting `WithParachute` derefences to the original type, the parachute can be removed by calling `WithParachute::remove_parachute`.

```rust,ignore
use jlrs::{catch::catch_exceptions, data::managed::parachute::AttachParachute, prelude::*};

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 2>(|mut frame| {
        // Safety: this is a POF. We attach a parachute to vec
        // to make the GC responsible for dropping it.
        unsafe {
            catch_exceptions(
                || {
                    let dims = (usize::MAX, usize::MAX);
                    let vec = vec![1usize];
                    let mut with_parachute = vec.attach_parachute(&mut frame);
                    let arr = TypedArray::<u8>::new_unchecked(&mut frame, dims);
                    with_parachute.push(2);
                    arr
                },
                |e| println!("caught exception: {e:?}"),
            )
        }
        .expect_err("allocated ridiculously-sized array successfully");
    });
}
```

We've attached a parachute to `vec` so it's fine that the next line throws an exception. The GC will eventually take care of dropping it for us.
