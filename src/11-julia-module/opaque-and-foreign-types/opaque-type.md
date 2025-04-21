# `OpaqueType`

The `OpaqueType` trait is the simplest way to expose a Rust type to Julia. When an opaque type is exported a new mutable type in Julia is created that can contain an instance of that type, Julia is unaware of the internal layout of the type.

Be aware `OpaqueType` is an unsafe trait. We have to initialize the type before we can use, which is handled by exporting it, and must not access its contents outside of our library. An opaque type must not reference managed data in any way: the layout of this type is unknown to Julia, so the GC would be unable to find those references. It can't contain any references to Rust data either; it must be `'static`, and implement `Send` and `Sync`. Rust doesn't have a stable ABI and libraries can be built with different versions of Rust, so it's unsound to access opaque data outside the library that has exported it.

Types that implement `OpaqueType` automatically implement the following traits: `IntoJulia`, `ConstructType`, `Typecheck`, and `ValidLayout`. If the type implements `Clone`, `Unbox` is also implemented.

We can derive `OpaqueType` if a type meets these constraints. Let's look at a few examples.
