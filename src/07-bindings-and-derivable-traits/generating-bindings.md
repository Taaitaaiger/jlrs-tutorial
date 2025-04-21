# Generating bindings

We can generate bindings for Julia types with the `reflect` function found in the `Reflect` module of JlrsCore.jl, it can be called with a vector of types.

```julia
julia> using JlrsCore.Reflect

julia> struct MyStruct
           a::Int8
           b::Tuple{Int8, UInt8}
       end

julia> struct MyWrapper
           ms::MyStruct
       end

julia> reflect([MyWrapper])
#[repr(C)]
#[derive(Clone, Debug, Unbox, ValidLayout, Typecheck, IntoJulia, ValidField, IsBits, ConstructType, CCallArg, CCallReturn)]
#[jlrs(julia_type = "Main.MyStruct")]
pub struct MyStruct {
    pub a: i8,
    pub b: ::jlrs::data::layout::tuple::Tuple2<i8, u8>,
}

#[repr(C)]
#[derive(Clone, Debug, Unbox, ValidLayout, Typecheck, IntoJulia, ValidField, IsBits, ConstructType, CCallArg, CCallReturn)]
#[jlrs(julia_type = "Main.MyWrapper")]
pub struct MyWrapper {
    pub ms: MyStruct,
}
```

As we can see, only `MyWrapper` has to be included to recursively generate bindings for `MyStruct` as well.[^1] The generated bindings derive all traits they can, and are annotated with the path to the type they've been generated from. It's important that this path matches the path where the type exists at runtime.

`reflect` has two keyword parameters, `f16` and `complex`. Either of these can be set to true when the feature with the same name is enabled for jlrs to map a `Float16` to `half::f16` and `Complex{T}` to `num::Complex<T>` respectively.

There are three things that `reflect` can't handle:

1. Types that have a field with a `Union` type that references a generic parameter.
2. Types that have a field with a `Tuple` type that references a generic parameter.
3. Types with atomic fields.[^2]

Note that this list doesn't include `Union` fields in general; as long as all possible variants are known, the layout is static and a valid layout can be generated:

```julia
julia> using JlrsCore.Reflect

julia> struct MyBitsUnionStruct
           u::Union{Int16, Tuple{UInt8, UInt8, UInt8, UInt8, UInt8}}
       end

julia> struct MyUnionStruct
           u::Union{Int16, Vector{UInt8}}
       end

julia> reflect([MyBitsUnionStruct, MyUnionStruct])
#[repr(C)]
#[derive(Clone, Debug, Unbox, ValidLayout, Typecheck, ValidField, ConstructType, CCallArg)]
#[jlrs(julia_type = "Main.MyBitsUnionStruct")]
pub struct MyBitsUnionStruct {
    #[jlrs(bits_union_align)]
    _u_align: ::jlrs::data::layout::union::Align2,
    #[jlrs(bits_union)]
    pub u: ::jlrs::data::layout::union::BitsUnion<5>,
    #[jlrs(bits_union_flag)]
    pub u_flag: u8,
}

#[repr(C)]
#[derive(Clone, Debug, Unbox, ValidLayout, Typecheck, ValidField, ConstructType, CCallArg)]
#[jlrs(julia_type = "Main.MyUnionStruct")]
pub struct MyUnionStruct<'scope, 'data> {
    pub u: ::std::option::Option<::jlrs::data::managed::value::ValueRef<'scope, 'data>>,
}
```

Support for inlined unions is limited to representation, the `BitsUnion` type is an opaque blob of bytes.

If bindings for a parametric type are requested, the most generic bindings are generated:

```julia
julia> using JlrsCore.Reflect

julia> struct MyParametricStruct{T}
           a::T
       end

julia> reflect([MyParametricStruct{UInt8}])
#[repr(C)]
#[derive(Clone, Debug, Unbox, ValidLayout, Typecheck, ValidField, IsBits, ConstructType, CCallArg, CCallReturn)]
#[jlrs(julia_type = "Main.MyParametricStruct")]
pub struct MyParametricStruct<T> {
    pub a: T,
}
```

Despite asking for bindings for `MyParametricStruct{UInt8}`, we got them for `MyParametricStruct{T}`.

Any type parameter that doesn't affect the layout is elided. In this case a separate layout type and type constructor are generated, which are linked with the `HasLayout` trait:

```julia
julia> using JlrsCore.Reflect

julia> struct MyElidedStruct{T}
           a::UInt8
       end

julia> reflect([MyElidedStruct{UInt8}])
#[repr(C)]
#[derive(Clone, Debug, Unbox, ValidLayout, Typecheck, ValidField, IsBits)]
#[jlrs(julia_type = "Main.MyElidedStruct")]
pub struct MyElidedStruct {
    pub a: u8,
}

#[derive(ConstructType, HasLayout)]
#[jlrs(julia_type = "Main.MyElidedStruct", constructor_for = "MyElidedStruct", scope_lifetime = false, data_lifetime = false, layout_params = [], elided_params = ["T"], all_params = ["T"])]
pub struct MyElidedStructTypeConstructor<T> {
    _t: ::std::marker::PhantomData<T>,
}
```

[^1]: Every type that is recursively inlined into the requested layout is included.

[^2]: Type constuctors are generated for types with atomic fields.
