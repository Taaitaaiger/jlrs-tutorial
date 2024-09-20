# Opaque and foreign types

In the previous section we've seen how an exported function can take and return data, which was always backed by some type that exists in Julia. In the previous chapter, when we avoided using jlrs entirely, we saw that if we wanted to expose custom types we had to hide them behind void pointers. Because we're no longer avoiding jlrs, we can create new types for our custom types and use them in the exported API.

We'll see that we can distinguish between two kinds of custom types, opaque and foreign types. Opaque types are opaque to Julia and can't reference managed data. Foreign types can reference managed data, we'll need to implement a custom mark function so the GC can find those references.
