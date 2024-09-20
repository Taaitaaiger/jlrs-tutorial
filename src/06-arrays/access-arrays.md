# Accessing arrays

The different array types don't provide direct access to their data, we'll need to create an accessor first. There are multiple accessor types, and the one that must be used depends on the layout of the elements.

A quick note on safety: never access an array that's already accessed mutably, either in Rust or Julia code.

It's possible to completely ignore the layout of the elements with an `IndeterminateAccessor`. It can be created with the `ArrayBase::indeterminate_data` method. It implements the `Accessor` trait which provides a `get_value` method which returns the element as a `Value`. Unlike Julia, array indexing starts at 0.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 2>(|mut frame| {
        let data = [1.0f64, 2., 3., 4.];
        let f64_ty = DataType::float64_type(&frame).as_value();
        let arr = RankedArray::<2>::from_slice_copied_for(&mut frame, f64_ty, &data, [2, 2])
            .expect("incompatible type and layout")
            .expect("invalid size");

        // Safety: we never mutably access this data.
        let accessor = unsafe { arr.indeterminate_data() };

        let a21 = accessor
            .get_value(&mut frame, [1, 0])
            .expect("out of bounds")
            .expect("undefined reference")
            .unbox::<f64>()
            .expect("wrong type");

        assert_eq!(a21, 2.);
    });
}
```

We've seen in the previous chapter that there are three ways a field of a composite type can be stored: it can be stored inline, as a reference to managed data, or as an inlined union. An array element is stored as if it were a field of a composite type with one minor exception, there's a difference between how inlined unions are stored in composite types and arrays.[^1]

There's a separate accessor for each of these layouts: `InlineAccessor`, `ValueAccessor`, and `BitsUnionAccessor`. There are two additional accessors, `BitsAccessor` and `ManagedAccessor`. The first can be used with layouts that implement the `IsBits` trait and the latter with arbitrary managed types like `Module` and `DataType`.

If a `Typed(Ranked)Array` is used the correct accessor might be inferred from that type's `T` parameter. Some of these methods will be available in that case: `inline_data`, `value_data`, `union_data`, `bits_data`, and `managed_data`. Methods prefixed with `try_`, e.g. `try_bits_data`, are generally available for all array types. These methods check if the correct accessor has been requested at runtime. Methods like `ArrayBase::has_bits_layout` can be used to check if an accessor is compatible with the layout of the elements.

All these accessor types implement `Accessor`, and additionally provide a `get` function to access an element at some index. Excluding the `BitsUnionAccessor`, they also implement `Index`. These implementations accept the same multidimensional indices as the functions that create new arrays do. The `as_slice` and `into_slice` methods provided by the indexable types let us ignore the multidimensionality and access the data as a slice in column-major order.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    // BitsAccessor
    handle.local_scope::<_, 1>(|mut frame| {
        let data = [1.0f64, 2., 3., 4.];
        let arr = TypedArray::<f64>::from_slice_copied(&mut frame, &data, [2, 2])
            .expect("incompatible type and layout")
            .expect("invalid size");

        // Safety: we never mutably access this data.
        let accessor = unsafe { arr.bits_data() };

        let a11 = accessor[[0, 0]];
        assert_eq!(a11, 1.);

        let a21 = accessor[[1, 0]];
        assert_eq!(a21, 2.);

        let a12 = accessor[[0, 1]];
        assert_eq!(a12, 3.);

        let a22 = accessor[[1, 1]];
        assert_eq!(a22, 4.);
    });

    // InlineAccessor
    handle.local_scope::<_, 1>(|mut frame| {
        let data = [1.0f64, 2., 3., 4.];
        let arr = TypedArray::<f64>::from_slice_copied(&mut frame, &data, [2, 2])
            .expect("incompatible type and layout")
            .expect("invalid size");

        // Safety: we never mutably access this data.
        let accessor = unsafe { arr.inline_data() };

        let elem = accessor[[1, 0]];
        assert_eq!(elem, 2.);
    });

    // ValueAccessor
    handle.local_scope::<_, 2>(|mut frame| {
        // Safety: this code only allocates and returns an array
        let arr = unsafe { Value::eval_string(&mut frame, "Any[:foo, :bar]") }
            .expect("caught an exception")
            .cast::<VectorAny>()
            .expect("not a VectorAny");

        // Safety: we never mutably access this data.
        let accessor = unsafe { arr.value_data() };

        let elem = accessor.get_value(&mut frame, 0)
            .expect("out of bounds")
            .expect("undefined reference");
        let sym = Symbol::new(&frame, "foo");
        assert_eq!(elem, sym);
    });

    // ManagedAccessor
    handle.local_scope::<_, 2>(|mut frame| {
        // Safety: this code only allocates and returns an array
        let arr = unsafe { Value::eval_string(&mut frame, "Symbol[:foo, :bar]") }
            .expect("caught an exception")
            .cast::<TypedVector<Symbol>>()
            .expect("not a TypedVector<Symbol>");

        // Safety: we never mutably access this data.
        let accessor = unsafe { arr.managed_data() };

        let elem = accessor.get(&mut frame, 0).expect("undefined reference or out of bounds");
        let sym = Symbol::new(&frame, "foo");
        assert_eq!(elem, sym);
    });

    // BitsUnionAccessor
    handle.local_scope::<_, 1>(|mut frame| {
        // Safety: this code only allocates and returns an array
        let arr = unsafe { Value::eval_string(&mut frame, "Union{Int, Float64}[1.0 2; 3 4.0]") }
            .expect("caught an exception")
            .cast::<Matrix>()
            .expect("not a Matrix");

        // Safety: we never mutably access this data.
        let accessor = unsafe { arr.try_union_data().expect("wrong accessor") };

        let elem = accessor.get::<isize, _>([1, 0]).expect("wrong layout").expect("out of bounds");
        assert_eq!(elem, 3);
    });
}
```

[^1]: In composite types, the data and the tag that identifies its type are stored adjacently, in an array the flags are collectively stored after the data.
