# Types and layouts

We've already seen a few different types in action, but we haven't really covered Julia's type system at all.

Every `Value` has a type, or `DataType`, which we can access at runtime.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 1>(|mut frame| {
        let v = Value::new(&mut frame, 1.0f32);
        let dt = v.datatype();
        println!("{:?}", dt);
    })
}
```

This example prints `Float32`, the `DataType` of a 32-bits floating point number in Julia. Internally, a `Value` is a pointer to some memory managed by Julia, and its `DataType` determines the layout of the memory it's pointing to.

There are three important traits that deal with this layout and type information: `ValidLayout`, `ValidField`, and `ConstructType`. They're all derivable traits, and should never be implemented manually. We'll cover the derivable traits and other code generation capabilities of jlrs later, for now it's only important to understand what these three traits encode.

`ValidLayout` can be implemented by types that represent the layout of a `DataType`. It's used to check that the layout in Rust and Julia match when converting them between languages at runtime. `ValidField` is similar, but is concerned with the layout of fields rather than the layout of types. The distinction is relevant because the layout of the type might not match the layout of the field with that type. Finally, `ConstructType` is used to construct Julia type objects from Rust types. The distinction is once again relevant because not all types have a layout, a layout doesn't necessarily map to a single type object, and sometimes we'll need to express a type that's more exotic than can be expressed with a layout.

Before we start to tackle Julia arrays where we'll see all these traits in action, we're going to look at how Julia data is laid out in memory first. The next sections are not intended as a guide how to match the layout of types in Rust and Julia, we normally never implement these representations manually, but it's useful to have a basic understanding of this topic.
