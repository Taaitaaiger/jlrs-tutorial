# Arrays

So far we've only worked with relatively simple types, now it's time to look at the `Array` type. The first thing that makes this type more complex are its type parameters, the element type `T` and rank `N`, which have special handling compared to other type parameters in jlrs.

This special handling involves a single base type, `ArrayBase<T, const N: isize>`, and aliases for the four possible cases:

 - `Array == ArrayBase<Unknown, -1>`
 - `TypedArray<T> == ArrayBase<T, -1>`
 - `RankedArray<const N: isize> == ArrayBase<Unknown, N>`
 - `TypedRankedArray<T, const N: isize> == ArrayBase<T, N>`

As can be seen in this list it's possible to ignore the element type and rank of an array. A known element type must implement `ConstructType`, a known rank is greater than or equal to 0.

There are a few additional specialized type aliases:

 - `Vector == RankedArray<1>`
 - `TypedVector<T> == TypedRankedArray<T, 1>`
 - `VectorAny == TypedVector<Any>`
 - `Matrix == RankedArray<2>`
 - `TypedMatrix<T> == TypedRankedArray<T, 2>`

The elements of Julia arrays are stored in column-major order, which is also known as "F" or "Fortran" order. The sequence `1, 2, 3, 4, 5, 6` maps to the following 2 x 3 matrix:

```text
1  3  5
2  4  6
```

i.e.

```julia
[1 3 5; 2 4 6]
```
