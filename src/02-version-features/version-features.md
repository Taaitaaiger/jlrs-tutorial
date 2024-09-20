# Version features

If we add jlrs as a dependency and try to compile our crate, we'll see that this fails even after following the instructions in the previous chapter. The reason is that there's an issue we need to deal with: the Julia C API is not stable and each new version tends to introduce a few minor, but backwards-incompatible, changes. jlrs strives to handle these incompatibilities internally as much as possible, but this requires enabling a feature to select the targeted version of Julia.

Features that select the targeted version of Julia are called version features. They are admittedly kind of a hack because version features are not additive; we must enable exactly one, and it must match the version of Julia that is used. If multiple version features, no version features, or an incorrect version feature is used, compilation will fail.

The following version features currently exist:

- `julia-1-6`
- `julia-1-7`
- `julia-1-8`
- `julia-1-9`
- `julia-1-10`
- `julia-1-11`

It's recommended to "reexport" these version features, and enable the correct one at compile time.

```toml
[features]
julia-1-6 = ["jlrs/julia-1-6"]
julia-1-7 = ["jlrs/julia-1-7"]
# etc...
```
