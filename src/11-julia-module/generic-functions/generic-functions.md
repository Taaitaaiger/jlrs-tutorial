# Generic functions

All functions in Julia are generic, we can add new methods as long as the argument types are different from existing methods. If a generic function in Rust takes an argument `T`, we can export it multiple times with different types.

```rust,ignore
use jlrs::prelude::*;

fn return_first_arg<T>(a: T, _b: T) -> T {
    a
}

julia_module! {
    become julia_module_tutorial_init_fn;

    for T in [isize, f64] {
        fn return_first_arg<T>(a: T, b: T) -> T;
    }
}
```

```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> JuliaModuleTutorial.return_first_arg(1, 2)
1

julia> JuliaModuleTutorial.return_first_arg(1.0, 2.0)
1.0

julia> JuliaModuleTutorial.return_first_arg(1.0, 2)
ERROR: MethodError: no method matching return_first_arg(::Float64, ::Int64)

Closest candidates are:
  return_first_arg(::Float64, ::Float64)
   @ Main.JuliaModuleTutorial none:0
  return_first_arg(::Int64, ::Int64)
   @ Main.JuliaModuleTutorial none:0
```

It's not necessary to use this for-loop construction, it's also valid to repeat the export with the generic types filled in.

```rust,ignore
use jlrs::prelude::*;

fn return_first_arg<T>(a: T, _b: T) -> T {
    a
}

julia_module! {
    become julia_module_tutorial_init_fn;

    fn return_first_arg(a: isize, b: isize) -> isize;
    fn return_first_arg(a: f64, b: f64) -> f64;
}
```

A type parameter may appear in arbitrary positions, the next example requires enabling the `complex` feature.

```rust,ignore
use jlrs::{data::layout::complex::Complex, prelude::*};

fn real_part<T>(a: Complex<T>) -> T {
    a.re
}

julia_module! {
    become julia_module_tutorial_init_fn;

    for T in [f32, f64] {
        fn real_part<T>(a: Complex<T>) -> T;
    }
}
```

```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> JuliaModuleTutorial.real_part(ComplexF32(1.0, 2.0))
1.0f0

julia> JuliaModuleTutorial.real_part(ComplexF64(1.0, 2.0))
1.0
```
