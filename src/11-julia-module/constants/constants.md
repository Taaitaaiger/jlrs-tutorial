# Constants

The simplest thing we can export from Rust to Julia is a constant. New constants can be created from static and constant items whose type implements `IntoJulia`.

<!-- LIBTEST START -->
```rust,ignore
use jlrs::prelude::*;

const CONST_U8: u8 = 1;
static STATIC_U8: u8 = 2;

julia_module! {
    become julia_module_tutorial_init_fn;

    const CONST_U8: u8;
    const STATIC_U8: u8;
}
```
<!-- LIBTEST END -->

If we compile this code and wrap it, we can access these constants:

<!-- LIBTEST_JL START -->
```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> JuliaModuleTutorial.CONST_U8
0x01

julia> JuliaModuleTutorial.STATIC_U8
0x02
```
<!-- LIBTEST_JL END -->

It's possible to rename a constant by putting `as NEW_NAME` at the end of the declaration. They can also be documented, Julia doctests are supported.

<!-- LIBTEST START -->
```rust,ignore
use jlrs::prelude::*;

const CONST_U8: u8 = 1;

julia_module! {
    become julia_module_tutorial_init_fn;

    ///     CONST_UINT8
    ///
    /// An exported constant.
    const CONST_U8: u8 as CONST_UINT8;
}
```
<!-- LIBTEST END -->

<!-- LIBTEST_JL START -->
```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> JuliaModuleTutorial.CONST_UINT8
0x01

help?> JuliaModuleTutorial.CONST_UINT8
   CONST_UINT8

  An exported constant.
```
<!-- LIBTEST_JL END -->
