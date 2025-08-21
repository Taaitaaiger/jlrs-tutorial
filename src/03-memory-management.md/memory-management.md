# Targets

In the previous chapter we've seen that we can only interact with Julia inside a scope, where we can use a frame to root managed data. If we look at the signature of any method we've called with a frame, we see that these methods are generic and can take an instance of any type that implements the `Target` trait. Their return type also depends on this target type.

Take the signature of `Value::eval_string`, for example:

```rust,ignore
pub unsafe fn eval_string<'target, C, Tgt>(
    target: Tgt,
    cmd: C,
) -> ValueResult<'target, 'static, Tgt>
where
    Tgt: Target<'target>,
    C: AsRef<str>,
```

Any type that implements `Target` is called a target. There are two things a target encodes: whether the result is rooted, and what lifetime restrictions apply to it.

If we call `Value::eval_string` with `&mut frame`, `ValueResult` is `Result<Value, Value>`. `&frame` also implement `Target`, if we call `Value::eval_string` with it the result is left unrooted, and `ValueResult` is `Result<WeakValue, WeakValue>`. We say that `&mut frame` is a rooting target, and `&frame` is a weak target.

The difference between `Value` and `WeakValue` is that `Value` is guaranteed to be rooted, `WeakValue` isn't. It's unsafe to use a `WeakValue` in any meaningful way. Distinguishing between rooted and unrooted data at the type level helps avoid accidental use of unrooted data and running into use-after-free issues, which can be hard to debug. Every managed type has a `Weak` alias. We'll call `Weak` types and their instances unrooted data.

The `Result` alias is used with functions that catch exceptions, otherwise `ValueData` is used instead; `ValueResult` is defined as `Result<ValueData, ValueData>`. Every managed type has a `Result` and `Data` alias.
