# Creating arrays

Functions that create new arrays can mostly be divided into two classes: `Typed(Ranked)Array` provides functions like `new` which use the given `T` to construct the element type, while `(Ranked)Array` provides similar functions postfixed with `_for`, e.g. `new_for`, which take the element type as an argument instead.

In addition to the element type, these functions take the desired dimensions of the array as an argument. Up to rank 4, tuples of `usize` can be used to express these dimensions. It's also possible to use `[usize; N]`, `&[usize; N]`, and `&[usize]`. If the rank of the array and the dimensions are known at compile time and they don't match, the code will fail to compile.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 2>(|mut frame| {
        let arr1 = TypedArray::<f32>::new(&mut frame, (2, 2))
            .expect("invalid size");
        assert_eq!(arr1.rank(), 2);

        let f32_ty = DataType::float32_type(&frame).as_value();
        let arr2 = RankedArray::<2>::new_for(&mut frame, f32_ty, [2, 2])
            .expect("invalid size");

        assert_eq!(arr1.element_type(), arr2.element_type());
    })
}
```

The `new(_for)` functions return an array whose elements haven't been initialized.[^1] It's also possible to wrap an existing `Vec` or slice with `from_vec(_for)` and `from_slice(_for)`. These functions require that the elements are laid out correctly for an array whose element type is `T`. If the layout of the elements is `U`, this layout must be correct for `T`. This connection is expressed with the `HasLayout` trait, which connects a type constructor with its layout type. They're the same type as long as no type parameters have been elided.

The `from_vec(_for)` functions take ownership of a `Vec`, which is dropped when the array is freed by the GC. The `from_slice(_for)` functions borrow their data from Rust instead. `Value` and `Array` have a second lifetime called `'data`. This lifetime is set to the lifetime of the borrow to prevent this array from being accessed after the borrow ends. Be aware that Julia is unaware of this lifetime, so there's nothing that prevents us from keeping the array alive by assigning it to a global variable or sending it to some background thread. It's your responsibility to guarantee this doesn't happen, which is one of the reasons why the methods to call Julia functions are unsafe.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 2>(|mut frame| {
        let data = vec![1.0f64, 2., 3., 4.];
        let arr = TypedArray::<f64>::from_vec(&mut frame, data, (2, 2))
            .expect("incompatible type and layout")
            .expect("invalid size");
        assert_eq!(arr.rank(), 2);

        let data = vec![1.0f64, 2., 3., 4.];
        let f64_ty = DataType::float64_type(&frame).as_value();
        let arr2 = RankedArray::<2>::from_vec_for(&mut frame, f64_ty, data, [2, 2])
            .expect("incompatible type and layout")
            .expect("invalid size");

        assert_eq!(arr.element_type(), arr2.element_type());
    });

    handle.local_scope::<_, 2>(|mut frame| {
        let mut data = vec![1.0f64, 2., 3., 4.];
        let arr = TypedArray::<f64>::from_slice(&mut frame, &mut data, (2, 2))
            .expect("incompatible type and layout")
            .expect("invalid size");
        assert_eq!(arr.rank(), 2);

        let mut data = vec![1.0f64, 2., 3., 4.];
        let f64_ty = DataType::float64_type(&frame).as_value();
        let arr2 = RankedArray::<2>::from_slice_for(&mut frame, f64_ty, &mut data, [2, 2])
            .expect("incompatible type and layout")
            .expect("invalid size");

        assert_eq!(arr.element_type(), arr2.element_type());
    })
}
```

The functions `from_slice_cloned(_for)` and `from_slice_copied(_for)` use `new(_for)` to allocate the array, then clone or copy the elements from a given slice to this array. These functions avoid the finalizer of `from_vec(_for)` and the lifetime limitations of `from_slice(_for)`, at the cost of cloning or copying the elements.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 2>(|mut frame| {
        let data = [1.0f64, 2., 3., 4.];
        let arr = TypedArray::<f64>::from_slice_cloned(&mut frame, &data, (2, 2))
            .expect("incompatible type and layout")
            .expect("invalid size");
        assert_eq!(arr.rank(), 2);

        let f64_ty = DataType::float64_type(&frame).as_value();
        let arr2 = RankedArray::<2>::from_slice_cloned_for(&mut frame, f64_ty, &data, [2, 2])
            .expect("incompatible type and layout")
            .expect("invalid size");

        assert_eq!(arr.element_type(), arr2.element_type());
    });

    handle.local_scope::<_, 2>(|mut frame| {
        let data = [1.0f64, 2., 3., 4.];
        let arr = TypedArray::<f64>::from_slice_copied(&mut frame, &data, (2, 2))
            .expect("incompatible type and layout")
            .expect("invalid size");
        assert_eq!(arr.rank(), 2);

        let f64_ty = DataType::float64_type(&frame).as_value();
        let arr2 = RankedArray::<2>::from_slice_copied_for(&mut frame, f64_ty, &data, [2, 2])
            .expect("incompatible type and layout")
            .expect("invalid size");

        assert_eq!(arr.element_type(), arr2.element_type());
    });
}
```

Finally, there are two specialized functions. `TypedVector::<Any>::new_any` allocates a vector that can hold elements of any type. `TypedVector::<u8>::from_bytes` can convert anything that can be referenced as a slice of bytes to a `TypedVector<u8>`, it's similar to `TypedVector::<u8>::from_slice_copied`.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 1>(|mut frame| {
        let arr = VectorAny::new_any(&mut frame, 3).expect("invalid size");
        assert_eq!(arr.rank(), 1);
    });

    handle.local_scope::<_, 2>(|mut frame| {
        let data = [1u8, 2, 3, 4];
        let arr = TypedVector::<u8>::from_bytes(&mut frame, &data).expect("invalid size");
        assert_eq!(arr.rank(), 1);

        let data = "also bytes";
        let arr = TypedVector::<u8>::from_bytes(&mut frame, &data).expect("invalid size");
        assert_eq!(arr.rank(), 1);
    });
}
```

[^1]: If the elements reference other managed data, the array storage will be initialized to 0.
