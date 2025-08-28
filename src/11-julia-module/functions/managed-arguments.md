# Managed arguments

We're not limited to just using immutable types as function arguments, managed types also implement `CCallArg`. The function can just as easily take a `Module` or `Value` as an argument. If the argument type is `Value`, that argument's type is left unspecified in the generated function signature and passed to `ccall` as `Any`.

<!-- LIBTEST START -->
```rust,ignore
use jlrs::prelude::*;

fn print_module_name(module: Module) {
    let name = module.name();
    println!("{name:?}");
}

fn print_value(value: Value) {
    println!("{value:?}");
}

julia_module! {
    become julia_module_tutorial_init_fn;

    fn print_module_name(module: Module);
    fn print_value(value: Value);
}
```
<!-- LIBTEST END -->

<!-- LIBTEST_JL START -->
```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> JuliaModuleTutorial.print_module_name(JuliaModuleTutorial)
:JuliaModuleTutorial

julia> JuliaModuleTutorial.print_value(JuliaModuleTutorial)
Main.JuliaModuleTutorial
```
<!-- LIBTEST_JL END -->
