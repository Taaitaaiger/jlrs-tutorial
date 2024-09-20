# Typed layouts

If the layout of an immutable type has one or more elided type parameters, the layout doesn't map to a single Julia type and can't implement `ConstructType`. This prevents us from using it as an argument type, despite the fact that it could be passed by value. Just like `TypedValue` let us annotate a `Value` with its type constructor, we can use `TypedLayout` to annotate a layout with its type constructor.

```rust,ignore
use jlrs::{
    data::{layout::typed_layout::TypedLayout, types::construct_type::ConstantBool},
    prelude::*,
};

#[repr(C)]
#[derive(Clone, Debug, Unbox, ValidLayout, Typecheck, ValidField, IsBits)]
#[jlrs(julia_type = "Main.JuliaModuleTutorial.HasElided")]
pub struct HasElided {
    pub a: i32,
}

#[derive(ConstructType, HasLayout)]
#[jlrs(
    julia_type = "Main.JuliaModuleTutorial.HasElided",
    constructor_for = "HasElided",
    scope_lifetime = false,
    data_lifetime = false,
    layout_params = [],
    elided_params = ["X"],
    all_params = ["X"]
)]
pub struct HasElidedTypeConstructor<X> {
    _x: ::std::marker::PhantomData<X>,
}

pub type HasElidedTrue = HasElidedTypeConstructor<ConstantBool<true>>;

fn get_inner(he: TypedLayout<HasElided, HasElidedTrue>) -> i32 {
    he.into_layout().a
}

julia_module! {
    become julia_module_tutorial_init_fn;

    fn get_inner(he: TypedLayout<HasElided, HasElidedTrue>) -> i32;
}
```

```julia
julia> module JuliaModuleTutorial
       using JlrsCore.Wrap

       struct HasElided{X}
           a::Int32
       end

       @wrapmodule("./target/debug/libjulia_module_tutorial", :julia_module_tutorial_init_fn)

       function __init__()
           @initjlrs
       end
       end
Main.JuliaModuleTutorial

julia> JuliaModuleTutorial.get_inner(JuliaModuleTutorial.HasElided{true}(1))
1

julia> JuliaModuleTutorial.get_inner(JuliaModuleTutorial.HasElided{1}(1))
ERROR: MethodError: no method matching get_inner(::Main.JuliaModuleTutorial.HasElided{1})

Closest candidates are:
  get_inner(::Main.JuliaModuleTutorial.HasElided{true})
```
