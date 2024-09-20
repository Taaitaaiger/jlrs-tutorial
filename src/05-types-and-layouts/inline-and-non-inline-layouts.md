# Inline and non-inline layouts

In the previous section we saw that fields with an `isbits` type are inlined in a composite type. A field whose type is mutable won't be inlined.

```julia
mutable struct Inner
    a::Int8
end

struct Outer
    inner::Inner
    b::UInt8
end
```

```rust,ignore
#[repr(C)]
struct Inner {
    a: i8
}

#[repr(C)]
struct Outer<'scope, 'data> {
    inner: Option<ValueRef<'scope, 'data>>,
    b: u8,
}
```

An unrooted reference is used instead of a managed type to represent non-inlined fields to account for mutability, which can render the field's old value unreachable. Managed types and unrooted references make use of the `Option<NonNull>` niche optimization to guarantee `Option<ValueRef>` has the same size as a pointer.[^1] We'll say that instances of `Outer` reference managed data.

Because mutable types aren't inlined, `Inner` can only implement `ValidLayout`, not `ValidField`. Immutable types are normally inlined, so `Outer` can implement both traits. The layouts identify single types, so both types can implement `ConstructType`.

[^1]: Null data is rare in Julia and generally invalid to use.
