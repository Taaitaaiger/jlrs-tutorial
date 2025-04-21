# Bindings and derivable traits

We've encountered several traits that shouldn't be implemented manually, but derived. These traits express connections between types in Rust and Julia and their properties.

The following traits can currently be derived:

- `ValidLayout`
  Expresses that the implementor represents the layout of one or more Julia types, i.e. it's a layout type.

- `ValidField`
  Expresses that the implementor represents the layout of one or more Julia types when used as a field of another type.

- `IsBits`
  Expresses that the implementor is the layout of an `isbits` type.

- `Typecheck`
  Lets the implementor be used with `DataType::is` and `Value::is`, the implementation calls `ValidLayout::valid_layout`.

- `IntoJulia`
  Lets the implementor be converted to managed data with `Value::new`.

- `Unbox`
  Lets the implementor be used as the target type of `Value::unbox`.

- `ConstructType`
  Lets the implementor be used as a type constructor.

- `HasLayout`
  Links a type constructor to its layout type.

- `CCallArg`
  Lets the implementor be used as an argument type of a function called via `ccall`.

- `CCallReturn`
  Lets the implementor be used as the return type of a function called via `ccall`.

- `Enum`
  Maps the implementor to a Julia enum.

We can use JlrsCore.jl to generate bindings to Julia types which derive these traits if applicable. These bindings provide an interface to existing Julia types, and can't be used to expose Rust types to Julia.
