# `ForeignType`

Foreign types are a special kind of opaque type which may contain references to managed data, but can't have type parameters. Instead of `OpaqueType` directly, we'll need to derive `ForeignType`. The only attibute that still applies is `super_type`.

Like `OpaqueType`, a type can only implement `ForeignType` if it is `'static` and implements `Send` and `Sync`. This is problematic, since managed data has lifetimes and doesn't implement those traits. To work around the first issue, we need to use `Weak` data because it allows the `'scope`-lifetime to be erased. To work around the second, we'll need to manually implement `Send` and `Sync`. As long as the Rust parts of the type implement these traits, it should be fine to assume they can be implemented; all managed data is hidden behind `Weak`, which lets us ignore the issue until we actually try to access it because these considerations are already a part of the safety contract of accessing weakly-referenced managed data.

## Mark functions

Foreign types can reference managed data because they have custom mark functions. When the GC encounters an instance of a foreign type during the mark phase, this custom function is called to allow the GC to find those live references. If the type of a field implements the `Mark` trait, that field can simply be annotated with `#[jlrs((mark)]` to include it in the generated mark function. This trait is implemented for all `Weak` types, `Option<Weak>`, and arrays and `Vec`s of types that implement `Mark` themselves.

If a field has a type that references Julia data but doesn't implement `Mark`, e.g. `HashMap<String, WeakValue>`, we'll need to implement a custom marking function manually and annotate the field with `#[jlrs(mark_with = custom_mark_fn)]`. This custom function for `T` must have this signature: `unsafe fn custom_mark_fn<P: ForeignType>(&T, ptls: PTls, parent: &P) -> usize`. This is the same signature as `Mark::mark`; unlike `Mark`, custom fuctions can be implemented even for types defined in other crates.

To implement a custom mark function correctly, we must mark every instance of Julia data referenced by that type. In the case of `HashMap<String, WeakValue>`, this means iterating over all values in the map and calling `Mark::mark` on every one with the provided `ptls` and `parent`, and returning the sum of their return values.

## Write barriers

A custom mark function isn't the only thing we need to maintain GC invariants, we'll use the word object to refer to an instance of a managed type. The GC has two generations, young and old. A newly allocated object is young, if it survives a collection cycle it becomes old. The GC can do a full collection cycle and look at both generations, or an incremental one and just look at the young generation. If a young object is only referenced by an old one, we hit a snag: an incremental run only looks at young objects, so it should never see that reference in an old object and free it. To prevent this from happening, we have to insert a write barrier whenever we start referencing an object that might be young. Two cases where a write barrier must be inserted are setting a field to another object, and adding an object to a collection.

```rust,ignore
use std::collections::HashMap;

use jlrs::{
    data::{managed::value::{typed::{TypedValue, TypedValueRet}, ValueRet}, types::foreign_type::{mark::Mark, ForeignType}}, prelude::*,  weak_handle, weak_handle_unchecked
};

// We can introduce additional generics as long as they can be inferred.
unsafe fn mark_map<M: Mark, P: ForeignType>(
    data: &HashMap<(), M>,
    ptls: jlrs::memory::PTls,
    parent: &P,
) -> usize {
    data.values().map(|v| unsafe { v.mark(ptls, parent) }).sum()
}

#[derive(ForeignType)]
pub struct ForeignThing {
    #[jlrs(mark)]
    a: WeakValue<'static, 'static>,
    #[jlrs(mark_with = mark_map)]
    b: HashMap<(), WeakValue<'static, 'static>>,
}

unsafe impl Send for ForeignThing {}
unsafe impl Sync for ForeignThing {}

impl ForeignThing {
    pub fn new(value: Value<'_, 'static>) -> TypedValueRet<ForeignThing> {
        match weak_handle!() {
            Ok(handle) => {
                TypedValue::new(
                    handle,
                    ForeignThing {
                        a: value.leak(),
                        b: HashMap::default(),
                    },
                )
                .leak()
            },
            Err(_) => panic!("not called from Julia"),
        }
    }

    pub fn get(&self) -> ValueRet {
        unsafe { self.a.assume_owned().leak() }
    }

    pub fn set(&mut self, value: Value) {
        unsafe {
            self.a = value.assume_owned().leak();
            self.write_barrier(self.a, self);
        }
    }
}

julia_module! {
    become julia_module_tutorial_init_fn;

    struct ForeignThing;
    in ForeignThing fn new(value: Value<'_, 'static>) -> TypedValueRet<ForeignThing> as ForeignThing;
    in ForeignThing fn get(&self) -> ValueRet;
    in ForeignThing fn set(&mut self, value: Value);
}
```

```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> v =  JuliaModuleTutorial.ForeignThing(Float32(3.0))
Main.JuliaModuleTutorial.ForeignThing()

julia> JuliaModuleTutorial.get(v)
3.0

julia> JuliaModuleTutorial.set(v, Float32(4.0))

julia> JuliaModuleTutorial.get(v)
4.0
```
