# ndarray

`BitsAccessor`, `InlineAccessor`, and `BitsAccessorMut` are compatible with ndarray via the `NdArrayView` and `NdArrayViewMut` traits. This requires enabling jlrs's `jlrs-ndarray` feature.

```rust,ignore
use jlrs::{
    convert::ndarray::{NdArrayView, NdArrayViewMut},
    prelude::*,
};

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    // BitsAccessor as ArrayView
    handle.local_scope::<_, 1>(|mut frame| {
        let data = [1.0f64, 2., 3., 4.];
        let arr = TypedArray::<f64>::from_slice_copied(&mut frame, &data, [2, 2])
            .expect("incompatible type and layout")
            .expect("invalid size");

        // Safety: we never mutably access this data.
        let accessor = unsafe { arr.bits_data() };
        let view = accessor.array_view();

        let a21 = view[[1, 0]];
        assert_eq!(a21, 2.);
    });

    // InlineAccessor as ArrayView
    handle.local_scope::<_, 1>(|mut frame| {
        let data = [1.0f64, 2., 3., 4.];
        let arr = TypedArray::<f64>::from_slice_copied(&mut frame, &data, [2, 2])
            .expect("incompatible type and layout")
            .expect("invalid size");

        // Safety: we never mutably access this data.
        let accessor = unsafe { arr.inline_data() };
        let view = accessor.array_view();

        let elem = view[[1, 0]];
        assert_eq!(elem, 2.);
    });

    // BitsAccessorMut as ArrayViewMut
    handle.local_scope::<_, 1>(|mut frame| {
        let data = [1., 2., 3., 4.];
        let mut arr = TypedArray::<f64>::from_slice_copied(&mut frame, &data, [2, 2])
            .expect("incompatible type and layout")
            .expect("invalid size");

        // Safety: this is the only accessor to this data.
        let mut accessor = unsafe { arr.bits_data_mut() };
        let mut view = accessor.array_view_mut();

        let elem = view[[1, 0]];
        assert_eq!(elem, 2.);

        view[[1, 0]] = 4.;
        let elem = view[[1, 0]];
        assert_eq!(elem, 4.);
    });
}
```
