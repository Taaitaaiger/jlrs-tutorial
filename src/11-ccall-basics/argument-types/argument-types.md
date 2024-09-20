# Argument types

Let's take a closer look at how we used `ccall` in the previous section:

```julia
ccall(ptr, Float64, (Float64, Float64), a, b)
```

The first argument is a pointer to the function we want to call, the second is the return type, the third a tuple of the argument types, and finally the arguments that the function must be called with. It's the caller's responsibility to ensure these types match the argument and return types of the function that will be called.

In the chapter on types and layouts, we've seen that the layout of immutable types corresponds to the direct translation of their definition from Julia to Rust:

```julia
julia> struct A
           a::Int8
       end

julia> struct B
           a::A
       end
```

maps to

```rust,ignore
#[repr(C)]
struct A {
    a: i8
}

#[repr(C)]
struct B {
    a: A
}
```

It's best to mostly restrict ourselves to `isbits` types in foreign interfaces. We can make limited use of mutable types, but it's important that we never use a mutable type as an argument type directly. The reason is that it's indeterminate whether the argument is passed to the foreign function by value or by reference. To ensure an argument it taken by reference, we can wrap its argument type with `Ref`:

```julia
julia> mutable struct MFloat64
           a::Float64
       end

julia> function call_rust(ptr::Ptr{Cvoid}, a::MFloat64, b::MFloat64)
           ccall(ptr, Float64, (Ref{MFloat64}, Ref{MFloat64}), a, b)
       end
```

The Rust function could be implemented as follows:

```rust,ignore
#[repr(C)]
struct MFloat64 {
    a: f64,
}

unsafe extern "C" fn add(a: *mut MFloat64, b: *mut MFloat64) -> f64 {
    (*a).a + (*b).a
}
```

We have to use mutable pointers instead of mutable references because `a` and `b` can alias.

Since `Ref` is a mutable type, it's perfectly fine to treat a `Ref{Float64}` as `*mut f64` instead of defining a custom type, This also holds true for other `isbits` types, but not for immutable types in general. In particular, we can't change what value a pointer field points to. Say we have the following struct:

```julia
julia> mutable struct MFloats64
           a::MFloat64
           b::MFloat64
       end
```

which maps to

```rust,ignore
#[repr(C)]
struct MFloats64 {
    a: *mut MFloat64,
    b: *mut MFloat64,
}
```

The following code is unsound:

```rust,ignore
unsafe extern "C" fn unsound_set(mf: *mut MFloats64, a: *mut MFloat64) {
    (*mf).a = a;
}
```

The reason is that we need to insert a write barrier after changing what value a field points to,[^1] but we can't do that here because we can't access the Julia's C API.

[^1]: Managed data starts out as a young object, after surviving garbage collection it becomes old. In practice, most objects never become old, and the GC can do an incremental collection where it only looks at young objects. If a mutation can cause an old object to reference a young one, a write barrier must be inserted after that mutation. This ensures the GC is aware that this old object references a young one, and must be included in an incremental collection.
