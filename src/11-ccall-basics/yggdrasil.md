# Yggdrasil

If we completely removed Rust from our system before trying to add and use a package that depends on Rust code like RustFFT.jl, we'd see that everything still works correctly. Things still work because a recipe to build the library is available in [Yggdrasil]. When we contribute a recipe to Yggdrasil, that library will be prebuilt and made available as a JLL package.

A recipe for a library written in Rust will typically look something like this, and should be named `build_tarballs.jl`:

```julia
# Note that this script can accept some limited command-line arguments, run
# `julia build_tarballs.jl --help` to see a usage message.
using BinaryBuilder, Pkg

name = "{{crate_name}}"
version = v"0.1.0"

# Collection of sources required to complete build
sources = [
    GitSource("https://github.com/{{user}}/{{crate_name}}.git",
              "{full commit hash, e.g.: 52ab80563a07d02e3d142f85101853bbf5c0a8a1}"),
]

# Bash recipe for building across all platforms
script = raw"""
cd $WORKSPACE/srcdir/{{crate_name}}

cargo build--release --verbose
install_license LICENSE
install -Dvm 0755 "target/${rust_target}/release/"*{{crate_name}}.${dlext} "${libdir}/lib{{crate_name}}.${dlext}"
"""

# These are the platforms we will build for by default, unless further
# platforms are passed in on the command line
platforms = supported_platforms(; experimental=true)
# Rust toolchain for i686 Windows is unusable
filter!(p -> !Sys.iswindows(p) || arch(p) != "i686", platforms)

# The products that we will ensure are always built
products = [
    LibraryProduct("lib{{crate_name}}", :lib{{crate_name}}),
]

# Dependencies that must be installed before this package can be built
dependencies = [
    Dependency("Libiconv_jll"; platforms=filter(Sys.isapple, platforms)),
]

# Build the tarballs.
build_tarballs(ARGS, name, version, sources, script, platforms, products, dependencies;
               julia_compat="1.6", compilers=[:c, :rust])
```

This recipe should work for crates that are written purely in Rust after replacing `{{user}}` and `{{crate_name}}`. If the crate depends on some other dynamic library, recipes must be available for those libraries so we can add them to the list of dependencies. This is outside the scope of this tutorial, see the [BinaryBuilder.jl documentation] for more information.

One final detail that we need to keep in mind is that BinaryBuilder.jl uses its own Rust toolchain. We can check which version of Rust will be used in the [recipe for the Rust toolchain].

We can test our recipe locally by executing it: `julia build_tarballs.jl`. In practice it's useful to set the `--verbose` and `--debug` flags. If `--debug` is set, a debug prompt is opened on failure to help diagnose and resolve the issue. On success, we can find the compiled library in the `products` directory, which we can use as if we had compiled it manually.

Now that we've ensured everything works as expected, we can contribute our recipe to Yggdrasil. Fork the Yggdrasil repository, create a new directory for the recipe and put it in that directory. Commit these changes with a message like `"[{{crate_name}}] version 0.1.0"` and open a PR. If everything goes well and our PR is accepted, a new package will be published named `{{crate_name}}_jll`.

Using this JLL package is a matter of adding it to Julia:

```julia
(@v1.10) pkg> add {{crate_name}}_jll
   Resolving package versions...
  Downloaded artifact: {{crate_name}}
    Updating `~/.julia/environments/v1.10/Project.toml`
  [54eccfce] + {{crate_name}}_jll v0.1.0+0
    Updating `~/.julia/environments/v1.10/Manifest.toml`
  [54eccfce] + {{crate_name}}_jll v0.1.0+0
Precompiling project...
  1 dependency successfully precompiled in 2 seconds. 86 already precompiled. 1 skipped during auto due to previous errors.

julia> using {{crate_name}}_jll

julia> {{crate_name}}_jll.lib{{crate_name}}_path
"/path/to/lib{{crate_name}}.so"

julia> ccall((:some_exported_function, {{crate_name}}_jll.lib{{crate_name}}_path), Cvoid, ())

```

[Yggdrasil]: https://github.com/JuliaPackaging/Yggdrasil
[BinaryBuilder.jl documentation]: https://docs.binarybuilder.org/stable/
[recipe for the Rust toolchain]: https://github.com/JuliaPackaging/Yggdrasil/blob/master/0_RootFS/Rust/build_tarballs.jl
