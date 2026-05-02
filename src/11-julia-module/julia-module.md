# `julia_module!`

In the previous chapter we've created a dynamic library that exposed Rust code to Julia without using jlrs. Using jlrs provides many additional features, including better support for custom types, code generation, and integration with Julia code. The main disadvantage is that our library won't be compatible with different versions of Julia, but is compiled for the specific version.

In this chapter we'll use the `julia_module!` macro to export constants, types and functions to Julia. To use this make we have to enable the `jlrs-derive` and `ccall` features.

```toml
[package]
name = "julia_module_tutorial"
version = "0.1.0"
edition = "2024"

[profile.dev]
panic = "abort"

[profile.release]
panic = "abort"

[features]

[lib]
crate-type = ["cdylib"]

[dependencies]
jlrs = { version = "0.23", features = ["jlrs-derive", "ccall"] }
```

It's important that we don't enable any runtime features like `local-rt` when we build a dynamic library.

The following is a minimal example of `julia_module!`:

```rust,ignore
use jlrs::prelude::*;

julia_module! {
    become julia_module_tutorial_init_fn;

    // module content...
}
```

The macro is transformed into a single function, `julia_module_tutorial_init_fn`, that can be used with JlrsCore.jl's `@wrapmodule` macro:

```julia
module JuliaModuleTutorial
using JlrsCore.Wrap

@wrapmodule("/path/to/libjulia_module_tutorial", :julia_module_tutorial_init_fn)

function __init__()
    @initjlrs
end
end
```

This is all the Julia code we'll need to write, the `@wrapmodule` macro generates the content of the module. For the sake of brevity, code samples in the following sections will write `module JuliaModuleTutorial ... end` as a shorthand for this module definition.
