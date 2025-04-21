# With generics

Opaque types can have generics, which are exposed as type parameters to Julia. In the best-case scenario, we don't have to deal with bounds on the struct type.

Opaque types must be `'static` and implement `Send` and `Sync`, so any generic must obey these constraints as well. They must also implement `ConstructType` because this type information is exposed to Julia.

We need to export an opaque type with parameters with every supported type parameter. The same is true for its methods, a separate function is generated for every combination of types. To do so effectively, we can loop through an array of types.

It can be useful to expose aliases for specific exported types. This alias can only be used as a constructor if that method is exposed again under the alias's name.

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

julia> v =  JuliaModuleTutorial.Opaque(Float32(3.0))
Main.JuliaModuleTutorial.Opaque{Float32}()

julia> v =  JuliaModuleTutorial.Opaque(Float64(3.0))
Main.JuliaModuleTutorial.Opaque{Float64}()

julia> v =  JuliaModuleTutorial.OpaqueF32(Float32(3.0))
Main.JuliaModuleTutorial.Opaque{Float32}()

julia> JuliaModuleTutorial.print(v)
Opaque { _a: 3.0 }
```
