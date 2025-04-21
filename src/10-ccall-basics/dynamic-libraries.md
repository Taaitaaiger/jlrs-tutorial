# Dynamic library

The embedding example is rather contrived, we rarely need to expose a function from an application that embeds Julia. It's much more likely that some Rust crate implements useful functionality that we want to expose to Julia.

Julia can load dynamic libraries at runtime.[^1] Let's create a new dynamic library that exposes the `add` function we've defined above. We start by creating a new crate.[^2]

```bash
cargo new julia_lib --lib
```

We need to change the crate type to `cdylib`, this can be configured in `Cargo.toml`:

```toml
[package]
name = "julia_lib"
version = "0.1.0"
edition = "2021"

[profile.release]
panic = "abort"

[profile.dev]
panic = "abort"

[lib]
crate-type = ["cdylib"]

[dependencies]
```

We don't need to add jlrs as a dependency, we'll discuss the advantages and disadvantages of using jlrs with dynamic libraries in the next chapter.

Replace the content of `lib.rs` with the following code:

```rust,ignore
#[no_mangle]
pub unsafe extern "C" fn add(a: f64, b: f64) -> f64 {
    a + b
}
```

The function is annotated with `#[no_mangle]` to prevent the name from being mangled. After building with `cargo build` we can find the library in `target/debug`. On Linux it will be named `libjulia_lib.so`, on macOS `libjulia_lib.dylib`, and on Windows `libjulia_lib.dll`. Let's use it!

Open the Julia REPL in `julia_lib`'s root directory and evaluate the following code:

```julia
julia> using Libdl

julia> handle = dlopen("./target/debug/libjulia_lib")
Ptr{Nothing} @0x0000000000e2a620

julia> func = dlsym(handle, "add")
Ptr{Nothing} @0x000073b0dec02100

julia> ccall(func, Float64, (Float64, Float64), 1.0, 2.0)
3.0
```

Note that we don't have to provide the extension when opening the library.

If the library is on the library search path we don't even need to open it or acquire function pointers, but can refer to it directly:

```julia
julia> ccall((:add, "libjulia_lib"), Float64, (Float64, Float64), 1.0, 2.0)
3.0
```

[^1]: Using the GNU toolchain is recommended on Windows. It might also be possible to use the MSVC toolchain but this hasn't been tested.

[^2]: If the crate we want to expose already provides a C API we won't need an intermediate crate. We can directly build the library and adapt to the existing API instead.
