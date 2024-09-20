# Dynamic targets

A `GcFrame` is a dynamically-sized alternative for `LocalGcFrame`. With a `GcFrame` we avoid having to count how many slots we'll need.

We'll first need to set up a dynamic stack. This is a matter of calling `WithStack::with_stack`, the `WithStack` trait is implemented for `LocalHandle`. Like `LocalGcFrame`, there are two secondary targets which reserve a slot, `Output` and `ReusableSlot`. They behave exactly the same as their local counterparts do.

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

        // Safety: calling + is safe
        unsafe { func.call2(target, a, b) }
    })
}

fn main() {
    let mut handle = Builder::new().start_local().expect("cannot init Julia");

    handle.with_stack(|mut stack| {
        stack.scope(|mut frame| {
            let mut output = frame.output();
            let mut reusable_slot = frame.reusable_slot();

            {
                // This result can be used until the next time `(&mut) output` is used
                let result = add(&mut output, 1, 2).expect("could not add numbers");
                let unboxed = result.unbox::<u8>().expect("cannot unbox as u8");
                assert_eq!(unboxed, 3);
            }

            {
                // This result can be used until the scope ends
                let result = add(output, 1, 2).expect("could not add numbers");
                let unboxed = result.unbox::<u8>().expect("cannot unbox as u8");
                assert_eq!(unboxed, 3);
            }

            {
                // This result can be used until the scope ends, but must not be used after
                // `reusable_slot` has been used again. Because the result can live longer
                // than it might be rooted, it's returned as a `ValueRef`.
                let result = add(&mut reusable_slot, 1, 2).expect("could not add numbers");

                // Safety: result is rooted until we use reusable_slot again
                let unboxed = unsafe { result.as_value() }.unbox::<u8>().expect("cannot unbox as u8");
                assert_eq!(unboxed, 3);
            }

            {
                // This result can be used until the scope ends
                let result = add(reusable_slot, 1, 2).expect("could not add numbers");
                let unboxed = result.unbox::<u8>().expect("cannot unbox as u8");
                assert_eq!(unboxed, 3);
            }
        })
    })
}
```

While a dynamic scope can be nested like a local scope can, this can only be done by calling `GcFrame::scope`. Due to requiring a stack, it's not possible to let an arbitrary target create a new dynamic scope.[^1] Allocating and resizing this stack is relatively expensive, and threading it through our application can be complicated, so it's best to stick with local scopes.

There's one more dynamic target: `AsyncGcFrame`. It's a `GcFrame` with some additional async capabilities, we'll take a closer look when the async runtime is introduced.

[^1]: Technically it's possible by creating a weak handle, but this is discouraged because setting up the dynamic stack is relatively expensive.
