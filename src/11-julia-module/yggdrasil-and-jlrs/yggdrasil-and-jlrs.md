# Yggdrasil and jlrs

In the previous chapter we saw how we could write a recipe to build a Rust crate and contribute it to Yggdrasil to distribute it as a JLL package. When the crate we want to build depends on jlrs, we have to deal with a complication: we need to build the library against every version of Julia that we want to support. This requires a few adjustments to the recipe.

The recipe should look as follows:

```julia
# Note that this script can accept some limited command-line arguments, run
# `julia build_tarballs.jl --help` to see a usage message.
using BinaryBuilder

name = "{{crate_name}}"
version = v"0.1.0"
julia_versions = [v"1.10", v"1.11", v"1.12", v"1.13"]

# Collection of sources required to complete build
sources = [
    GitSource("https://github.com/{{user}}/{{crate_name}}.git",
              "{full commit hash, e.g.: 52ab80563a07d02e3d142f85101853bbf5c0a8a1}"),
]

# Bash recipe for building across all platforms
script = raw"""
cd $WORKSPACE/srcdir/{{crate_name}}
cargo build --release --verbose
install_license LICENSE
install -Dvm 0755 "target/${rust_target}/release/"*{{crate_name}}".${dlext}" "${libdir}/lib{{crate_name}}.${dlext}"
"""

include("../../L/libjulia/common.jl")
platforms = vcat(libjulia_platforms.(julia_versions)...)

# 32-bit Windows, AArch64 FreeBSD, and riscv64 are not supported
is_excluded(p) = (Sys.iswindows(p) && nbits(p) == 32) || (Sys.isfreebsd(p) && arch(p) == "aarch64") || arch(p) == "riscv64"
filter!(!is_excluded, platforms)

# The products that we will ensure are always built
products = [
    LibraryProduct("lib{{crate_name}}", :librustfft),
]

# Dependencies that must be installed before this package can be built
dependencies = [
    BuildDependency("libjulia_jll"),
    Dependency("Libiconv_jll"; platforms=filter(Sys.isapple, platforms)),
]

# Build the tarballs.
build_tarballs(ARGS, name, version, sources, script, platforms, products, dependencies;
               preferred_gcc_version=v"10", julia_compat="1.10", compilers=[:c, :rust])
```

The main differences with the recipe for a crate that doesn't depend on jlrs are:

- The supported versions of Julia are set.
- Supported platforms are acquired via `libjulia_platforms`, not `supported_platforms`.
- `libjulia_jll` is added to the dependencies as a build dependency.

[#2942]: https://github.com/JuliaLang/Pkg.jl/issues/2942
