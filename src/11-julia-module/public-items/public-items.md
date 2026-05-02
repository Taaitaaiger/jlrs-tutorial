# Public items

The items that can be exported with `julia_module!` can be marked with `pub`, these items will be exported by the generated module. If a function is exported multiple times, all these functions must be marked `pub`.

<!-- LIBTEST START -->
```rust,ignore
use jlrs::prelude::*;

fn return_first_arg<T>(a: T, _b: T) -> T {
    a
}

julia_module! {
    become julia_module_tutorial_init_fn;

    pub fn return_first_arg(a: isize, b: isize) -> isize;
    pub fn return_first_arg(a: f64, b: f64) -> f64;
}
```
<!-- LIBTEST END -->
