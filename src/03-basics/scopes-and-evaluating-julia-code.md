# Scopes and evaluating Julia code

There are three steps our application needs to take to evaluate

```julia
println("Hello world!")
```

1. Configure and start the Julia runtime.
2. Create a scope.
3. Evaluate the code inside the scope.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 1>(|mut frame| {
        // Safety: we only evaluate a print statement, which is perfectly safe.
        unsafe {
            Value::eval_string(&mut frame, "println(\"Hello, world!\")")
        }.expect("an exception occurred");
    });
}
```

Let's go through this code step-by-step.

```rust,ignore
let handle = Builder::new().start_local().expect("cannot init Julia");
```

This line initializes Julia and returns a `LocalHandle` to the runtime. The `Builder` lets us configure the runtime, options include setting the number of threads Julia can use and using a custom system image. When the runtime is started, the JlrsCore.jl package is loaded automatically.[^1]

The handle lets us call into Julia from the current thread, the runtime shuts down when it's dropped. Julia can only be initialized once per process, and can't be reinitialized after it has shut down.

```rust,ignore
handle.local_scope::<_, 1>(|mut frame| { /*snip*/ });
```

Before we can call into Julia we have to create a scope by calling `LocalHandle::local_scope` first. This method takes a constant generic integer and a closure that provides access to a frame. The frame is used to prevent data that is managed by Julia's garbage collector, or GC, from being freed while we're using it from Rust. This is called rooting. We'll call such data managed data.

An important question to ask is: when can the GC be triggered? The rough answer is whenever managed data is allocated. If the GC is triggered from some thread, it will wait until all threads that can call into Julia have reached a safepoint. Because we're only using a single thread, there are no other threads that need to reach a safepoint and the GC can run immediately, we'll leave it at that for now.

Functions provided by jlrs that return managed data are typically called with a mutable reference to a frame.[^2] These functions can only be called inside a scope, and their result is rooted in the frame. As long as managed data is rooted, it, and any other managed data it refers to, will not be freed by the GC. Every time data is rooted in a frame one of its slots is consumed, the number of slots is expressed by the constant generic integer. It's unfortunate, but its value can't be inferred. We need to count how many slots we use.

```rust,ignore
|mut frame| {
    // Safety: we only call print with a string, which is perfectly safe.
    unsafe { Value::eval_string(&mut frame, "println(\"Hello, world!\")") }
        .expect("an exception occurred");
}
```

Inside the closure we call `Value::eval_string`, which lets us evaluate arbitrary Julia code. It takes a mutable reference to our frame and a string to evaluate, and returns the result as a `Value` rooted in this frame.[^3] A `Value` is managed data of an arbitrary type.[^4] It's unsafe to call this function because it lets us evaluate arbitrary Julia code, including silly and obviously unsound things like `unsafe_load(Ptr{UInt}(C_NULL))`.

A nice property of scopes is that they naturally introduce a lifetime. Instances of `Value` and other managed types make use of this lifetime to ensure they can't outlive their scope. If we tried to remove the semicolon after `expect` our code would fail to compile because the result doesn't live long enough.

[^1]: If JlrsCore hasn't been installed, it will be installed by default. We can customize this with `Builder::install_jlrs_core`. Successfully loading JlrsCore is required to use jlrs.

[^2]: There are other types that can be used instead of mutable references to frames, collectively these types are called targets. We'll cover targets in the next chapter.

[^3]: The actual argument and return types are a bit more involved. Like footnote 2, this will be covered in the next chapter.

[^4]: In this particular case `nothing` is returned, whose type is `Nothing`. If we had evaluated `1 + 2` instead, the `Value` would have contained an `Int`.
