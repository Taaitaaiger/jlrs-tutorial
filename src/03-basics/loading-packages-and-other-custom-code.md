# Loading packages and other custom code

Everything we've done so far has involved standard functionality that's available directly in jlrs and Julia, at worst we've had to evaluate some code to define a custom type. While it's nice that we can use this essential functionality, it's reasonable that we also want to make use of packages.

Any package that has been installed for the targeted version of Julia can be loaded with `LocalHandle::using`.[^1]

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 1>(|mut frame| {
        let dot = Module::main(&frame).global(&mut frame, "dot");
        assert!(dot.is_err());
    });

    // Safety: LinearAlgebra is a valid package name
    unsafe {
        handle.using("LinearAlgebra")
    }.expect("Package does not exist");

    handle.local_scope::<_, 1>(|mut frame| {
        let dot = Module::main(&frame).global(&mut frame, "dot");
        assert!(dot.is_ok());
    });
}
```

The function `dot` isn't defined in the `Main` module until we've called `handle.using("LinearAlgebra")`, which internally just evaluates `using LinearAlgebra`. To restrict our imports, we have to construct a `using` or `import` statement manually and evaluate it with `Value::eval_string`.

Every package we load must have been installed in advance. Unlike the REPL, trying to use a package that hasn't been installed doesn't lead to a prompt to install it, it just fails. After a package has been loaded, its root module can be accessed with `Module::package_root_module`.

Including a file with custom Julia code works similarly; any file can be loaded and evaluated with `LocalHandle::include`, which calls `Main.include` with the provided path. This works well for local development, but figuring out the correct path to the file when we distribute our code can become problematic. In this case it's better to include the content of the file with the `include_str!` macro and evaluate it with `Value::eval_string`.

[^1]: As long as we don't mess with the [`JULIA_DEPOT_PATH` environment variable]

[`JULIA_DEPOT_PATH` environment variable]: https://docs.julialang.org/en/v1/manual/environment-variables/#JULIA_DEPOT_PATH
