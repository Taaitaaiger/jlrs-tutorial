# Other attributes

There are two attributes that we haven't covered yet: `super_type` and `bounds`. These attributes can be used to set the super type and bound on the type parameters in Julia.

The first works similarly to `key`. The syntax is `#[jlrs(super_type = "path::to::Type")]`, the type must implement `ConstructType` and must not use any of the type parameters. The latter restriction may be dropped in the future.

The second is admittedly of limited use, because the only variants that can be used are those that have been explicitly exported. Its syntax is very similar to Julia; just replace the upper (and/or lower) bound with the path to a constructible type: `#[jlrs(bounds = "T <: path::to::Type, ...")]`.
