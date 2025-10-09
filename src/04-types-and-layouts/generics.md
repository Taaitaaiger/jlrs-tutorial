# Generics

Types in Julia can have parameters, which may or may not affect the layout of the type.

There are two reasons why a type parameter might not affect the layout:

1. it's a value parameter, not referenced by any of the fields.
2. it affects the layout of a field that isn't inlined.

Any type parameter that doesn't affect the layout can be elided, otherwise it can be treated the same way in Rust and Julia:

```julia
struct Generic{T}
    t::T
end

struct SetGeneric
    t::Generic{UInt32}
end

struct Elided{T}
    t::UInt32
end
```

```rust,ignore
#[repr(C)]
struct Generic<T> {
    t: T,
}

#[repr(C)]
struct SetGeneric {
    t: Generic<u32>,
}

#[repr(C)]
struct Elided {
    t: u32,
}
```

All three types can implement `ValidLayout` and `ValidField` because they're immutable types in Julia. In the case of `Generic` it's required that `T: ValidField`. If `T` is some mutable or otherwise non-inlined type, we can express the layout type as `Generic<Option<ValueRef>>`.

`Generic` and `SetGeneric` don't elide any type parameters so they can implement `ConstructType`, but `Elided` is unaware of the type paramater `T`.
