# Typed values

While it's nice that we can use `Value` to handle argument types that don't implement `CCallArg`, it's annoying that this doesn't introduce any restrictions on that argument. A `TypedValue` is a `Value` that has been annotated with its type constructor. When we use it as an argument type, the generated function will restrict that argument to that type object and pass it to `ccall` as `Any`.

```rust,ignore
use jlrs::{data::managed::value::typed::TypedValue, prelude::*};

fn add(a: TypedValue<f64>, b: TypedValue<f64>) -> f64 {
    let a = a.unbox::<f64>().unwrap();
    let b = b.unbox::<f64>().unwrap();

    a + b
}

julia_module! {
    become julia_module_tutorial_init_fn;

    fn add(a: TypedValue<f64>, b: TypedValue<f64>) -> f64;
}
```

```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> JuliaModuleTutorial.add(1.0, 2.0)
3.0

julia> JuliaModuleTutorial.add(1, 2.0)
ERROR: MethodError: no method matching add(::Int64, ::Float64)

Closest candidates are:
  add(::Float64, ::Float64)
```
