# Non-rooting targets

We don't always need to root managed data. If we never use the result of a function, or if we can guarantee it's globally rooted, it's perfectly fine to leave it unrooted. Keeping unnecessary data alive only leads to additional GC overhead. In this case we want to use a non-rooting target.

Any target can be used as a non-rooting target by using it behind an immutable reference. There is also `Unrooted`, which can be created by calling `Target::unrooted` or `Managed::unrooted_target`. It's useful if it's not possible to use a reference to an existing target. When an unrooted target is created with the first method, it inherits the `'target` lifetime of the target, with the second it inherits the managed data's `'scope` lifetime.

There are several other non-rooting targets mentioned in the table, which are all handle types, most of which we haven't seen yet. They're relatively unimportant, they're treated as targets because they can only exist when it's safe to call into Julia, introduce a useful `'target` lifetime, and targets can create new scopes.
