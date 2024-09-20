# Project setup

We first create a new binary package with `cargo`:

```bash
cargo new julia_app --bin
```

Open `Cargo.toml`, add jlrs as a dependency and enable the `local_rt` feature. We abort on panics[^1], and reexport the version features:

```toml
[package]
name = "julia_app"
version = "0.1.0"
edition = "2021"

[features]
julia-1-6 = ["jlrs/julia-1-6"]
julia-1-7 = ["jlrs/julia-1-7"]
julia-1-8 = ["jlrs/julia-1-8"]
julia-1-9 = ["jlrs/julia-1-9"]
julia-1-10 = ["jlrs/julia-1-10"]
julia-1-11 = ["jlrs/julia-1-11"]

[profile.dev]
panic = "abort"

[profile.release]
panic = "abort"

[dependencies]
jlrs = {version = "0.21", features = ["local-rt"]}
```

If we tried to build our application without enabling a version feature, we'd see the following error:

```text
error: A Julia version must be selected by enabling exactly one of the following version features:
           julia-1-6
           julia-1-7
           julia-1-8
           julia-1-9
           julia-1-10
           julia-1-11
```

If Julia 1.10 has been installed and we've configured our environment according to the steps in the [dependency chapter], building and running should succeed after enabling the `julia-1-10` feature:

```bash
cargo build --features julia-1-10
```

It's important to set the `-rdynamic` linker flag when we embed Julia on Linux, Julia will perform badly otherwise.[^2] This flag can be set on the command line with the `RUSTFLAGS` environment variable:

`RUSTFLAGS="-Clink-args=-rdynamic" cargo build --features julia-1-10`

It's also possible to set this flag with a `config.toml` file in the project's root directory:

```toml
[target.linux]
rustflags = [ "-C", "link-args=-rdynamic" ]
```

[dependency chapter]: ../01-dependencies/julia.md

[^1]: In certain circumstances panicking can cause soundness issues, so it's better to abort.

[^2]: The nitty-gritty reason is that there's some thread-local data that Julia uses constantly. To effectively access this data, it must be defined in an application so the most performant TLS model can be used. By setting the `-rdynamic` linker flag, `libjulia` can find and make use of the definition in our application. If this flag hasn't been set Julia will fall back to a slower TLS model, which has signifant, negative performance implications. This is only important on Linux, macOS and Windows users can ignore this entirely because the concept of TLS models don't exists on these platforms.
