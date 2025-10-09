# Testing applications

When we test a binary crate that embeds Julia we have to keep in mind that Julia can only be initialized once. The easiest way to ensure this is by limiting ourselves to integration tests in a separate `tests` directory, and defining a single test per file. Each file in the `tests` directory is executed in a separate process, the single test ensures we only use Julia from a single thread.[^1] This approach applies to all runtimes.

```rust,ignore
use jlrs::prelude::*;

fn test_case_1<'target, Tgt: Target<'target>>(_target: &Tgt) {}

fn test_case_2<'target, Tgt: Target<'target>>(_target: &Tgt) {}

#[test]
fn test_fn() {
    let handle = Builder::new().start_local().expect("cannot init Julia");
    handle.local_scope::<_, 0>(|frame| {
        test_case_1(&frame);
        test_case_2(&frame);
    });
}
```

This restriction doesn't apply to doctests, each doctest runs in a separate process.

[^1]: Setting `--test-threads=1` doesn't allow multiple tests per file, the different tests would run sequentially but do so from different threads.
