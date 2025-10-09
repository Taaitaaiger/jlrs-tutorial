# Arrays

To pass an array as an argument, we'll need to convert it to a pointer to its first element. This is a matter of expressing its argument type as `Ptr{ElemType}`.

```rust,ignore
unsafe extern "C" fn add_one(ptr: *mut i8, len: usize) {
    std::slice::from_raw_parts_mut(ptr, len)
        .iter_mut()
        .for_each(|i| *i += 1);
}
```

```julia
julia> function call_rust(ptr::Ptr{Cvoid}, arr::Vector{Int8})
           ccall(ptr, Cvoid, (Ptr{Int8}, UInt), arr, length(arr))
       end
```

This approach also works for higher-ranked arrays, the elements are laid out in column-major order.

Avoid mutable element types. Array elements essentially behave like struct fields, and we can't insert write barriers.
