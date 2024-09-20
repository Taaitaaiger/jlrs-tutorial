# Functions

Any function can be exported as long as its argument types and return type are compatible with Julia. This requires that these types implement `CCallArg` and `CCallReturn` respectively.

These traits should not be implemented manually. jlrs provides implementations for primitive and managed types, bindings for Julia types generated with `JlrsCore.Reflect.reflect` will derive these traits when applicable. `CCallArg` is derived if the type has no elided type parameters[^1], isn't a zero-sized type, and is immutable. `CCallReturn` additionally requires that the type is an `isbits` type. If these properties hold, the data can be taken or returned by value, and the layout of the Rust type maps to a single Julia type.

Exporting a function is a matter copying and pasting its signature:

```rust,ignore
use jlrs::prelude::*;

fn add(a: f64, b: f64) -> f64 {
    a + b
}

julia_module! {
    become julia_module_tutorial_init_fn;

    fn add(a: f64, b: f64) -> f64;
}
```

```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> JuliaModuleTutorial.add(1.0, 2.0)
3.0

julia> JuliaModuleTutorial.add(1, 2.0)
ERROR: MethodError: no method matching add(::Int64, ::Float64)
```

We don't have to mark our function as `extern "C"`, the `julia_module!` macro generates an `extern "C"` wrapper function for every exported function. These wrappers only exist inside the `julia_module_tutorial_init_fn` so we don't need to worry about name conflicts.

Like constants, exported functions can be renamed and documented.

```rust,ignore
use jlrs::prelude::*;

fn add(a: f64, b: f64) -> f64 {
    a + b
}

julia_module! {
    become julia_module_tutorial_init_fn;

    ///     add!(::Float64, ::Float64)::Float64
    fn add(a: f64, b: f64) -> f64 as add!;
}
```

```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> JuliaModuleTutorial.add!(1.0, 2.0)
3.0

help?> JuliaModuleTutorial.add!
   add!(::Float64, ::Float64)::Float64
```

[^1]: i.e., ConstructType is also derived.
