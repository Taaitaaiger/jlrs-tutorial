# Tracking arrays

It's trivial to create multiple mutable accessors to the same array. A band-aid is available: jlrs can track managed data to prevent mutable aliasing in Rust code to a degree. An array can be tracked exclusively or shared with the `track_exclusive` and `track_shared` methods available to all array types. `track_shared` succeeds as long as the array isn't already tracked exclusively, `track_exclusive` enforces exclusive access.

Overall, tracking can make accessing arrays safer as long as it's used consistently, but it's unaware of accesses in Julia code.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    // Shared tracking
    handle.local_scope::<_, 1>(|mut frame| {
        let data = [1.0f64, 2., 3., 4.];
        let arr = TypedArray::<f64>::from_slice_copied(&mut frame, &data, [2, 2])
            .expect("incompatible type and layout")
            .expect("invalid size");

        let tracked = arr.track_shared().expect("already tracked exclusively");
        assert!(arr.track_exclusive().is_err());
        assert!(arr.track_shared().is_ok());

        let accessor = tracked.bits_data();

        let elem = accessor[[1, 0]];
        assert_eq!(elem, 2.);
    });

    // Exclusive tracking
    handle.local_scope::<_, 1>(|mut frame| {
        let data = [1.0f64, 2., 3., 4.];
        let arr = TypedArray::<f64>::from_slice_copied(&mut frame, &data, [2, 2])
            .expect("incompatible type and layout")
            .expect("invalid size");

        let tracked = arr.track_exclusive().expect("already tracked exclusively");
        assert!(arr.track_exclusive().is_err());
        assert!(arr.track_shared().is_err());

        let accessor = tracked.bits_data();

        let elem = accessor[[1, 0]];
        assert_eq!(elem, 2.);
    });
}
```
