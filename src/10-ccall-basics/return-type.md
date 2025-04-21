# Return type

The story for the return type is simpler: we need to limit ourselves to returning `isbits` types, if nothing is returned we can use `Cvoid` like we've seen in the array example. This is admittedly a major oversimplification, but possibilities are limited because we can't allocate new managed data.
