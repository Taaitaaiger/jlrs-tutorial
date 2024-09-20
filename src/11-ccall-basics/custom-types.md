# Custom types

What if we want to expose Rust data of a type that doesn't correspond to any Julia type?

The most straighforward option is to box the data, leak it as a pointer, and treat it as `Ptr{Cvoid}` in Julia. `Ptr{Cvoid}` is an `isbits` type, so we can simply return the pointer from Rust and expect a `Ptr{Cvoid}` in Julia. We'll need a custom function to free the data we've leaked when we're done using it.

For the sake of clarity, the examples in this tutorial assume our library is on the library search path so we can access its content by name.

```rust,ignore
#[no_mangle]
pub unsafe extern "C" fn new_rs_string(ptr: *const u8, len: usize) -> *mut String {
    let slice = std::slice::from_raw_parts(ptr, len);
    let s = String::from_utf8_lossy(slice).into_owned();
    let boxed = Box::new(s);
    Box::leak(boxed) as *mut _
}

#[no_mangle]
pub unsafe extern "C" fn print_rs_string(s: *mut String) {
    let s = s.as_ref().unwrap();
    println!("{s}")
}

#[no_mangle]
pub unsafe extern "C" fn free_rs_string(s: *mut String) {
    let _ = Box::from_raw(s);
}
```

```julia
julia> s = "Foo"
"Foo"

julia> rs_s = ccall((:new_rs_string, "libjulia_lib"), Ptr{Cvoid}, (Ptr{UInt8}, UInt), s, sizeof(s))
Ptr{Nothing} @0x000000000224ea40

julia> ccall((:print_rs_string, "libjulia_lib"), Cvoid, (Ptr{Cvoid},), rs_s)
Foo

julia> ccall((:free_rs_string, "libjulia_lib"), Cvoid, (Ptr{Cvoid},), rs_s)

```

If we can't box the data we'll need to adapt to this type in Julia by defining an immutable type.

```rust,ignore
#[repr(C)]
#[derive(Copy, Clone)]
pub struct Compound {
    a: f64,
    b: f64
}

#[no_mangle]
pub unsafe extern "C" fn new_compound(a: f64, b: f64) -> Compound {
    Compound { a, b }
}

#[no_mangle]
pub unsafe extern "C" fn add_compound(compound: Compound) -> f64 {
    compound.a + compound.b
}
```

```julia
julia> struct Compound
           a::Float64
           b::Float64
       end

julia> ccall((:new_compound, "libjulia_lib"), Compound, (Float64, Float64), 1.0, 2.0)
Compound(1.0, 2.0)

julia> ccall((:add_compound, "libjulia_lib"), Float64, (Compound,), compound)
3.0
```
