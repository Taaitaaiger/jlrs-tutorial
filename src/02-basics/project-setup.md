# Project setup

We first create a new binary package with `cargo`:

```bash
cargo new julia_app --bin
```

Open `Cargo.toml`, add jlrs as a dependency and enable the `local_rt` feature. We abort on panics[^1]:

```toml
[package]
name = "julia_app"
version = "0.1.0"
edition = "2021"

[features]

[profile.dev]
panic = "abort"

[profile.release]
panic = "abort"

[dependencies]
jlrs = {version = "0.21", features = ["local-rt"]}
```

If Julia 1.10 has been installed and we've configured our environment according to the steps in the [dependency chapter], building and running should succeed:

```bash
cargo build
```

It's important to set the `-rdynamic` linker flag when we embed Julia, Julia will perform badly otherwise.[^2] This flag can be set on the command line with the `RUSTFLAGS` environment variable:

`RUSTFLAGS="-Clink-args=-rdynamic" cargo build`

It's also possible to set this flag with a `config.toml` file in the project's root directory:

```toml
[target.linux]
rustflags = [ "-C", "link-args=-rdynamic" ]
```

[dependency chapter]: ../01-dependencies/julia.md

[^1]: In certain circumstances panicking can cause soundness issues, so it's better to abort.

[^2]: The nitty-gritty reason is that there's some thread-local data that Julia uses constantly. To effectively access this data, it must be defined in an application so the most performant TLS model can be used. By setting the `-rdynamic` linker flag, `libjulia` can find and make use of the definition in our application. If this flag hasn't been set Julia will fall back to a slower TLS model, which has signifant, negative performance implications.
