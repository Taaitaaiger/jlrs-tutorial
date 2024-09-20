# Rust

The minimum supported Rust version (MSRV) is currently 1.77, but some features may require a more recent version. The MSRV can be bumped in minor releases of jlrs.[^1]

Note for Windows users: only the GNU toolchain is supported for dynamic libraries, applications that embed Julia can use either the GNU or MSVC toolchain.

[^1]: The informal policy is that the MSRV must not exceed the version used by Yggdrasil.
