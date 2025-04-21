# Throwing exceptions

Throwing an exception is a matter of returning either `Result<T, ValueRet>` or `JlrsResult<T>`. If the error variant is returned it's thrown as an exception, otherwise the result is unwrapped and returned to Julia.

```rust,ignore
use jlrs::{data::managed::value::ValueRet, prelude::*, weak_handle};

fn throws_exception() -> Result<(), ValueRet> {
    match weak_handle!() {
        Ok(handle) => {
            // We're just throwing (and catching) an exception
            let res = unsafe { Value::eval_string(&handle, "throw(ErrorException(\"Oops\"))") };
            match res {
                Ok(_) => Ok(()),
                Err(e) => Err(e.leak()),
            }
        }
        _ => panic!("not called from Julia"),
    }
}

julia_module! {
    become julia_module_tutorial_init_fn;

    fn throws_exception() -> Result<(), ValueRet>;
}
```

```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> JuliaModuleTutorial.throws_exception()
ERROR: Oops
Stacktrace:
 [1] top-level scope
   @ REPL[2]:1
```

Many methods in jlrs have a name ending in `unchecked`, these methods don't catch exceptions. If such a method is called and an exception is thrown, there must be no pending drops because control flow will directly jump back to Julia. It's recommended to always catch exceptions and rethrow them as in the example.
