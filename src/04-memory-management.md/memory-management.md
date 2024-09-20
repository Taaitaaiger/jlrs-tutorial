# Targets

In the previous chapter we've seen that we can only interact with Julia inside a scope, where we can use a frame to root managed data. If we look at the signature of any method we've called with a frame, we see that these methods are generic and can take an instance of any type that implements the `Target` trait. Their return type also depends on this target type.

Take the signature of `Call::call0`, for example:

```rust,ignore
unsafe fn call0<'target, Tgt>(self, target: Tgt) -> ValueResult<'target, 'data, Tgt>
    where
        Tgt: Target<'target>;
```

Any type that implements `Target` is called a target. There are two things a target encodes: whether the result is rooted, and what lifetime restrictions apply to it.

If we call `call0` with `&mut frame`, `ValueResult` is `Result<Value, Value>`. `&frame` also implement `Target`, if we call `call0` with it the result is left unrooted, and `ValueResult` is `Result<ValueRef, ValueRef>`. We say that `&mut frame` is a rooting target, and `&frame` is a non-rooting target.

The difference between `Value` and `ValueRef` is that `Value` is guaranteed to be rooted, `ValueRef` isn't. It's unsafe to use a `ValueRef` in any meaningful way. Distinguishing between rooted and unrooted data at the type level helps avoid accidental use of unrooted data and running into use-after-free issues, which can be hard to debug. Every managed type has a `Ref` alias, we'll call instances of these types unrooted references [to managed data].

The `Result` alias is used with functions that catch exceptions, otherwise `ValueData` is used instead; `ValueResult` is defined as `Result<ValueData, ValueData>`. Every managed type has a `Result` and `Data` alias.
