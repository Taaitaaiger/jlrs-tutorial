# Union fields

The representation of a field with a `Union` type depends on the union's variants. If all variants are `isbits` types an optimization applies and the field is inlined, otherwise the field is represented as `Option<ValueRef>`. We'll see later that a similar optimization applies to arrays.

The presence of a union field doesn't affect whether the layout type can implement `ValidLayout`, `ValidField`, and `ConstructType`.

It's not particularly important to know how an inlined union can be represented in Rust, so no example will be provided.
