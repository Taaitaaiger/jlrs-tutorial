# Cross-language LTO

At the core of jlrs lives a small static library written in C. This library serves a few purposes:

 - It hides implementation details of Julia's C API.
 - It exposes functionality implemented in terms of macros and static inline functions.
 - It provides work-arounds for backwards-incompatible changes.

Many operations are delegated to this library, which tend to be very cheap compared to the overhead of calling a function. Because the library is written in C, these functions will never be inlined.

If we use `clang` to build this library, we can enable cross-language LTO with the `lto` feature if `clang` and `rustc` use the same major LLVM version. We can query what version of clang we need to use with `rustc -vV`.

```bash
> rustc -vV
rustc 1.80.1 (3f5fd8dd4 2024-08-06)
binary: rustc
commit-hash: 3f5fd8dd41153bc5fdca9427e9e05be2c767ba23
commit-date: 2024-08-06
host: x86_64-unknown-linux-gnu
release: 1.80.1
LLVM version: 18.1.7
```

The relevant information is in the final line: LLVM 18 is used, so we need to use clang-18.

```bash
RUSTFLAGS="-Clinker-plugin-lto -Clinker=clang-18 -Clink-arg=-fuse-ld=lld -Clink-args=-rdynamic" \
CC=clang-18 \
cargo build --release --features {{julia_version}}
```

Cross-language LTO has only been tested on Linux, it can be enabled for applications and dynamic libraries. It has no effect on the performance of Julia code, only on Rust code that calls into the intermediate library.
