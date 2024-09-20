# Using targets and nested scopes

Functions that take a target do so by value, which means the target can only be used once.[^1] If we call such a function with `&mut frame`, only one slot of that frame will be used to root the result. This keeps counting the number of slots we need as easy as possible because we only need to count the number of times the frame is used as a target inside the closure.

This does raise an obvious question: what if the function that takes a target needs to root more than one value? The answer is that targets let us create a nested scope.

```rust,ignore
use jlrs::prelude::*;

fn add<'target, Tgt>(target: Tgt, a: u8, b: u8) -> ValueResult<'target, 'static, Tgt>
where
    Tgt: Target<'target>,
{
    target.with_local_scope::<_, _, 3>(|target, mut frame| {
        let a = Value::new(&mut frame, a);
        let b = Value::new(&mut frame, b);
        let func = Module::base(&frame)
            .global(&mut frame, "+")
            .expect("+ not found in Base");

        // Safety: calling + is safe.
        unsafe { func.call2(target, a, b) }
    })
}

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 1>(|mut frame| {
        let result = add(&mut frame, 1, 2).expect("could not add numbers");
        let unboxed = result.unbox::<u8>().expect("cannot unbox as u8");
        assert_eq!(unboxed, 3);
    });
}
```

This approach helps avoid rooting managed data longer than necessary. After calling `add`, only its result is rooted. The temporary values we created in that function are no longer rooted because we've left its scope.

It's strongly recommended to avoid writing functions that take a specific target type, and always take a target generically.

[^1]: Some functions take a target by immutable reference and return rooted data. This data is guaranteed to be globally rooted, and the operation won't consume the target.