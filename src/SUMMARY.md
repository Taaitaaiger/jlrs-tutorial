# Summary

[Introduction](./00-introduction.md)

# Getting started

- [Dependencies](./01-dependencies/dependencies.md)
  - [Julia](./01-dependencies/julia.md)
  - [Rust](./01-dependencies/rust.md)
  - [C](./01-dependencies/c.md)

- [Version features](./02-version-features/version-features.md)

- [Basics](./03-basics/basics.md)
  - [Project setup](./03-basics/project-setup.md)
  - [Scopes and evaluating Julia code](./03-basics/scopes-and-evaluating-julia-code.md)
  - [Managed data and functions](./03-basics/julia-data-and-functions.md)
  - [Casting, unboxing and accessing managed data](./03-basics/casting-unboxing-and-accessing-julia-data.md)
  - [Loading packages and other custom code](./03-basics/loading-packages-and-other-custom-code.md)

# Getting familiar

- [Targets](./04-memory-management.md/memory-management.md)
  - [Using targets and nested scopes](./04-memory-management.md/using-targets.md)
  - [Target types](./04-memory-management.md/target-types.md)
    - [Local targets](./04-memory-management.md/local-targets.md)
    - [Dynamic targets](./04-memory-management.md/dynamic-targets.md)
    - [Non-rooting targets](./04-memory-management.md/non-rooting-targets.md)

- [Types and layouts](./05-types-and-layouts/types-and-layouts.md)
  - [`isbits` layouts](./05-types-and-layouts/isbits-layouts.md)
  - [Inline and non-inline layouts](./05-types-and-layouts/inline-and-non-inline-layouts.md)
  - [Union fields](./05-types-and-layouts/union-fields.md)
  - [Generics](./05-types-and-layouts/generics.md)

- [Arrays](./06-arrays/arrays.md)
  - [Creating arrays](./06-arrays/create-arrays.md)
  - [Accessing arrays](./06-arrays/access-arrays.md)
  - [Mutating arrays](./06-arrays/mutate-arrays.md)
  - [`ndarray`](./06-arrays/ndarray.md)
  - [Tracking arrays](./06-arrays/track-arrays.md)

- [Exception handling](./07-exception-handling/exception-handling.md)
  - [Parachutes](./07-exception-handling/parachutes.md)

- [Bindings and derivable traits](./08-bindings-and-derivable-traits/bindings-and-derivable-traits.md)
  - [Generating bindings](./08-bindings-and-derivable-traits/generating-bindings.md)
  - [Customizing bindings](./08-bindings-and-derivable-traits/customizing-bindings.md)

# Other runtimes

- [Multithreaded runtime](./09-multithreaded-runtime/multithreaded-runtime.md)
  - [Garbage collection, locks, and other blocking functions](./09-multithreaded-runtime/garbage-collection-locks-and-other-blocking-functions.md)

- [Async runtime](./10-async-runtime/async-runtime.md)
  - [Blocking tasks](./10-async-runtime/blocking-tasks.md)
  - [Async tasks](./10-async-runtime/async-tasks.md)
  - [Persistent tasks](./10-async-runtime/persistent-tasks.md)
  - [Combining the multithreaded and async runtimes](./10-async-runtime/combining-the-multithreaded-and-async-runtimes.md)

# Dynamic libraries

- [ccall basics](./11-ccall-basics/ccall-basics.md)
  - [Argument types](./11-ccall-basics/argument-types/argument-types.md)
    - [Arrays](./11-ccall-basics/argument-types/arrays.md)
  - [Return type](./11-ccall-basics/return-type.md)
  - [Dynamic libraries](./11-ccall-basics/dynamic-libraries.md)
  - [Custom types](./11-ccall-basics/custom-types.md)
  - [Yggdrasil](./11-ccall-basics/yggdrasil.md)

- [`julia_module!`](./12-julia-module/julia-module.md)
  - [Constants](./12-julia-module/constants/constants.md)
  - [Functions](./12-julia-module/functions/functions.md)
    - [Managed arguments](./12-julia-module/functions/managed-arguments.md)
    - [Array arguments](./12-julia-module/functions/array-arguments.md)
    - [Typed values](./12-julia-module/functions/typed-values.md)
    - [Typed layouts](./12-julia-module/functions/typed-layouts.md)
    - [Returning managed data](./12-julia-module/functions/returning-managed-data.md)
    - [`CCallRef`](./12-julia-module/functions/ccall-ref.md)
    - [Throwing exceptions](./12-julia-module/functions/throwing-exceptions.md)
    - [GC-safety](./12-julia-module/functions/gc-safety.md)
  - [Opaque and foreign types](./12-julia-module/opaque-and-foreign-types/opaque-and-foreign-types.md)
    - [`OpaqueType`](./12-julia-module/opaque-and-foreign-types/opaque-type.md)
    - [`ForeignType`](./12-julia-module/opaque-and-foreign-types/foreign-type.md)
  - [Generic functions](./12-julia-module/generic-functions/generic-functions.md)
    - [Parametric opaque types](./12-julia-module/generic-functions/parametric-opaque-types.md)
    - [Type environment](./12-julia-module/generic-functions/type-environment.md)
  - [`Type aliases`](./12-julia-module/type-aliases/type-aliases.md)
  - [Yggdrasil and jlrs](./12-julia-module/yggdrasil-and-jlrs/yggdrasil-and-jlrs.md)

# Other topics

- [Keyword arguments](./13-keyword-arguments/keyword-arguments.md)
- [Safety](./14-safety/safety.md)
- [When to leave things unrooted](./15-when-to-leave-things-unrooted/when-to-leave-things-unrooted.md)
- [Caching Julia data](./16-caching-julia-data/caching-julia-data.md)
- [Cross-language LTO](./17-cross-language-lto/cross-language-lto.md)
- [Testing applications](./18-testing-applications/testing-applications.md)
- [Testing libraries](./19-testing-libraries/testing-libraries.md)
