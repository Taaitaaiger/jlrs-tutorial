# `ForeignType`

Foreign types are very similar to opaque types, the main difference is that a foreign type can contain references to managed data. Instead of `OpaqueType` we'll need to implement `ForeignType`. When we implement this trait, we have to provide a mark function to let the GC find these references.

Like `OpaqueType`, implementations of `ForeignType` must be thread-safe. A foreign type may only be used in the library that defines it. Fields that reference managed data must use `Ret`-aliases because the `'scope` lifetime has to be erased. One thing that's important to keep in mind is that we whenever we change what managed data is referenced by a field, we must insert a write barrier after this mutation. See [this footnote] for more information.

To implement the associated `mark` function[^1] we'll need to use `mark_queue_obj` and `mark_queue_objarray` to mark every reference to managed data. We need to sum the result of every call to `mark_queue_obj` and return this sum; `mark_queue_objarray` can be used to mark a slice of references to managed data, this operation doesn't affect the sum.

```rust,ignore
use jlrs::{
    data::{
        managed::value::{
            typed::{TypedValue, TypedValueRet},
            ValueRet,
        },
        memory::PTls,
        types::foreign_type::ForeignType,
    },
    memory::gc::{mark_queue_obj, write_barrier},
    prelude::*,
    weak_handle,
};

pub struct ForeignWrapper {
    a: ValueRet,
    b: ValueRet,
}

// Safety: Tracking `self` guarantees access to a `ForeignWrapper` is thread-safe.
unsafe impl Send for ForeignWrapper {}
unsafe impl Sync for ForeignWrapper {}

unsafe impl ForeignType for ForeignWrapper {
    fn mark(ptls: PTls, data: &Self) -> usize {
        // Safety: We mark all referenced managed data.
        unsafe {
            let mut n_marked = 0;
            n_marked += mark_queue_obj(ptls, data.a) as usize;
            n_marked += mark_queue_obj(ptls, data.b) as usize;
            n_marked
        }
    }
}

impl ForeignWrapper {
    fn new(a: Value<'_, 'static>, b: Value<'_, 'static>) -> TypedValueRet<ForeignWrapper> {
        match weak_handle!() {
            Ok(handle) => {
                let data = ForeignWrapper {
                    a: a.leak(),
                    b: b.leak(),
                };
                TypedValue::new(handle, data).leak()
            }
            Err(_) => panic!("not called from Julia"),
        }
    }

    fn set_a(&mut self, a: Value<'_, 'static>) {
        // Safety: we insert a write barrier after mutating the field
        unsafe {
            self.a = a.leak();
            write_barrier(self, a);
        }
    }

    fn get_a(&self) -> ValueRet {
        self.a
    }
}

julia_module! {
    become julia_module_tutorial_init_fn;

    struct ForeignWrapper;

    in ForeignWrapper fn new(a: Value<'_, 'static>, b: Value<'_, 'static>)
        -> TypedValueRet<ForeignWrapper> as ForeignWrapper;

    in ForeignWrapper fn set_a(&mut self, a: Value<'_, 'static>);

    in ForeignWrapper fn get_a(&self) -> ValueRet;
}
```

```julia
julia> module JuliaModuleTutorial ... end
Main.JuliaModuleTutorial

julia> x = JuliaModuleTutorial.ForeignWrapper(1, 2)
Main.JuliaModuleTutorial.ForeignWrapper()

julia> JuliaModuleTutorial.get_a(x)
1

julia> JuliaModuleTutorial.set_a(x, 4)

julia> JuliaModuleTutorial.get_a(x)
4
```

[this footnote]: ../../11-ccall-basics/argument-types/argument-types.md#1

[^1]: Yes, the signature of `mark` is odd. It takes `PTls` as its first argument for consistency with `mark_queue_*` and other functions in the Julia C API which take `PTls` explicitly.
