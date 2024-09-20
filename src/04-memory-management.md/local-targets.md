# Local targets

The frame we've use so far is a `LocalGcFrame`. It's called local because all roots are stored locally on the stack, which is why we need to know its size at compile time.

Every time we root data by using a mutable reference to a `LocalGcFrame` we consume one of its slots. It's also possible to reserve a slot as a `LocalOutput` or `LocalReusableSlot`, they can be created by calling `LocalGcFrame::local_output` and `LocalGcFrame::local_reusable_slot`. These methods consume a slot. The main difference between the two is that `LocalReusableSlot` is a bit more permissive with the lifetime of the result at the cost of returning an unrooted reference. They're useful if we need to return multiple instances of managed data from a scope, or want to reuse a slot inside one.

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
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 2>(|mut frame| {
        let mut output = frame.local_output();
        let mut reusable_slot = frame.local_reusable_slot();

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

            // Safety: result is rooted until we use `reusable_slot` again
            let unboxed = unsafe { result.as_value() }.unbox::<u8>().expect("cannot unbox as u8");
            assert_eq!(unboxed, 3);
        }

        {
            // This result can be used until the scope ends
            let result = add(reusable_slot, 1, 2).expect("could not add numbers");
            let unboxed = result.unbox::<u8>().expect("cannot unbox as u8");
            assert_eq!(unboxed, 3);
        }
    });
}
```

An `UnsizedLocalGcFrame` is similar to a `LocalGcFrame`, the major difference is that its size isn't required to be known at runtime. If the size of the frame is statically known, use `LocalGcFrame`.

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
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.unsized_local_scope(2, |mut frame| {
        let mut output = frame.local_output();
        let mut reusable_slot = frame.local_reusable_slot();

        {
            let result = add(&mut output, 1, 2).expect("could not add numbers");
            let unboxed = result.unbox::<u8>().expect("cannot unbox as u8");
            assert_eq!(unboxed, 3);
        }

        {
            let result = add(output, 1, 2).expect("could not add numbers");
            let unboxed = result.unbox::<u8>().expect("cannot unbox as u8");
            assert_eq!(unboxed, 3);
        }

        {
            let result = add(&mut reusable_slot, 1, 2).expect("could not add numbers");

            // Safety: result is rooted until we use `reusable_slot` again
            let unboxed = unsafe { result.as_value() }.unbox::<u8>().expect("cannot unbox as u8");
            assert_eq!(unboxed, 3);
        }

        {
            let result = add(reusable_slot, 1, 2).expect("could not add numbers");
            let unboxed = result.unbox::<u8>().expect("cannot unbox as u8");
            assert_eq!(unboxed, 3);
        }
    })
}
```
