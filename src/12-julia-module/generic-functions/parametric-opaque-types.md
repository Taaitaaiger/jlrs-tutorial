# Parametric opaque types

The `OpaqueType` and `ForeignType` traits create new Julia types without any type parameters, so we can't use these traits when the type has one or more parameters that we want to expose to Julia. Instead, we'll need to implement the `ParametricBase` and `ParametricVariant` traits.

`ParametricBase` describes the type when its parameters haven't been set to an explicit type. We have to provide a `Key` type which doesn't depend on any of the generics, and the names of all type parameters our Julia type will have. `ParametricVariant` describes a specific variant of the parameteric type and we must provide type constructors for all generics. A parametric opaque type must be exported with every combination of generics that we want to use.

```rust,ignore
use jlrs::{
    data::{
        managed::value::typed::{TypedValue, TypedValueRet},
        types::{
            construct_type::ConstructType,
            foreign_type::{ParametricBase, ParametricVariant},
        },
    },
    impl_type_parameters, impl_variant_parameters,
    prelude::*,
    weak_handle,
};

pub struct ParametricOpaque<T, U> {
    a: T,
    b: U,
}

impl<T, U> ParametricOpaque<T, U>
where
    T: 'static + Send + Sync + Copy + ConstructType,
    U: 'static + Send + Sync + Copy + ConstructType,
{
    fn new(a: T, b: U) -> TypedValueRet<ParametricOpaque<T, U>> {
        match weak_handle!() {
            Ok(handle) => {
                let data = ParametricOpaque { a, b };
                TypedValue::new(handle, data).leak()
            }
            Err(_) => panic!("not called from Julia"),
        }
    }

    fn get_a(&self) -> T {
        self.a
    }

    fn set_b(&mut self, b: U) -> U {
        let old = self.b;
        self.b = b;
        old
    }
}

// Safety: we've correctly mapped the generics to type parameters
unsafe impl<T, U> ParametricBase for ParametricOpaque<T, U>
where
    T: 'static + Send + Sync + Copy + ConstructType,
    U: 'static + Send + Sync + Copy + ConstructType,
{
    type Key = ParametricOpaque<(), ()>;
    impl_type_parameters!('T', 'U');
}

// Safety: we've correctly mapped the generics to variant parameters
unsafe impl<T, U> ParametricVariant for ParametricOpaque<T, U>
where
    T: 'static + Send + Sync + Copy + ConstructType,
    U: 'static + Send + Sync + Copy + ConstructType,
{
    impl_variant_parameters!(T, U);
}

julia_module! {
    become julia_module_tutorial_init_fn;

    for T in [f32, f64] {
        for U in [f32, f64] {
            struct ParametricOpaque<T, U>;

            in ParametricOpaque<T, U> fn new(a: T, b: U) -> TypedValueRet<ParametricOpaque<T, U>> as ParametricOpaque;

            in ParametricOpaque<T, U> fn get_a(&self) -> T;
            in ParametricOpaque<T, U> fn set_b(&mut self, b: U) -> U;
        }
    }
}
```

```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> typeof(JuliaModuleTutorial.ParametricOpaque)
UnionAll

julia> v = JuliaModuleTutorial.ParametricOpaque(1.0, float(2.0))
Main.JuliaModuleTutorial.ParametricOpaque{Float64, Float64}()

julia> JuliaModuleTutorial.get_a(v)
1.0

julia> methods(JuliaModuleTutorial.set_b)
# 4 methods for generic function "set_b" from Main.JuliaModuleTutorial:
 [1] set_b(arg1::Main.JuliaModuleTutorial.ParametricOpaque{Float64, Float64}, arg2::Float64)
     @ none:0
 [2] set_b(arg1::Main.JuliaModuleTutorial.ParametricOpaque{Float64, Float32}, arg2::Float32)
     @ none:0
 [3] set_b(arg1::Main.JuliaModuleTutorial.ParametricOpaque{Float32, Float64}, arg2::Float64)
     @ none:0
 [4] set_b(arg1::Main.JuliaModuleTutorial.ParametricOpaque{Float32, Float32}, arg2::Float32)
     @ none:0
```
