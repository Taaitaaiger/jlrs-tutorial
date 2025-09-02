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
edition = "2024"

[features]

[profile.dev]
panic = "abort"

[profile.release]
panic = "abort"

[dependencies]
jlrs = {version = "0.22", features = ["local-rt"]}
```

If Julia has been installed and we've configured our environment according to the steps in the [dependency chapter], building and running should succeed:

```bash
cargo build
```

If you use `juliaup` and `jlrs-launcher`, the following command must be used:

```bash
jlrs-launcher run cargo build
```

The Julia version can be specified:

```bash
jlrs-launcher run +1.11 cargo build
```

It's important to set the `-rdynamic` linker flag when we embed Julia, Julia will perform badly otherwise.[^2] This flag can be set on the command line with the `RUSTFLAGS` environment variable:

`RUSTFLAGS="-Clink-args=-rdynamic" cargo build`

It's also possible to set this flag with a `config.toml` file in [one of the supported directories] for [supported platforms]:

```toml
[target.x86_64-unknown-linux-gnu]
rustflags = [ "-C", "link-args=-rdynamic" ]

[target.aarch64-unknown-linux-musl]
rustflags = [ "-C", "link-args=-rdynamic" ]

# ...etc
```

[dependency chapter]: ../01-dependencies/julia.md

[^1]: In certain circumstances panicking can cause soundness issues, so it's better to abort.

[^2]: The nitty-gritty reason is that there's some thread-local data that Julia uses constantly. To effectively access this data, it must be defined in an application so the most performant TLS model can be used. By setting the `-rdynamic` linker flag, `libjulia` can find and make use of the definition in our application. If this flag hasn't been set Julia will fall back to a slower TLS model, which has signifant, negative performance implications.

[one of the supported directories]: https://doc.rust-lang.org/cargo/reference/config.html

[supported platforms]: https://doc.rust-lang.org/rustc/platform-support.html
