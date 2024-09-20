# Keyword arguments

Calling a function with custom keyword arguments involves a few small steps:

1. Create a `NamedTuple` with the custom arguments with `named_tuple!`.
2. Provide those arguments to the function we want to call with `ProvideKeyword::provide_keywords`.
3. Call the resulting `WithKeywords` instance with the positional arguments; `WithKeywords` implements `Call`.

```rust,ignore
use jlrs::prelude::*;

fn main() {
    let handle = Builder::new().start_local().expect("cannot init Julia");

    handle.local_scope::<_, 8>(|mut frame| {
        unsafe {
            let func = Value::eval_string(&mut frame, "add(a, b; c=3.0, d=4.0, e=5.0) = a + b + c + d + e")
                .expect("an exception occurred");

            let a = Value::new(&mut frame, 1.0);
            let b = Value::new(&mut frame, 2.0);
            let c = Value::new(&mut frame, 5.0);
            let d = Value::new(&mut frame, 1.0);
            let kwargs = named_tuple!(&mut frame, "c" => c, "d" => d);

            let res = func.call2(&mut frame, a, b)
                .expect("caught exception")
                .unbox::<f64>()
                .expect("not an f64");

            assert_eq!(res, 15.0);

            let func_with_kwargs = func
                .provide_keywords(kwargs)
                .expect("invalid keyword arguments");

            let res = func_with_kwargs.call2(&mut frame, a, b)
                .expect("caught exception")
                .unbox::<f64>()
                .expect("not an f64");

            assert_eq!(res, 14.0);
        };
    });
}
```
