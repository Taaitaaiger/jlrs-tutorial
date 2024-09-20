# Managed data and functions

In the previous section we printed `"Hello, World!"` from Julia by evaluating `println("Hello, World!")`. While there's a lot we can achieve by using Julia this way, it's inflexible and has many limitations. One of these limitations is that, modulo string formatting and other gnarly work-arounds, we can't change the argument `println` is called with.

What we really want to do is call Julia functions with arbitrary arguments. Let's start with `println(1)`.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 3>(|mut frame| {
        let one = Value::new(&mut frame, 1usize);
        let println_fn = Module::base(&frame)
            .global(&mut frame, "println")
            .expect("println not found in Base");

        // Safety: calling println with an integer is safe
        unsafe { println_fn.call1(&mut frame, one).expect("println threw an exception") };
    });
}
```

The capacity of the frame is set to `3` because `&mut frame` is used three times to root managed data.

The first use of the frame happens in the call to `Value::new`, which converts data from Rust to Julia. Julia calls this boxing, to avoid confusion with boxing in Rust we'll call it "creating a value" or "converting to managed data" instead. Any type that implements `IntoJulia` can be converted to managed data with this function, jlrs provides implementations of this trait for primitive types, pointer types, and tuples with 32 or fewer fields.

Most functions are globals in a module, `println` is defined in the `Base` module. Julia modules can be accessed via the `Module` type, which is a managed type just like `Value`. The functions `Module::base` and `Module::main` provide access to the `Base` and `Main` modules respectively. These functions take an immutable reference to a frame to prevent them from existing outside a scope, but they don't need to be rooted and this doesn't count as a use of the frame. Globals in Julia modules can be accessed with `Module::global`, we use the frame a second time when we call this method to root its result.[^1]

Finally we call `println_fn` with the frame and one argument. This is the third and last use of the frame. Any `Value` is potentially callable, the `Call` trait provides methods to call them with any number of arguments. Specialized methods like `Call::call1` exist to call functions with 3 or fewer arguments, `Call::call` accepts an arbitrary number of arguments. Every argument must be a `Value`.

Calling Julia functions is unsafe for mostly the same reason as evaluating Julia code is, nothing prevents us from calling `unsafe_load` with a wild pointer. Other risks involve thread-safety and mutably aliasing data that is directly accessed from Rust, which can't be statically prevented. In practice, most Julia code is as safe to call from Rust as it is from Julia.

One thing that should be noted is that while calling a function is more efficient than evaluating Julia code, each argument is passed as a `Value`. This means every function call involves dynamically dispatching to the appropriate method, which can cause significant overhead if we call small functions. In practice it's best to do as much as possible in Julia, and keep the code necessary to call it from Rust as simple as possible. This gives Julia the opportunity to optimize, and we avoid the verbosity of the low-level interfaces jlrs exposes.

All of that said, we didn't want to print `1`, we wanted to print `Hello, World!`. If we tried the most obvious thing and replaced `1usize` in the code above with `"Hello, World!"`, we'd see that this would fail to compile because `&str` doesn't implement `IntoJulia`. We need to use another managed type, `JuliaString`, which maps to Julia's `String` type.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 3>(|mut frame| {
        let s = JuliaString::new(&mut frame, "Hello, World!").as_value();
        let println_fn = Module::base(&frame)
            .global(&mut frame, "println")
            .expect("println not found in Base");

        // Safety: calling println with a string is safe
        unsafe { println_fn.call1(&mut frame, s).expect("println threw an exception") };
    });
}
```

So far we've encountered three managed types, `Value`, `Module`, and `JuliaString`, we'll see several more in the future. All managed types implement the `Managed` trait and have at least one lifetime that encodes their scope, the method `Managed::as_value` can be used to convert managed data to a `Value`.

[^1]: We didn't need to use the frame a second time here, but that's outside the scope of this chapter.
