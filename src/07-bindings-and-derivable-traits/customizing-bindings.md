# Customizing bindings

When `reflect` is used, the names of types and fields of the generated bindings are the same as their Julia counterparts. The type in Julia is also expected to be defined at a specific path. If this is problematic or otherwise undesirable, these names can be adjusted.

`reflect` doesn't return a string, but an instance of a type called `Layouts` that can be used with the `renamestruct!`, `renamefields!`, and `overridepath!` functions. The functions are exported by the `Reflect` module, `renamestruct!` lets us rename the Rust type, `renamefields!` the fields of a generated type, and `overridepath!` overrides the path where the type object is defined in Julia.

```julia
julia> using JlrsCore.Reflect

julia> struct MyZST end

julia> layouts = reflect([MyZST]);

julia> renamestruct!(layouts, MyZST, "MyZeroSizedType")

julia> layouts
#[repr(C)]
#[derive(Clone, Debug, Unbox, ValidLayout, Typecheck, IntoJulia, ValidField, IsBits, ConstructType)]
#[jlrs(julia_type = "Main.MyZST", zero_sized_type)]
pub struct MyZeroSizedType {
}
```

```julia
julia> using JlrsCore.Reflect

julia> struct Food
           burger::Bool
       end

julia> layouts = reflect([Food]);

julia> renamefields!(layouts, Food, [:burger => "hamburger"])

julia> layouts
#[repr(C)]
#[derive(Clone, Debug, Unbox, ValidLayout, Typecheck, IntoJulia, ValidField, IsBits, ConstructType, CCallArg, CCallReturn)]
#[jlrs(julia_type = "Main.Food")]
pub struct Food {
    pub hamburger: ::jlrs::data::layout::bool::Bool,
}
```

```julia
julia> using JlrsCore.Reflect

julia> struct MyZeroSizedType end

julia> layouts = reflect([MyZeroSizedType]);

julia> overridepath!(layouts, MyZeroSizedType, "Main.A.MyZeroSizedType")

julia> layouts
#[repr(C)]
#[derive(Clone, Debug, Unbox, ValidLayout, Typecheck, IntoJulia, ValidField, IsBits, ConstructType)]
#[jlrs(julia_type = "Main.A.MyZeroSizedType", zero_sized_type)]
pub struct MyZeroSizedType {
}
```
