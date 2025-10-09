# Testing libraries

Testing a dynamic library is mostly a matter of embedding Julia in the testing application, but there are a few things to keep in mind.

- To embed Julia we have to enable a runtime feature, but such a feature must not be enabled for library crates under normal circumstances.
- To compile integration tests, we must build an `rlib`.
- We have to call the generated init-function before calling functions that our library exports to Julia.
- We can only call exported functions, not the generated `extern "C"` functions that would have been called from Julia.
- Testing requires unwinding on panics, and we normally want to abort.

To deal with the first two limitations we need to edit our `Cargo.toml` a bit.

```toml
[lib]
crate-type = ["cdylib", "rlib"]

[features]
rt = ["jlrs/local-rt"] # Or any other runtime feature
```

The `rt` feature must not be enabled by default, we must only enable it when we test our code: `cargo test --features rt`. As always, the limitation that Julia can only be initialized once per process applies. Each integration test file in the tests directory must only contain a single test that initializes Julia and calls the generated init function. Our crate can similarly use just one test function that initializes Julia, so it's easiest to stick with integration tests.

Let's test the following library:

```rust,ignore
use jlrs::{
    data::{
        managed::value::typed::{TypedValue, TypedValueRet},
        types::foreign_type::OpaqueType,
    },
    prelude::*,
    weak_handle,
};

#[derive(Debug)]
pub struct OpaqueInt {
    a: i32,
}

unsafe impl OpaqueType for OpaqueInt {}

impl OpaqueInt {
    pub fn new(a: i32) -> TypedValueRet<OpaqueInt> {
        match weak_handle!() {
            Ok(handle) => TypedValue::new(handle, OpaqueInt { a }).leak(),
            Err(_) => panic!("not called from Julia"),
        }
    }

    pub fn get_a(&self) -> i32 {
        self.a
    }

    pub fn set_a(&mut self, a: i32) {
        self.a = a;
    }
}

julia_module! {
    become testing_libraries_tutorial_init_fn;

    struct OpaqueInt;

    in OpaqueInt fn new(a: i32) -> TypedValueRet<OpaqueInt> as OpaqueInt;
    in OpaqueInt fn get_a(&self) -> i32;
    in OpaqueInt fn set_a(&mut self, a: i32);
}
```

We'll call our library `testing_libraries_tutorial`. We can test it as follows:

```rust,ignore
use jlrs::prelude::*;
use testing_libraries_tutorial::{testing_libraries_tutorial_init_fn, OpaqueInt};

fn create_opaque_int<'target, Tgt: Target<'target>>(target: &Tgt) {
    target.local_scope::<_, 1>(|mut frame| {
        let opaque_int_ref = OpaqueInt::new(0);

        // Safety: we immediately root the unrooted data.
        let opaque_int = unsafe { opaque_int_ref.root(&mut frame) };

        // Safety: this data hasn't been released to Julia yet
        let tracked = unsafe { opaque_int.track_shared() }.expect("already tracked");

        let a = tracked.get_a();
        assert_eq!(a, 0);
    });
}

fn mutate_opaque_int<'target, Tgt: Target<'target>>(target: &Tgt) {
    target.local_scope::<_, 1>(|mut frame| {
        let opaque_int_ref = OpaqueInt::new(0);

        // Safety: we immediately root the unrooted data.
        let mut opaque_int = unsafe { opaque_int_ref.root(&mut frame) };

        {
            // Safety: this data hasn't been released to Julia yet
            let mut tracked = unsafe { opaque_int.track_exclusive() }.expect("already tracked");
            tracked.set_a(1);
        }

        {
            // Safety: this data hasn't been released to Julia yet
            let tracked = unsafe { opaque_int.track_shared() }.expect("already tracked");
            let a = tracked.get_a();
            assert_eq!(a, 1);
        }
    });
}

#[test]
fn it_works() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 0>(|frame| {
        // Safety: we only call the init function once, all exported types
        // will be created in the `Main` module. The second argument must
        // be set to 1.
        unsafe { testing_libraries_tutorial_init_fn(Module::main(&frame), 1) };

        create_opaque_int(&frame);
        mutate_opaque_int(&frame);
    })
}
```

We can see in these tests that we can track a `TypedValue` to acquire a reference to its internal data, which lets us call the type's methods. This matches the behavior of the generated `extern "C"` functions when they haven't been annotated with `#[untracked_self]`. If this annotation is present and we want to avoid tracking, we can access the internal pointer of a `Value` directly with `Value::data_ptr` and dereferencing it accordingly.
