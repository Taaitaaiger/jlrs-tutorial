# `CCallRef`

In the previous chapter we saw how we could wrap an argument type in `ccall` with `Ref` to guarantee it was passed by reference. We can use `CCallRef` to achieve this when we export functions with `julia_module!`.

When `CCallRef<T>` is used as an argument type, the generated function restricts the argument type to `T`, it's passed to `ccall` as `Ref{T}`. One important detail that we must keep in mind when using `CCallRef` as an argument type is that the argument is only guaranteed to be passed by reference, not that the argument is managed data.[^1]

If `CCallRefRet<T>` is used as a return type, `ccall` returns it as `Ref{T}` and the function as `T`. The main advantage returning `CCallRefRet<T>` has over `TypedValueRet<T>` is that using `CCallRefRet` produces more type-stable code.

```rust,ignore
use jlrs::{
    data::managed::{
        ccall_ref::{CCallRef, CCallRefRet},
        value::typed::TypedValue,
    },
    prelude::*,
    weak_handle,
};

fn add(a: CCallRef<f64>, b: CCallRef<f64>) -> CCallRefRet<f64> {
    let a = a.as_ref().expect("incompatible layout");
    let b = b.as_ref().expect("incompatible layout");

    match weak_handle!() {
        Ok(handle) => CCallRefRet::new(TypedValue::new(handle, a + b).leak()),
        Err(_) => panic!("not called from Julia"),
    }
}

julia_module! {
    become julia_module_tutorial_init_fn;

    fn add(a: CCallRef<f64>, b: CCallRef<f64>) -> CCallRefRet<f64>;
}
```

```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> JuliaModuleTutorial.add(1.0, 2.0)
3.0
```

[^1]: While both are pointers to the same layout, managed data is guaranteed to be preceded in memory by a tag that identifies its type. This tag isn't guaranteed to be present when an argument is passed by reference.
