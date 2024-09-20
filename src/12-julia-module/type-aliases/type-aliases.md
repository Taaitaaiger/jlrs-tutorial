# Type aliases

Sometimes we don't want to rename a type but create additional aliases for it, This is particularly useful with parametric opaque types whose constructor can't infer its parameters from the arguments.

The syntax is `type {{Name}} = {{TypeConstructor}}`. The alias doesn't inherit any constructors, they must be defined for every alias separately.

```rust,ignore
use std::marker::PhantomData;

use jlrs::{
    data::{
        managed::{ccall_ref::CCallRefRet, value::typed::TypedValue},
        types::{
            construct_type::ConstructType,
            foreign_type::{ParametricBase, ParametricVariant},
        },
    },
    impl_type_parameters, impl_variant_parameters,
    prelude::*,
    weak_handle,
};

pub struct HasParam<T> {
    data: isize,
    _param: PhantomData<T>,
}

impl<T> HasParam<T>
where
    T: 'static + Send + Sync + ConstructType,
{
    fn new(data: isize) -> CCallRefRet<HasParam<T>> {
        match weak_handle!() {
            Ok(handle) => {
                let data = HasParam {
                    data,
                    _param: PhantomData,
                };
                CCallRefRet::new(TypedValue::new(handle, data).leak())
            }
            Err(_) => panic!("not called from Julia"),
        }
    }

    fn data(&self) -> isize {
        self.data
    }
}

// Safety: we've correctly mapped the generics to type parameters
unsafe impl<T> ParametricBase for HasParam<T>
where
    T: 'static + Send + Sync + ConstructType,
{
    type Key = HasParam<()>;
    impl_type_parameters!('T');
}

// Safety: we've correctly mapped the generics to variant parameters
unsafe impl<T> ParametricVariant for HasParam<T>
where
    T: 'static + Send + Sync + ConstructType,
{
    impl_variant_parameters!(T);
}

julia_module! {
    become julia_module_tutorial_init_fn;

    for T in [f32, f64] {
        struct HasParam<T>;
        in HasParam<T> fn data(&self) -> isize;
    };

    type HasParam32 = HasParam<f32>;
    in HasParam<f32> fn new(data: isize) -> CCallRefRet<HasParam<f32>> as HasParam32;

    type HasParam64 = HasParam<f64>;
    in HasParam<f64> fn new(data: isize) -> CCallRefRet<HasParam<f64>> as HasParam64;
}
```

```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> d = JuliaModuleTutorial.HasParam32(1)
Main.JuliaModuleTutorial.HasParam{Float32}()

julia> JuliaModuleTutorial.data(d)
1

julia> d = JuliaModuleTutorial.HasParam64(2)
Main.JuliaModuleTutorial.HasParam{Float64}()

julia> JuliaModuleTutorial.data(d)
2
```
