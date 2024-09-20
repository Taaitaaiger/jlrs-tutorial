# Target types

No target types have been named yet, even frames have only been called just that without elaborating what their exact type is. The following table lists all target types, which lifetime is used for `'target`, and whether it's a rooting target or not.

| Type                                | Rooting |
| ----------------------------------- | ------- |
| `LocalGcFrame<'target>`             | Yes     |
| `&mut LocalGcFrame<'target>`        | Yes     |
| `UnsizedLocalGcFrame<'target>`      | Yes     |
| `&mut UnsizedLocalGcFrame<'target>` | Yes     |
| `LocalOutput<'target>`              | Yes     |
| `&'target mut LocalOutput`          | Yes     |
| `LocalReusableSlot<'target>`        | Yes     |
| `&mut LocalReusableSlot<'target>`   | Yes[^1] |
| `GcFrame<'target>`                  | Yes     |
| `&mut GcFrame<'target>`             | Yes     |
| `Output<'target>`                   | Yes     |
| `&'target mut Output`               | Yes     |
| `ReusableSlot<'target>`             | Yes     |
| `&mut ReusableSlot<'target>`        | Yes[^1] |
| `AsyncGcFrame<'target>`             | Yes     |
| `&mut AsyncGcFrame<'target>`        | Yes     |
| `Unrooted`                          | No      |
| `StackHandle<'target>`              | No      |
| `Pin<&'target mut WeakHandle>`      | No      |
| `ActiveHandle<'target>`             | No      |
| `&Tgt where Tgt: Target<'target>`   | No      |

These targets belong to three different groups: local targets, dynamic targets, and non-rooting targets.

[^1]: While a mutable reference to a `(Local)ReusableSlot` roots the data, it assigns the scope's lifetime to the result which allows the result to live until we leave the scope. This slot can be reused, though, so the data is not guaranteed to remain rooted for the entire `'target` lifetime. For this reason an unrooted reference is returned.
