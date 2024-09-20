# `isbits` layouts

The layout of a primitive type in Julia usually matches its analog in Rust: if the `DataType` is `Int8`, a `Value` of this type is a pointer to an `i8`; if it's `Float32` the `Value` is a pointer to an `f32`. There are two exceptions: `Bool` and `Char` map to types of the same name defined in jlrs, not `bool` and `char`.

Composite types are a bit more involved. `isbits` types are immutable types made up of primitive types and other `isbits` types. Their layout maps to the obvious `repr(C)` representation in Rust. For example, the following Rust and Julia types have the same layout in memory

```julia
struct InnerBits
    a::Int8
end

struct OuterBits
    inner::InnerBits
    b::UInt8
end
```

```rust,ignore
#[repr(C)]
struct InnerBits {
    a: i8
}

#[repr(C)]
struct OuterBits {
    inner: InnerBits,
    b: u8,
}
```

Because `InnerBits` and `OuterBits` in Rust faithfully represent the layout of their corresponding type in Julia they can implement `ValidLayout`. They can implement `ValidField` because they're inlined into the composite when used as a field type. The layouts correspond to a single type in Julia, so these types can implement `ConstructType` to map the Rust type to their Julia counterpart.
