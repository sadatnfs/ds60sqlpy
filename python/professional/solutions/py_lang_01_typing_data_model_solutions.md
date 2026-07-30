# Advanced typing and data-model solution reasoning

Attempt `python-lang-01` before reading
[`py_lang_01_typing_data_model_solution.py`](py_lang_01_typing_data_model_solution.py).

`Reader[T_co]` is covariant because it only produces values. A mutable
repository both consumes and produces its type, so it remains invariant.
`TypedDict` describes the shape of existing dictionaries; its literal `kind`
field lets a checker narrow a union. Overloads describe the relationship
between a literal argument and return type, while one runtime implementation
must still validate input.

`Batches` implements `__iter__` and `__next__`; `Transaction` implements the
context-manager protocol and never suppresses exceptions. `NonBlankText`
demonstrates descriptor lookup through both the class and an instance.
`ApiRecord` shows cooperative `super()` following the method resolution order
(MRO), not simply “calling the parent.”

`@runtime_checkable` verifies only that an object has named protocol members; it
does not run a static type checker or validate full signatures. TypedDict and
overloads also disappear as enforcement unless runtime code validates them.

Metaclasses can customize class creation, but they complicate inheritance and
tooling. The solution uses `__init_subclass__` for a small registry, which is
usually sufficient. Metaclasses remain appropriate for framework-level class
construction when simpler hooks cannot express the invariant.

Edge cases include exhausted iterators, zero batch sizes, exceptions inside a
transaction, corrupted descriptor storage, conflicting mixin order, and a
runtime object that has a `name` attribute of the wrong semantic type.

