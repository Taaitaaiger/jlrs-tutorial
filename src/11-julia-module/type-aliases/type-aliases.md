# Type aliases

Sometimes we don't want to rename a type but create additional aliases for it, This is particularly useful with parametric opaque types whose constructor can't infer its parameters from the arguments.

The syntax is `type {{Name}} = {{TypeConstructor}}`. The alias doesn't inherit any constructors, they must be defined for every alias separately.

```rust,ignore
use std::fmt::Debug;

use jlrs::{
    data::{
        managed::{ccall_ref::CCallRefRet, value::typed::TypedValue},
        types::construct_type::ConstructType,
    },
    prelude::*,
    weak_handle,
};

#[derive(Debug, OpaqueType)]
struct Opaque<T> {
    _a: T,
}

impl<T: 'static + Send + Sync + ConstructType + Debug> Opaque<T> {
    fn new(a: T) -> CCallRefRet<Opaque<T>> {
        match weak_handle!() {
            Ok(handle) => CCallRefRet::new(TypedValue::new(handle, Opaque { _a: a }).leak()),
            Err(_) => panic!("not called from Julia"),
        }
    }

    fn print(&self) {
        println!("{:?}", self)
    }
}

julia_module! {
    become julia_module_tutorial_init_fn;

    for T in [f32, f64] {
        struct Opaque<T>;
        in Opaque<T> fn new(a: T) -> CCallRefRet<Opaque<T>> as Opaque;
        in Opaque<T> fn print(&self);
    };

    type OpaqueF32 = Opaque<f32>;
    in Opaque<f32> fn new(a: f32) -> CCallRefRet<Opaque<f32>> as OpaqueF32;
}
```

```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> v =  JuliaModuleTutorial.OpaqueF32(Float32(3.0))
Main.JuliaModuleTutorial.Opaque{Float32}()

julia> JuliaModuleTutorial.print(v)
Opaque { _a: 3.0 }
```
