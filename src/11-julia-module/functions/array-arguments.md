# Array arguments

Without jlrs we had to convert arrays to a pointer to their first element if we wanted to access them in a `ccall`ed function, with jlrs taking an array argument directly isn't an issue.

Any of the aliases of `ArrayBase` can be used as an argument type, they enforce the obvious restrictions: `Array` only enforces that the argument is an array, `TypedArray` puts restrictions on the element type, `RankedArray` on the rank, and `TypedRankedArray` on both. Other aliases like `Vector` are expressed in terms of these aliases so they can also be used as argument types.

```rust,ignore
use jlrs::prelude::*;

// Safety: the array must not be mutated from another thread
unsafe fn sum_array(array: TypedArray<f64>) -> f64 {
    array.bits_data().as_slice().iter().sum()
}

julia_module! {
    become julia_module_tutorial_init_fn;

    fn sum_array(array: TypedArray<f64>) -> f64;
}
```

```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> JuliaModuleTutorial.sum_array([1.0 2.0])
3.0

julia> JuliaModuleTutorial.sum_array([1.0; 2.0])
3.0
```
