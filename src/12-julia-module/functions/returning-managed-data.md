# Returning managed data

We can return data by value as long as the return type is an `isbits` type, anything more complex must be returned as managed data. However, we run into an issue here: we'll need to create a scope before we can create managed data, and we need to return that data from the scope despite the lifetime constraints.

To create a scope we'll need a handle, introducing: `WeakHandle`. A `WeakHandle` provides the same functionalty as the `LocalHandle` we've used in most embedding examples, but it doesn't shut down Julia when it's dropped. We can created them freely with the `weak_handle!` and `weak_handle_unchecked!` macros. The first confirms that the thread is in a state where it can call into Julia and is safe to use, the latter assumes this is the case and is therefore unsafe to use.

While this at least gives us a way to create scopes, we still need to solve the other problem: how do we return managed data from a scope?

Every managed type in jlrs has a `'scope` lifetime, to return managed data from the scope we'll need to erase this lifetime. jlrs takes the rootedness guarantee of managed types seriously, so we can't simply adjust the lifetime of such data directly. `Ref`-types don't guarantee that the data is rooted for its `'scope` lifetime, so we're free to relax it to `'static`, which solves our issue. We call this leaking managed data.

In short, to return managed data we'll need to convert it to a `Ref` with static lifetimes first. All managed types have a `Ret` alias, which is the `Ref` alias with static lifetimes. These `Ret`-aliases implement `CCallReturn`. Converting managed data to a `Ret` type is a matter of calling `Managed::leak`.

```rust,ignore
use jlrs::{
    data::managed::value::typed::{TypedValue, TypedValueRet},
    prelude::*,
    weak_handle,
};

fn add(a: f64, b: f64) -> TypedValueRet<f64> {
    match weak_handle!() {
        Ok(handle) => TypedValue::new(handle, a + b).leak(),
        _ => panic!("not called from Julia"),
    }
}

julia_module! {
    become julia_module_tutorial_init_fn;

    fn add(a: f64, b: f64) -> TypedValueRet<f64>;
}
```

```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> JuliaModuleTutorial.add(1.0, 2.0)
3.0
```

We didn't have to create a scope because a `WeakHandle` is a non-rooting target itself. We can skip rooting the data because we call no other functions that could hit a safepoint before returning from `add`. The `weak_handle!` macro must be used in combination with `match` or `if let`, we can't `unwrap` or `expect` it.

We can return arrays the same way, all `ArrayBase` aliases have a `Ret`-alias.

```rust,ignore
use jlrs::{data::managed::array::TypedMatrixRet, prelude::*, weak_handle};

fn new_matrix(rows: usize, cols: usize) -> TypedMatrixRet<f64> {
    match weak_handle!() {
        Ok(handle) => {
            let data = vec![0.0f64; rows * cols];
            TypedMatrix::from_vec(handle, data, [rows, cols])
                .expect("size invalid")
                .expect("caught exception")
                .leak()
        }
        _ => panic!("not called from Julia"),
    }
}

julia_module! {
    become julia_module_tutorial_init_fn;

    fn new_matrix(rows: usize, cols: usize) -> TypedMatrixRet<f64>;
}
```

```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> JuliaModuleTutorial.new_matrix(UInt(4), UInt(2))
4×2 Matrix{Float64}:
 0.0  0.0
 0.0  0.0
 0.0  0.0
 0.0  0.0
```
