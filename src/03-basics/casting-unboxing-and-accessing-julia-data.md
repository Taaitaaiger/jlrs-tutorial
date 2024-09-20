# Casting, unboxing and accessing managed data

So far, the only Julia function we've called is `println`, which isn't particularly interesting because it returns `nothing`. In practice, we often don't just want to call Julia functions for their side-effects, we also want to use their results in Rust.

A `Value` is an instance of some Julia type, managed by the GC. If there's a more specific managed type for that Julia type, we can convert the `Value` by casting it with `Value::cast`.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 1>(|mut frame| {
        let s = JuliaString::new(&mut frame, "Hello, World!").as_value();
        assert!(s.cast::<JuliaString>().is_ok());

        let module = Module::main(&frame).as_value();
        assert!(module.cast::<Module>().is_ok());
        assert!(module.cast::<JuliaString>().is_err());
    });
}
```

Managed types aren't the only types that map between Rust and Julia. There are many types where the layout in Rust matches the layout of the managed data, including most primitive types. These types implement the `Unbox` trait which lets us extract the data from the `Value` with `Value::unbox`.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 1>(|mut frame| {
        let one = Value::new(&mut frame, 1usize);
        let unboxed = one.unbox::<usize>().expect("cannot be unboxed as usize");
        assert_eq!(unboxed, 1);
    });
}
```

If there's no appropriate type that implements `Unbox` or `Managed`, we can access the fields of a `Value` manually.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 4>(|mut frame| {
        // Normally, this custom type would have been defined in some module.
        // Safety: Defining a new type is safe.
        let custom_type = unsafe {
            Value::eval_string(
                &mut frame,
                "struct CustomType
                    a::UInt8
                    b::Bool
                    CustomType() = new(0x1, false)
                end

                CustomType",
            )
            .expect("cannot create CustomType")
        };

        // Safety: the constructor of CustomType is safe to call
        let inst = unsafe {
            custom_type
                .call0(&mut frame)
                .expect("cannot call constructor of CustomType")
        };

        let a = inst.get_field(&mut frame, "a")
            .expect("no field named a")
            .unbox::<u8>()
            .expect("cannot unbox as u8");

        assert_eq!(a, 1);

        let b = inst.get_field(&mut frame, "b")
            .expect("no field named b")
            .unbox::<Bool>()
            .expect("cannot unbox as Bool")
            .as_bool();

        assert_eq!(b, false);
    });
}
```

There's a lot going on in this example, but a lot of it is just setup code. We first evaluate some Julia code that defines `CustomType`. Constructors in Julia are just functions linked to a type, so we can call `CustomType`'s constructor by calling the result of the code we've evaluated. Finally, we get to the point and use `Value::get_field` to access the fields before unboxing their content.[^1] The second field is unboxed as a `Bool`, not a `bool`. The Julia `Char` type similarly maps to jlrs's `Char` type. These types exist to avoid any potential mismatches between Rust and Julia.

[^1]: `Value::get_field` accesses a field by name, if we had wanted to access a field of a tuple we would have needed to do so by index with `Value::get_nth_field`. Indexing starts at 0.
