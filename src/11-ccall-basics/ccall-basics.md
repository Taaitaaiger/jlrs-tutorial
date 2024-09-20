# ccall basics

So far we've focussed on calling Julia from Rust by embedding Julia in a Rust application, in this chapter we start with the other side of the story: calling Rust from Julia. One of the nice features of Julia is its `ccall` interface, which can call functions that use the C ABI, including `extern "C"` functions in Rust.[^1] Most of this chapter won't use jlrs, Julia can load arbitrary dynamic libraries at runtime.

The intent of this chapter is to cover some essential information about `ccall`. For more in-depth information, read the [Calling C and Fortran Code] chapter in the Julia manual.

To get started with calling into Rust from Julia, we're going to look at a final embedding example first before creating our first dynamic library. We'll expose a function pointer to Julia and call it with `ccall`.

```rust,ignore
use std::ffi::c_void;

use jlrs::prelude::*;

unsafe extern "C" fn add(a: f64, b: f64) -> f64 {
    a + b
}

static JULIA_CODE: &str = "function call_rust(ptr::Ptr{Cvoid}, a::Float64, b::Float64)
    ccall(ptr, Float64, (Float64, Float64), a, b)
end";

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 5>(|mut frame| {
        let ptr = Value::new(&mut frame, add as *mut c_void);

        let a = Value::new(&mut frame, 1.0f64);
        let b = Value::new(&mut frame, 2.0f64);

        // Safety: we're just defining a function.
        let func = unsafe { Value::eval_string(&mut frame, JULIA_CODE) }
            .expect("an exception occurred");

        // Safety: Immutable types are passed and returned by value, so `add`
        // has the correct signature for the `ccall` in `call_rust`. All
        // `add` does is add `a` and `b`, which is perfectly safe.
        let res = unsafe { func.call3(&mut frame, ptr, a, b) }
            .expect("an exception occurred")
            .unbox::<f64>()
            .expect("not an f64");

        assert_eq!(res, 3.0f64);
    });
}
```

All this example does is call `add`, which adds two numbers and returns the result. We can convert this function to `Value` by converting it to a void pointer first. It's not possible to call `ccall` directly from Rust because the return and argument types must be statically known, so we create a function that `ccall`s the function pointer with the given arguments by evaluating its definition.

[^1]: An ABI defines things like how a function call works at a binary level.

[Calling C and Fortran Code]: https://docs.julialang.org/en/v1/manual/calling-c-and-fortran-code/
