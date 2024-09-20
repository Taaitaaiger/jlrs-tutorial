# Yggdrasil and jlrs

In the previous chapter we saw how we could write a recipe to build a Rust crate and contribute it to Yggdrasil to distribute it as a JLL package. When the crate we want to build depends on jlrs, we have to deal with a complication: we need to build the library against every version of Julia that we want to support, and enable the correct version feature at compile time. We'll also need to enable the `yggdrasil` feature. This requires a few adjustments to the recipe.

We're going to assume the crate re-exposes the version and `yggdrasil` features:

```toml
[features]
julia-1-6 = ["jlrs/julia-1-6"]
julia-1-7 = ["jlrs/julia-1-7"]
julia-1-8 = ["jlrs/julia-1-8"]
julia-1-9 = ["jlrs/julia-1-9"]
julia-1-10 = ["jlrs/julia-1-10"]
julia-1-11 = ["jlrs/julia-1-11"]
yggdrasil = ["jlrs/yggdrasil"]
```

The recipe should look as follows:

```julia
# Note that this script can accept some limited command-line arguments, run
# `julia build_tarballs.jl --help` to see a usage message.
using BinaryBuilder, Pkg

# See https://github.com/JuliaLang/Pkg.jl/issues/2942
# Once this Pkg issue is resolved, this must be removed
uuid = Base.UUID("a83860b7-747b-57cf-bf1f-3e79990d037f")
delete!(Pkg.Types.get_last_stdlibs(v"1.6.3"), uuid)

name = "{{crate_name}}"
version = v"0.1.0"
julia_versions = [v"1.6.3", v"1.7", v"1.8", v"1.9", v"1.10", v"1.11"]

# Collection of sources required to complete build
sources = [
    GitSource("https://github.com/{{user}}/{{crate_name}}.git",
              "{full commit hash, e.g.: 52ab80563a07d02e3d142f85101853bbf5c0a8a1}"),
]

# Bash recipe for building across all platforms
script = raw"""
cd $WORKSPACE/srcdir/{{crate_name}}

# This program prints the version feature that must be passed to `cargo build`
# Adapted from ../../G/GAP/build_tarballs.jl
# HACK: determine Julia version
cat > version.c <<EOF
#include <stdio.h>
#include "julia/julia_version.h"
int main(int argc, char**argv)
{
    printf("julia-%d-%d", JULIA_VERSION_MAJOR, JULIA_VERSION_MINOR);
    return 0;
}
EOF
${CC_BUILD} -I${includedir} -Wall version.c -o julia_version
julia_version=$(./julia_version)

cargo build --features yggdrasil,${julia_version} --release --verbose
install_license LICENSE
install -Dvm 0755 "target/${rust_target}/release/"*{{crate_name}}".${dlext}" "${libdir}/lib{{crate_name}}.${dlext}"
"""

include("../../L/libjulia/common.jl")
platforms = vcat(libjulia_platforms.(julia_versions)...)

# Rust toolchain for i686 Windows is unusable
is_excluded(p) = Sys.iswindows(p) && nbits(p) == 32
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
               preferred_gcc_version=v"10", julia_compat="1.6", compilers=[:c, :rust])
```

The main differences with the recipe for a crate that doesn't depend on jlrs are:

- The workaround for issue [#2942].
- The supported versions of Julia are set.
- A small executable that prints the version feature we need to enable is built and executed as part of the build script.
- `libjulia/common.jl` is included.
- Supported platforms are acquired via `libjulia_platforms`, not `supported_platforms`.
- `libjulia_jll` is added to the dependencies as a build dependency.

[#2942]: https://github.com/JuliaLang/Pkg.jl/issues/2942
