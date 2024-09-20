# Caching Julia data

Accessing data in a module can be expensive, especially if we need to access it often. These accesses can be cached with a `StaticRef`, which can be defined with the `define_static_ref!` macro and accessed with the `static_ref!` macro.

```rust,ignore
use jlrs::{define_static_ref, prelude::*, static_ref};

define_static_ref!(ADD_FUNCTION, Value, "Base.+");

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 3>(|mut frame| {
        let v1 = Value::new(&mut frame, 1.0f64);
        let v2 = Value::new(&mut frame, 2.0f64);

        let add_func = static_ref!(ADD_FUNCTION, &frame);
        let res = unsafe { add_func.call2(&mut frame, v1, v2) }
            .expect("caught an exception")
            .unbox::<f64>()
            .expect("wrong type");

        assert_eq!(res, 3.0);
    })
}
```

It's possible to combine these two operations with `inline_static_ref!`, this is useful if we only need to use the data in a single function or want to expose a separate function to access it.

```rust,ignore
use jlrs::{inline_static_ref, prelude::*};

#[inline]
fn add_function<'target, Tgt>(target: &Tgt) -> Value<'target, 'static>
where
    Tgt: Target<'target>,
{
    inline_static_ref!(ADD_FUNCTION, Value, "Base.+", target)
}

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 3>(|mut frame| {
        let v1 = Value::new(&mut frame, 1.0f64);
        let v2 = Value::new(&mut frame, 2.0f64);

        let add_func = add_function(&frame);
        let res = unsafe { add_func.call2(&mut frame, v1, v2) }
            .expect("caught an exception")
            .unbox::<f64>()
            .expect("wrong type");

        assert_eq!(res, 3.0);
    })
}
```

A `StaticRef` is thread-safe: it's just an atomic pointer internally, which is initialized when it's first accessed. Any thread that can call into Julia can access it, if multiple threads try to access this data before it has been initialazed, all these threads will try to initialize it. The data is globally rooted so we don't need to root it ourselves.[^1]

[^1]: One thing that's important to remember is that mutation can cause previously global data to become unreachable. It's our responsibility to guarantee we never change a global that's exposed as a `StaticRef`.
