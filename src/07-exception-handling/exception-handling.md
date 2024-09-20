# Exception handling

Many functions in Julia can throw exceptions, including low-level functions exposed by jlrs. Examples include calling a Julia function with incorrect arguments and trying to allocate a ridiculously-sized array. These functions are typically exposed twice: as a function that catches exceptions, and one that doesn't.

The function that doesn't catch the exception is always unsafe. Julia exceptions are implemented with `longjmp`, when an exception is thrown control flow jumps to the nearest enclosing catch block, so we must guarantee we don't jump over any pending drops. We can call arbitrary functions in a try-block with a custom exception handler with the `catch_exceptions` function, but this remains unsafe because we still have to guarantee we don't jump over any drops. It's fine to jump out of some deeply nested scope as long as any frame that is jumped over is a ["Plain Old Frame"].

If an exception is thrown and there is no handler available, Julia aborts the process.

```rust,ignore
use jlrs::{catch::catch_exceptions, prelude::*};

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    // Safety: we don't jump over any pending drops if an exception is thrown.
    handle.local_scope::<_, 1>(|mut frame| unsafe {
        catch_exceptions(
            || {
                TypedArray::<u8>::new_unchecked(&mut frame, (usize::MAX, usize::MAX));
            },
            |e| {
                println!("caught exception: {e:?}")
            },
        ).expect_err("allocated ridiculously-sized array successfully");
    });
}
```

This example should print `caught exception: ArgumentError("invalid Array dimensions")`.

["Plain Old Frame"]: https://github.com/rust-lang/rfcs/blob/master/text/2945-c-unwind-abi.md#plain-old-frames
