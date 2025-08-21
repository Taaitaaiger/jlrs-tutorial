# Mutating arrays

In addition to the immutable accessors we've seen in the previous section, jlrs also provides mutable accessors.

Methods like `(try_)bits_data_mut` and types like `BitsAccessorMut` exist analogously to the immutable variants. The methods provided by the mutable accessors have names similar to their immutable counterparts. Some accessors don't provide direct mutable access to an element; they don't implement `IndexMut` or provide a `set_mut` method. In this case we'll need to use `AccessorMut::set_value`.

Mutating managed data from Rust is generally unsafe in jlrs. The reason essentially boils down to "just because you have access to a mutable value doesn't mean you're allowed to mutate it." Strings are a good example, they're mutable but it's UB to mutate them. Array accessors are a bit special in this regard: it's unsafe to create a mutable accessor, but many of their mutating methods are safe. The safety-requirements are implied by the requirements of creating a mutable accessor in the first place.

The array types implement `Copy` so it's trivial to create two mutable accessors to the same array, or multiple mutable and immutable accessor in general. It's your responsibility to ensure this doesn't happen. It's possible to avoid this issue to a degree by tracking the array, which we'll cover later in this chapter.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    // IndeterminateAccessorMut
    handle.local_scope::<_, 4>(|mut frame| {
        let data = [1.0f64, 2., 3., 4.];
        let f64_ty = DataType::float64_type(&frame).as_value();
        let mut arr = RankedArray::<2>::from_slice_copied_for(&mut frame, f64_ty, &data, [2, 2])
            .expect("incompatible type and layout")
            .expect("invalid size");

        // Safety: this is the only accessor to this data.
        let mut accessor = unsafe { arr.indeterminate_data_mut() };

        let v = Value::new(&mut frame, 5.0f64);
        accessor.set_value(&mut frame, [1, 0], v).expect("index out of bounds").expect("caught exception");

        let elem = accessor
            .get_value(&mut frame, [1, 0])
            .expect("out of bounds")
            .expect("undefined reference")
            .unbox::<f64>()
            .expect("wrong type");
        assert_eq!(elem, 5.);
    });

    // BitsAccessorMut
    handle.local_scope::<_, 1>(|mut frame| {
        let data = [1.0f64, 2., 3., 4.];
        let mut arr = TypedArray::<f64>::from_slice_copied(&mut frame, &data, [2, 2])
            .expect("incompatible type and layout")
            .expect("invalid size");

        // Safety: this is the only accessor to this data.
        let mut accessor = unsafe { arr.bits_data_mut() };

        let elem = accessor[[1, 0]];
        assert_eq!(elem, 2.);

        accessor[[1, 0]] = 4.;
        let elem = accessor[[1, 0]];
        assert_eq!(elem, 4.);
    });

    // InlineAccessorMut
    handle.local_scope::<_, 2>(|mut frame| {
        let data = [1.0f64, 2., 3., 4.];
        let mut arr = TypedArray::<f64>::from_slice_copied(&mut frame, &data, [2, 2])
            .expect("incompatible type and layout")
            .expect("invalid size");

        // Safety: this is the only accessor to this data.
        let mut accessor = unsafe { arr.inline_data_mut() };

        let elem = accessor[[1, 0]];
        assert_eq!(elem, 2.);

        let v = Value::new(&mut frame, 4.0f64);
        accessor
            .set_value(&mut frame, [1, 0], v)
            .expect("index out of bounds")
            .expect("caught an exception");

        let elem = accessor[[1, 0]];
        assert_eq!(elem, 4.);
    });

    // ValueAccessorMut
    handle.local_scope::<_, 3>(|mut frame| {
        // Safety: this code only allocates and returns an array
        let mut arr = unsafe { Value::eval_string(&mut frame, "Any[:foo, :bar]") }
            .expect("caught an exception")
            .cast::<VectorAny>()
            .expect("not a VectorAny");

        // Safety: this is the only accessor to this data.
        let mut accessor = unsafe { arr.value_data_mut() };

        let v = Value::new(&mut frame, 1usize);
        accessor
            .set_value(&mut frame, 0, v)
            .expect("out of bounds")
            .expect("caught an exception");

        let elem = accessor.get(&mut frame, 0).expect("out of bounds");
        assert_eq!(v, elem);
    });

    // ManagedAccessorMut
    handle.local_scope::<_, 4>(|mut frame| {
        // Safety: this code only allocates and returns an array
        let mut arr = unsafe { Value::eval_string(&mut frame, "Symbol[:foo, :bar]") }
            .expect("caught an exception")
            .cast::<TypedVector<Symbol>>()
            .expect("not a TypedVector<Symbol>");

        // Safety: this is the only accessor to this data.
        let mut accessor = unsafe { arr.managed_data_mut() };

        let sym = Symbol::new(&mut frame, "baz");
        accessor
            .set_value(&mut frame, 0, sym.as_value())
            .expect("out of bounds")
            .expect("caught an exception");

        let elem = accessor.get(&mut frame, 0).expect("out of bounds");
        assert_eq!(sym, elem);
    });

    // BitsUnionAccessorMut
    handle.local_scope::<_, 1>(|mut frame| {
        // Safety: this code only allocates and returns an array
        let mut arr =
            unsafe { Value::eval_string(&mut frame, "Union{Int, Float64}[1.0 2; 3 4.0]") }
                .expect("caught an exception")
                .cast::<Matrix>()
                .expect("not a Matrix");

        // Safety: this is the only accessor to this data.
        let mut accessor = unsafe { arr.try_union_data_mut().expect("wrong accessor") };

        accessor
            .set([1, 0], DataType::float64_type(&frame), 4.0f64)
            .expect("out of bounds or incompatible type")
            .expect("caught an exception");

        let elem = accessor
            .get::<f64, _>([1, 0])
            .expect("wrong layout")
            .expect("out of bounds");
        assert_eq!(elem, 4.0);
    });
}
```
