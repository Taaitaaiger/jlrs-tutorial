# `OpaqueType`

The `OpaqueType` trait is the simplest way to expose a Rust type to Julia, for most intents and purposes it's just a marker trait. It's an unsafe trait because we have to initialize the type before we can use it, but this will be handled by exporting it. An opaque type can't reference managed data in any way: the layout of this type is unknown to Julia, so the GC would be unable to find those references. Besides not referencing any Julia data, it can't contain any references to Rust data either and must be thread-safe[^1]. An opaque type may only be used by the library that defines it.

Any type that implements `OpaqueType` can be exported by adding `struct {{Type}}` to `julia_module!`. When the initialization-function is called, a new mutable type with that name is created in the wrapping module.

A type just by itself isn't useful, if we tried to export it we'd find the type in our module, but we'd be unable to do anything with it. We can export an opaque type's associated functions and methods almost as easily as we can export other functions, the only additional thing we need to do is prefix the export with `in {{Type}}`. Methods can take `&self` and `&mut self`, if the type implements `Clone` it can also take `self`. The `self` argument is tracked before it's dereferenced to prevent mutable aliasing, it's possible to opt out of this by annotating the method with `#[untracked_self]`.

```rust,ignore
use jlrs::{
    data::{
        managed::{ccall_ref::CCallRefRet, value::typed::TypedValue},
        types::foreign_type::OpaqueType,
    },
    prelude::*,
    weak_handle,
};

#[derive(Debug)]
struct OpaqueInt {
    _a: i32,
}

unsafe impl OpaqueType for OpaqueInt {}

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

Note that `OpaqueInt::new` has been renamed to `OpaqueInt` to serve as a constructor. We don't need to track `self` when we call `print` because we never create a mutable reference to `self`.

[^1]: I.e., the type must be `'static`, `Send` and `Sync`.
