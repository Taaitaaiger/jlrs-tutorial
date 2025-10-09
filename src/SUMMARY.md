# Summary

[Introduction](./00-introduction.md)

# Getting started

- [Dependencies](./01-dependencies/dependencies.md)
  - [Julia](./01-dependencies/julia.md)
  - [Rust](./01-dependencies/rust.md)
  - [C](./01-dependencies/c.md)

- [Basics](./02-basics/basics.md)
  - [Project setup](./02-basics/project-setup.md)
  - [Scopes and evaluating Julia code](./02-basics/scopes-and-evaluating-julia-code.md)
  - [Managed data and functions](./02-basics/julia-data-and-functions.md)
  - [Casting, unboxing and accessing managed data](./02-basics/casting-unboxing-and-accessing-julia-data.md)
  - [Loading packages and other custom code](./02-basics/loading-packages-and-other-custom-code.md)

# Getting familiar

- [Targets](./03-memory-management/memory-management)
  - [Using targets and nested scopes](./03-memory-management/using-targets.md)
  - [Target types](./03-memory-management/target-types.md)
    - [Local targets](./03-memory-management/local-targets.md)
    - [Dynamic targets](./03-memory-management/dynamic-targets.md)
    - [Weak targets](./03-memory-management/weak-targets.md)

- [Types and layouts](./04-types-and-layouts/types-and-layouts.md)
  - [`isbits` layouts](./04-types-and-layouts/isbits-layouts.md)
  - [Inline and non-inline layouts](./04-types-and-layouts/inline-and-non-inline-layouts.md)
  - [Union fields](./04-types-and-layouts/union-fields.md)
  - [Generics](./04-types-and-layouts/generics.md)

- [Arrays](./05-arrays/arrays.md)
  - [Creating arrays](./05-arrays/create-arrays.md)
  - [Accessing arrays](./05-arrays/access-arrays.md)
  - [Mutating arrays](./05-arrays/mutate-arrays.md)
  - [`ndarray`](./05-arrays/ndarray.md)
  - [Tracking arrays](./05-arrays/track-arrays.md)

- [Exception handling](./06-exception-handling/exception-handling.md)
  - [Parachutes](./06-exception-handling/parachutes.md)

- [Bindings and derivable traits](./07-bindings-and-derivable-traits/bindings-and-derivable-traits.md)
  - [Generating bindings](./07-bindings-and-derivable-traits/generating-bindings.md)
  - [Customizing bindings](./07-bindings-and-derivable-traits/customizing-bindings.md)

# Other runtimes

- [Multithreaded runtime](./08-multithreaded-runtime/multithreaded-runtime.md)
  - [Garbage collection, locks, and other blocking functions](./08-multithreaded-runtime/garbage-collection-locks-and-other-blocking-functions.md)

- [Async runtime](./09-async-runtime/async-runtime.md)
  - [Blocking tasks](./09-async-runtime/blocking-tasks.md)
  - [Async tasks](./09-async-runtime/async-tasks.md)
  - [Persistent tasks](./09-async-runtime/persistent-tasks.md)
  - [Combining the multithreaded and async runtimes](./09-async-runtime/combining-the-multithreaded-and-async-runtimes.md)

# Dynamic libraries

- [ccall basics](./10-ccall-basics/ccall-basics.md)
  - [Argument types](./10-ccall-basics/argument-types/argument-types.md)
    - [Arrays](./10-ccall-basics/argument-types/arrays.md)
  - [Return type](./10-ccall-basics/return-type.md)
  - [Dynamic libraries](./10-ccall-basics/dynamic-libraries.md)
  - [Custom types](./10-ccall-basics/custom-types.md)
  - [Yggdrasil](./10-ccall-basics/yggdrasil.md)

- [`julia_module!`](./11-julia-module/julia-module.md)
  - [Constants](./11-julia-module/constants/constants.md)
  - [Functions](./11-julia-module/functions/functions.md)
    - [Managed arguments](./11-julia-module/functions/managed-arguments.md)
    - [Array arguments](./11-julia-module/functions/array-arguments.md)
    - [Typed values](./11-julia-module/functions/typed-values.md)
    - [Typed layouts](./11-julia-module/functions/typed-layouts.md)
    - [Returning managed data](./11-julia-module/functions/returning-managed-data.md)
    - [`CCallRef`](./11-julia-module/functions/ccall-ref.md)
    - [Throwing exceptions](./11-julia-module/functions/throwing-exceptions.md)
    - [GC-safety](./11-julia-module/functions/gc-safety.md)
  - [Opaque and foreign types](./11-julia-module/opaque-and-foreign-types/opaque-and-foreign-types.md)
    - [`OpaqueType`](./11-julia-module/opaque-and-foreign-types/opaque-type.md)
      - [Without generics](./11-julia-module/opaque-and-foreign-types/opaque-type/without-generics.md)
      - [With generics](./11-julia-module/opaque-and-foreign-types/opaque-type/with-generics.md)
      - [With restrictions](./11-julia-module/opaque-and-foreign-types/opaque-type/with-restrictions.md)
      - [Other attributes](./11-julia-module/opaque-and-foreign-types/opaque-type/other-attributes.md)
    - [`ForeignType`](./11-julia-module/opaque-and-foreign-types/foreign-type.md)
  - [Generic functions](./11-julia-module/generic-functions/generic-functions.md)
    - [Type environment](./11-julia-module/generic-functions/type-environment.md)
  - [`Type aliases`](./11-julia-module/type-aliases/type-aliases.md)
  - [Yggdrasil and jlrs](./11-julia-module/yggdrasil-and-jlrs/yggdrasil-and-jlrs.md)

# Other topics

- [Keyword arguments](./12-keyword-arguments/keyword-arguments.md)
- [Safety](./13-safety/safety.md)
- [When to leave things unrooted](./14-when-to-leave-things-unrooted/when-to-leave-things-unrooted.md)
- [Caching Julia data](./15-caching-julia-data/caching-julia-data.md)
- [Cross-language LTO](./16-cross-language-lto/cross-language-lto.md)
- [Testing applications](./17-testing-applications/testing-applications.md)
- [Testing libraries](./18-testing-libraries/testing-libraries.md)
