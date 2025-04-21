# Without generics

As mentioned before, `OpaqueType` can be derived if a type doesn't contain any references to either Rust or Julia data, and implements `Send` and `Sync`. A type that implements this trait must be exported with `struct {{Name}}`. Methods and associated functions can be exported with `in {{Type}} {{Signature}}`.

When an exported method is called from Julia, an instance of the opaque type must be used as the first argument. This data is tracked before it is converted to a reference, which guarantees that mutable aliasing is prevented. It's possible to opt out of tracking by annotating the export with `#[untracked_self]`, which is safe to use if no methods which take `&mut self` are exported. `#[gc_safe]` is also supported.

To create a constructor, we can export an (associated) function and rename it to the name of the type. The constructor must return either a `CCallRefRet`, a `TypedValueRet`, or a `ValueRet`; opaque types implement `IntoJulia`, so they can be converted with `(Typed)Value::new`. A finalizer that drops the data is automatically registered.

```rust,ignore
use jlrs::{
    data::managed::{ccall_ref::CCallRefRet, value::typed::TypedValue},
    prelude::*,
    weak_handle,
};

#[derive(Debug, OpaqueType)]
struct OpaqueInt {
    _a: i32,
}

impl OpaqueInt {
    fn new(a: i32) -> CCallRefRet<OpaqueInt> {
        match weak_handle!() {
            Ok(handle) => CCallRefRet::new(TypedValue::new(handle, OpaqueInt { _a: a }).leak()),
            Err(_) => panic!("not called from Julia"),
        }
    }

    fn print(&self) {
        println!("{:?}", self)
    }
}

julia_module! {
    become julia_module_tutorial_init_fn;

    struct OpaqueInt;

    in OpaqueInt fn new(a: i32) -> CCallRefRet<OpaqueInt> as OpaqueInt;

    #[untracked_self]
    in OpaqueInt fn print(&self);
}
```

```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> v =  JuliaModuleTutorial.OpaqueInt(Int32(3))
Main.JuliaModuleTutorial.OpaqueInt()

julia> JuliaModuleTutorial.print(v)
OpaqueInt { _a: 3 }
```
