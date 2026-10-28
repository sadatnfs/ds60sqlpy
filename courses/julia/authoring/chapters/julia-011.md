## A function can have several methods

Julia selects a method using the types of its positional arguments. The selection can depend on several arguments, not only a distinguished receiver object. This makes generic operations convenient when behavior depends on combinations of representations.

An abstract type can describe a category without defining storage for every subtype. Concrete subtypes supply their own fields. A generic operation such as area can then have methods for the concrete shapes while a higher-level function calls that operation without hardcoding every case.

Method specificity matters when several signatures match. A more specific applicable method can be selected, but overlapping signatures may be ambiguous when neither is more specific than the other. Defining the intersection explicitly makes the intended behavior clear. An ambiguity should not be hidden by depending on method definition order.

## Worked case A: one operation over two shapes

The shape types validate nonnegative dimensions in their constructors. Two area methods implement the appropriate formulas, and a generic total uses them through the same operation name. The code tests a heterogeneous collection and an empty collection with an explicit additive identity.

{{WORKED_A}}

## Worked case B: specify an intersection

One method handles an integer first argument and another handles an integer second argument. The pair with two integers lies in their overlap. A third, explicitly intersecting method resolves that case. A pair of unsupported argument types still produces a method error, which is more honest than an unexplained fallback value.

{{WORKED_B}}

## Interfaces and ownership

A useful interface is a set of required operations and behavioral laws, not just an abstract-type declaration. A new shape type needs an area method and suitable invariants if it is to participate in the same algorithm. Later interface work can add iteration or indexing with independent tests of those laws.

Extend functions deliberately. Defining a method for an owned type is usually easier to reason about than adding broad behavior for types owned by other packages. Uncoordinated extensions can create ambiguities or alter another package's assumptions. Keep method signatures as specific as the intended contract requires.

## Diagnose dispatch

When a call fails, inspect the actual argument types and available methods. A visually similar value can have a different type after parsing or promotion. Do not fix a method error merely by adding an unrestricted catch-all method if the input violates the intended domain.

Conversely, an unnecessarily narrow annotation can reject compatible inputs without improving correctness. The next unit uses parametric methods to express useful constraints while retaining generic numerical behavior. Correct dispatch and good performance are related but distinct questions; a heterogeneous collection may be valid while offering different specialization opportunities.

These examples demonstrate real dispatch and constructor checks on small owned types. They do not establish that every problem needs inheritance, that keyword arguments select methods in the same way as positional arguments, or that adding more methods always improves an API. Preserve the operation's meaning across every supported representation.
