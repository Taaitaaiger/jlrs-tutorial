# Type environment

In every function we've exported so far, pretty much all argument and return types have been fully specified and have no remaining free type parameters.[^1] We can express types that have type parameters with `TypedValue`. To export such a function we'll need to provide a type environment that maps to the `where {T, U <: UpperBound}` part of the signature. If we tried to export it without an environment, `@wrapmodule` would fail with an `UndefVarError`.

We can use the `tvar!` macro to create a type parameter, this macro only supports single-character names. To create a type parameter `C`, we use `tvar!('C')`. The environment can be created with the `tvars!` macro, which must contain all used parameters in a valid order. The types in the signature must not include any bounds, bounds must only be used in the environment. To create the typevar `C` with an upper bound, we use `tvar!('C'; UpperBoundType)` where `UpperBoundType` is the type constructor of the upper bound. Rust macro's don't like `<` in this position so the name and bounds are seperated with a semicolon instead of `<:`.

```rust,ignore
use jlrs::{
    data::{
        managed::value::typed::TypedValue,
        types::abstract_type::{AbstractArray, AbstractFloat},
    },
    prelude::*,
    tvar, tvars,
};

// We must include `T` and `N` before `A`
// because `A` uses these parameters.
type GenericEnv = tvars!(
    tvar!('T'; AbstractFloat),
    tvar!('N'),
    tvar!('A'; AbstractArray<tvar!('T'), tvar!('N')>)
);

fn print_args(array: TypedValue<tvar!('A')>, data: TypedValue<tvar!('T')>) {
    println!("Array:\n    {array:?}");
    println!("Data:\n    {data:?}");
}

julia_module! {
    become julia_module_tutorial_init_fn;

    fn print_args(_array: TypedValue<tvar!('A')>, _data: TypedValue<tvar!('T')>) use GenericEnv;
}
```

```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> JuliaModuleTutorial.print_args([1.0 2.0], 3.0)
Array:
    1×2 Matrix{Float64}:
 1.0  2.0
Data:
    3.0

julia> JuliaModuleTutorial.print_args([1.0f0 2.0f0], 3.0f0)
Array:
    1×2 Matrix{Float32}:
 1.0  2.0
Data:
    3.0f0

julia> JuliaModuleTutorial.print_args([1.0f0 2.0f0], 3.0)
ERROR: MethodError: no method matching print_args(::Matrix{Float32}, ::Float64)

Closest candidates are:
  print_args(::A, ::T) where {T<:AbstractFloat, N, A<:AbstractArray{T, N}}
   @ Main.JuliaModuleTutorial none:0
```

To rename a function that uses a type environment, we have to put `as {{name}}` before `use {{EnvType}}`.

[^1]: The exception being array types, which are internally treated as a special case to handle their free parameters.
