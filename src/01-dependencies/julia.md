# Julia

jlrs currently supports Julia 1.6 up to and including Julia 1.11. Using the most recent stable version is recommended. While juliaup can be used, manually installing Julia is recommended. The reason is that to compile jlrs successfully, the path to the Julia's header files and library must be known and this can be tricky to achieve with juliaup.

There are several platform-dependent ways to make these paths known:

#### Linux

If `julia` is on your `PATH` at `/path/to/bin/julia`, the main header file is expected to live at `/path/to/include/julia/julia.h` and the library at `/path/to/lib/libjulia.so`. If you do not want to add `julia` to your `PATH`, you can set the `JULIA_DIR` environment variable instead. If `JULIA_DIR=/path/to`, the headers and library must live at the previously mentioned paths.

The directory that contains `libjulia.so` must be on the library search path. If this is not the case and the library lives at `/path/to/lib/libjulia.so`, you must add `/path/to/lib/` to the `LD_LIBRARY_PATH` environment variable.

#### Windows

If `julia` is on your `Path` at `X:\path\to\bin\julia.exe`, the main header file is expected to live at `X:\path\to\include\julia\julia.h` and the library at `X:\path\to\bin\libjulia.dll`. You can set the `JULIA_DIR` environment variable instead. If `JULIA_DIR=X:\path\to`, the headers and library must live at the previously mentioned paths.

The directory that contains `libjulia.dll` must be on your `Path` at runtime if Julia is embedded.

#### MacOS

If `julia` is on your `PATH` at `/path/to/bin/julia`, the main header file is expected to live at `/path/to/include/julia/julia.h` and the library at `/path/to/lib/libjulia.dylib`. If you do not want to add `julia` to your `PATH`, you can set the `JULIA_DIR` environment variable instead. If `JULIA_DIR=/path/to`, the headers and library must live at the previously mentioned paths.

The directory that contains `libjulia.dylib` must be on the library search path. If this is not the case and the library lives at `/path/to/lib/libjulia.dylib`, you must add `/path/to/lib/` to the `DYLD_LIBRARY_PATH` environment variable.
