from render import add, ex, SPECS

add(
    1,
    (
        "JavaScript is a language; Node and browsers are hosts that provide different APIs around it. "
        "Arithmetic, objects, functions and Promises belong to the language. Node adds process "
        "information, filesystem access and server APIs. Browsers add a document tree, events, layout and "
        "browser storage. Some APIs such as URL and fetch exist in both hosts, but that overlap does not "
        "make every program portable. A Node process has no document object to edit.\n"
        "\n"
        "This course uses ES modules with the .mjs extension for JavaScript. Modules have their own scope "
        "and run in strict mode. Imports name dependencies explicitly, and top-level await can wait for "
        "asynchronous setup. A file being syntactically valid does not mean its host dependencies exist. "
        "The first lesson makes the actual Node version, module identity and missing browser globals "
        "observable before introducing larger programs."
    ),
    (
        "An import statement loads a declared module binding. The node: prefix identifies a built-in Node "
        "module rather than an installed package. const creates a binding that cannot be reassigned, "
        "while the object it references may still be mutable. import.meta.url identifies the current ES "
        "module. typeof can inspect an undeclared host global without throwing, which is useful for "
        "distinguishing Node from a browser without pretending to implement the missing API."
    ),
    [
        ("ECMAScript", "The standardized JavaScript language semantics."),
        ("Host", "The environment supplying APIs around the language."),
        ("ES module", "A file with explicit imports/exports and its own strict scope."),
    ],
    [
        ex(
            "Inspect the actual host",
            "Check that the prepared runtime is Node 24 and that process exists.",
            "major version 24; process.release.name is node.",
            (
                "assert.equal(Number(process.versions.node.split('.')[0]), 24);\n"
                "assert.equal(process.release.name, 'node');"
            ),
            (
                "The version check verifies the actual process rather than trusting a file extension. The "
                "prepared profile is the supported baseline for later host APIs."
            ),
        ),
        ex(
            "Distinguish browser globals",
            "Inspect document and window using typeof inside Node.",
            "both undefined.",
            "assert.equal(typeof document, 'undefined');\nassert.equal(typeof window, 'undefined');",
            (
                "A browser DOM lesson cannot be validated by a Node run that never had a document. Later browser "
                "chapters use separate real HTML fixtures."
            ),
        ),
        ex(
            "Use language arithmetic independently of host APIs",
            "Calculate 2+3 and compare the numeric result with a string.",
            "number 5; not strictly equal to string 5.",
            "const total = 2 + 3;\nassert.equal(total, 5);\nassert.notEqual(total, '5');",
            (
                "The arithmetic belongs to the language. The strict assertion distinguishes the numeric value "
                "from a textual representation."
            ),
        ),
        ex(
            "Inspect module identity",
            "Read import.meta.url and confirm it identifies the current module.",
            "a file URL ending in .mjs in the classroom.",
            (
                "assert.equal(new URL(import.meta.url).protocol, 'file:');\n"
                "assert.ok(import.meta.url.endsWith('.mjs'));"
            ),
            (
                "Module identity is useful for resolving local resources without assuming the current working "
                "directory. It is not a network download request."
            ),
        ),
        ex(
            "Observe strict module function calls",
            "Call an ordinary function without a receiver and inspect this.",
            "this is undefined.",
            "function receiver() { return this; }\nassert.equal(receiver(), undefined);",
            (
                "ES modules use strict semantics. The callsite determines this for an ordinary function; it is "
                "not automatically the global object."
            ),
        ),
        ex(
            "Await a real Promise result",
            "Resolve 7 through a Promise and await it before checking.",
            "observed value 7 after await.",
            (
                "const pending = Promise.resolve(7);\n"
                "assert.ok(pending instanceof Promise);\n"
                "const value = await pending;\n"
                "assert.equal(value, 7);"
            ),
            (
                "A Promise is a handle for eventual completion. Checking the handle is different from checking "
                "the resolved value after the asynchronous boundary."
            ),
        ),
    ],
    helper="",
    imports="import { strict as assert } from 'node:assert';",
    source="https://nodejs.org/docs/latest-v24.x/api/esm.html",
    notes="",
)

add(
    2,
    (
        "JavaScript values have runtime types, and operators can perform implicit conversion. The plus "
        "operator adds numbers but concatenates when string conversion applies. Strict equality avoids "
        "the broad coercion of loose equality, but it still has specific semantics for NaN and signed "
        "zero. Object.is provides another comparison contract. Choose the relation required by the domain "
        "rather than assuming one operator means every notion of same.\n"
        "\n"
        "Numbers use binary floating-point arithmetic and have a finite safe-integer range. Exact decimal "
        "fractions such as 0.1 are generally approximate. BigInt represents arbitrary-size integers but "
        "cannot be mixed with Number arithmetic without an explicit conversion policy. null and undefined "
        "are distinct values commonly used for absence; neither should be silently converted to a domain "
        "count. Validate external numeric text before calculation instead of relying on a convenient "
        "coercion."
    ),
    (
        "typeof reports primitive categories but typeof null is the historical string object. "
        "Number.isNaN tests NaN without coercing its argument. Number.isFinite rejects non-number values "
        "and infinities. Object.is distinguishes +0 and -0 while treating NaN as equal to itself. BigInt "
        "literals end in n. JSON does not serialize BigInt by default, so an explicit wire-format policy "
        "is needed."
    ),
    [
        ("Coercion", "An implicit conversion performed by an operator or API."),
        (
            "Strict equality",
            "A comparison that does not broadly convert different primitive types.",
        ),
        ("Safe integer", "An integer exactly distinguishable within the Number representation."),
        ("BigInt", "An arbitrary-size integer type with separate arithmetic rules."),
    ],
    [
        ex(
            "Trace plus versus numeric conversion",
            "Compare 2+3, 2+string 3, and Number(string 3)+2.",
            "5, string 23, and 5.",
            "assert.equal(2 + 3, 5);\nassert.equal(2 + '3', '23');\nassert.equal(Number('3') + 2, 5);",
            (
                "The same symbol has different behavior when a string participates. Explicit conversion makes the "
                "intended numeric operation visible."
            ),
        ),
        ex(
            "Inspect absence and NaN",
            "Compare typeof null, undefined and Number.isNaN results.",
            "null reports object; undefined reports undefined; only numeric NaN passes isNaN.",
            (
                "assert.equal(typeof null, 'object');\n"
                "assert.equal(typeof undefined, 'undefined');\n"
                "assert.equal(Number.isNaN(NaN), true);\n"
                "assert.equal(Number.isNaN('not a number'), false);"
            ),
            (
                "The typeof null result is a language legacy, not evidence that null has usable object "
                "properties. Number.isNaN avoids converting arbitrary text."
            ),
        ),
        ex(
            "Compare equality contracts",
            "Use NaN, +0 and -0 with strict equality and Object.is.",
            "NaN!==NaN; Object.is(NaN, NaN) is true; +0===-0; Object.is distinguishes zeros.",
            (
                "assert.equal(NaN === NaN, false);\n"
                "assert.equal(Object.is(NaN, NaN), true);\n"
                "assert.equal(0 === -0, true);\n"
                "assert.equal(Object.is(0, -0), false);"
            ),
            (
                "Different APIs use different equality relations. A collection key policy may differ from "
                "Object.is, which is examined in the Map/Set lesson."
            ),
        ),
        ex(
            "Expose floating-point approximation",
            "Add 0.1 and 0.2 and compare with 0.3 under an explicit tolerance.",
            "strict equality false; absolute error below 1e-15.",
            "const value = 0.1 + 0.2;\nassert.notEqual(value, 0.3);\nassert.ok(Math.abs(value - 0.3) < 1e-15);",
            (
                "A tolerance is appropriate only when the domain permits approximate arithmetic. Currency or "
                "identity calculations may require integer units or another representation."
            ),
        ),
        ex(
            "Protect integer identity",
            "Compare the two integers just beyond Number.MAX_SAFE_INTEGER and then use BigInt.",
            "Number collapses a difference; BigInt preserves it.",
            (
                "const max = Number.MAX_SAFE_INTEGER;\n"
                "assert.equal(max + 1, max + 2);\n"
                "const exact = BigInt(max);\n"
                "assert.notEqual(exact + 1n, exact + 2n);"
            ),
            (
                "Losing a unit difference is unacceptable for an identifier or counter requiring exactness. "
                "Converting after rounding cannot recover the original integer."
            ),
        ),
        ex(
            "Reject ambiguous numeric input",
            "Validate finite nonblank numeric text and reject blank, Infinity and mixed BigInt arithmetic.",
            "valid 12 accepted; invalid cases throw.",
            (
                "assert.equal(parseFinite('12'), 12);\n"
                "assert.throws(() => parseFinite(' '), TypeError);\n"
                "assert.throws(() => parseFinite('Infinity'), TypeError);\n"
                "assert.throws(() => 1n + 1, TypeError);"
            ),
            (
                "The parser states its accepted text domain instead of accepting every Number coercion. BigInt "
                "and Number mixing needs an explicit precision policy."
            ),
        ),
    ],
    helper=(
        "function parseFinite(text) {\n"
        "  if (typeof text !== 'string' || text.trim() === '') throw new TypeError('nonblank numeric text "
        "required');\n"
        "  const value = Number(text);\n"
        "  if (!Number.isFinite(value)) throw new TypeError('finite number required');\n"
        "  return value;\n"
        "}"
    ),
    imports="import { strict as assert } from 'node:assert';",
    source="https://tc39.es/ecma262/multipage/abstract-operations.html",
    notes="",
)

add(
    3,
    (
        "Control flow decides which expressions execute and how many times. JavaScript conditions use "
        "truthiness, so false, 0, empty string, null, undefined and NaN act differently from empty arrays "
        "and objects, which are truthy. Short-circuit operators can return an operand rather than a "
        "Boolean. The nullish-coalescing operator provides a fallback only for null or undefined, which "
        "is often different from treating zero or empty text as missing.\n"
        "\n"
        "Loops need an initial state, an invariant and a termination condition. A prefix sum invariant "
        "says the accumulator equals the sum of elements already visited. Half-open index bounds align "
        "with zero-based arrays. Boundary tests on empty and single-element inputs expose off-by-one "
        "errors more clearly than a large happy-path example. A loop that mutates its own collection also "
        "needs an explicit policy about which elements are visited."
    ),
    (
        "Use if for a branch, for...of for values, and indexed for when positions matter. The expression "
        "left&&right evaluates right only when left is truthy; left||right uses right only when left is "
        "falsy. Neither necessarily returns a Boolean. The expression value??fallback preserves 0, false "
        "and empty string. A loop condition i<array.length excludes the invalid index length."
    ),
    [
        ("Truthiness", "The Boolean interpretation used by conditions."),
        ("Short circuit", "Skipping an operand after the result can be determined."),
        ("Loop invariant", "A property preserved as each iteration advances."),
        ("Nullish fallback", "A fallback applied only to null or undefined."),
    ],
    [
        ex(
            "Compare false and truthy containers",
            "Inspect Boolean conversions of 0, empty string, empty array and empty object.",
            "false, false, true, true.",
            "assert.deepEqual([Boolean(0), Boolean(''), Boolean([]), Boolean({})], [false, false, true, true]);",
            (
                "An empty collection is still an object. Testing if(array) does not establish that it contains "
                "any elements."
            ),
        ),
        ex(
            "Preserve a valid zero with nullish fallback",
            "Compare 0||10 with 0??10, and null??10.",
            "10, 0, 10.",
            "assert.equal(0 || 10, 10);\nassert.equal(0 ?? 10, 0);\nassert.equal(null ?? 10, 10);",
            (
                "The operators encode different absence policies. A valid zero count should not silently become a "
                "default because it is falsy."
            ),
        ),
        ex(
            "Trace a prefix sum",
            "Sum 2, 4, 6 and record the accumulator after each iteration.",
            "prefixes 2, 6, 12.",
            (
                "let sum = 0;\n"
                "const prefixes = [];\n"
                "for (const value of [2, 4, 6]) { sum += value; prefixes.push(sum); }\n"
                "assert.deepEqual(prefixes, [2, 6, 12]);"
            ),
            (
                "Each element contributes exactly once. The recorded states make the invariant inspectable rather "
                "than only checking a final total."
            ),
        ),
        ex(
            "Handle an empty collection",
            "Run the same accumulation pattern on an empty array.",
            "sum 0 and iterations 0.",
            (
                "let sum = 0;\n"
                "let iterations = 0;\n"
                "for (const value of []) { sum += value; iterations += 1; }\n"
                "assert.equal(sum, 0);\n"
                "assert.equal(iterations, 0);"
            ),
            "The additive identity already represents the empty result. No fabricated element is needed.",
        ),
        ex(
            "Stop at the first match",
            "Find the first 8 in 3, 8, 8 using an indexed loop and break.",
            "index 1.",
            (
                "const values = [3, 8, 8];\n"
                "let found = -1;\n"
                "for (let index = 0; index < values.length; index += 1) {\n"
                "  if (values[index] === 8) { found = index; break; }\n"
                "}\n"
                "assert.equal(found, 1);"
            ),
            (
                "Without break, a later match could overwrite the first index. The sentinel -1 distinguishes "
                "absence from index 0."
            ),
        ),
        ex(
            "Make a wrong boundary observable",
            "Iterate with index<=length over a one-element array and record the values.",
            "extra undefined element exposes the off-by-one.",
            (
                "const values = [7];\n"
                "const observed = [];\n"
                "for (let index = 0; index <= values.length; index += 1) observed.push(values[index]);\n"
                "assert.deepEqual(observed, [7, undefined]);"
            ),
            (
                "JavaScript array out-of-range reads return undefined rather than throwing by default. A loop bug "
                "can therefore travel into later arithmetic as NaN unless the contract is checked."
            ),
        ),
    ],
    helper="",
    imports="import { strict as assert } from 'node:assert';",
    source="https://tc39.es/ecma262/multipage/ecmascript-language-statements-and-declarations.html",
    notes="",
)

add(
    4,
    (
        "Functions define reusable computations, and lexical scope determines which bindings a function "
        "can read. A closure retains access to bindings from the environment where it was created. Those "
        "bindings can hold state across calls, which is useful for a small counter or factory. Closures "
        "do not automatically copy every captured value. A shared var binding in a loop can make several "
        "functions observe the same final value, while let creates the intended per-iteration bindings.\n"
        "\n"
        "Default parameters apply when an argument is undefined, not when it is null. Ordinary function "
        "this depends on the callsite; arrow functions capture this lexically. A clear function contract "
        "should distinguish arguments, returned values, mutable captured state and receiver dependence. "
        "Prefer explicit parameters when a closure would hide important dependencies."
    ),
    (
        "A function declaration introduces a named callable; an arrow expression creates a function "
        "value. Returning a nested function forms a closure over its surrounding bindings. let and const "
        "are block-scoped, while var is function-scoped. The default syntax name=value is evaluated when "
        "the argument is undefined. Use call or bind only when receiver behavior is part of the contract, "
        "not as a substitute for understanding the callsite."
    ),
    [
        ("Lexical scope", "Binding lookup determined by where code is written."),
        ("Closure", "A function retaining access to its surrounding bindings."),
        ("Default parameter", "A fallback used when the supplied argument is undefined."),
        ("Receiver", "The this value used by an ordinary method call."),
    ],
    [
        ex(
            "Call a pure function",
            "Use add with 2, 3 and with negative 1, 1.",
            "5 and 0.",
            (
                "function add(left, right) { return left + right; }\n"
                "assert.equal(add(2, 3), 5);\n"
                "assert.equal(add(-1, 1), 0);"
            ),
            (
                "The function depends only on its arguments and changes no external state. Boundary examples can "
                "be tested independently."
            ),
        ),
        ex(
            "Build independent closures",
            "Create two counters; increment the first twice and the second once.",
            "first 1, 2; second 1.",
            (
                "const first = counter();\n"
                "const second = counter();\n"
                "assert.equal(first(), 1);\n"
                "assert.equal(first(), 2);\n"
                "assert.equal(second(), 1);"
            ),
            (
                "Each factory call creates a separate captured binding. Equal initial values do not imply shared "
                "counter state."
            ),
        ),
        ex(
            "Compare let and var loop capture",
            "Create three closures in a let loop and three in a var loop.",
            "let returns 0, 1, 2; var returns 3, 3, 3.",
            (
                "const block = [];\n"
                "for (let index = 0; index < 3; index += 1) block.push(() => index);\n"
                "const shared = [];\n"
                "for (var index = 0; index < 3; index += 1) shared.push(() => index);\n"
                "assert.deepEqual(block.map(fn => fn()), [0, 1, 2]);\n"
                "assert.deepEqual(shared.map(fn => fn()), [3, 3, 3]);"
            ),
            (
                "The difference is binding lifetime, not the time the function body was parsed. All var closures "
                "share one function-scoped index."
            ),
        ),
        ex(
            "Distinguish undefined from null defaults",
            "Call a greeting function with no argument, undefined and null.",
            "default used for the first two; null preserved.",
            (
                "function label(value = 'guest') { return value; }\n"
                "assert.equal(label(), 'guest');\n"
                "assert.equal(label(undefined), 'guest');\n"
                "assert.equal(label(null), null);"
            ),
            (
                "A default parameter does not define a general missing-value policy. If null is invalid, the "
                "function must validate it explicitly."
            ),
        ),
        ex(
            "Observe an ordinary receiver",
            "Call a method through its object and then with an explicit alternate receiver.",
            "4 and 9.",
            (
                "const item = { value: 4, read() { return this.value; } };\n"
                "assert.equal(item.read(), 4);\n"
                "assert.equal(item.read.call({ value: 9 }), 9);"
            ),
            (
                "The same function can operate on different receivers. Detaching it and calling without a "
                "receiver may produce an error rather than retain the original object."
            ),
        ),
        ex(
            "Reject an invalid factory configuration",
            "Create a step counter with nonpositive or noninteger step.",
            "TypeError for 0 and 1.5; step 2 yields 2, 4.",
            (
                "assert.throws(() => counter(0), TypeError);\n"
                "assert.throws(() => counter(1.5), TypeError);\n"
                "const next = counter(2);\n"
                "assert.deepEqual([next(), next()], [2, 4]);"
            ),
            (
                "Validate the configuration when the closure is created so every later call can rely on its "
                "invariant. Hidden invalid state is harder to diagnose after many calls."
            ),
        ),
    ],
    helper=(
        "function counter(step = 1) {\n"
        "  if (!Number.isInteger(step) || step <= 0) throw new TypeError('positive integer step "
        "required');\n"
        "  let value = 0;\n"
        "  return () => { value += step; return value; };\n"
        "}"
    ),
    imports="import { strict as assert } from 'node:assert';",
    source="https://tc39.es/ecma262/multipage/ecmascript-language-functions-and-classes.html",
    notes="",
)

add(
    5,
    (
        "Array operations differ in whether they mutate the container, return a new container or reuse "
        "referenced objects. map transforms values, filter selects them, and reduce combines them under "
        "an explicit accumulator contract. A new array does not necessarily contain new objects: shallow "
        "copies preserve nested references. sort mutates its array and uses string ordering by default, "
        "which can misorder numbers. toSorted returns a sorted copy in the prepared Node 24 runtime.\n"
        "\n"
        "An immutable transformation means preserving the prior value needed by the application, not "
        "merely using const. const prevents rebinding the variable but does not freeze its array. Choose "
        "mutation or copying based on ownership and history requirements. Test both returned results and "
        "the original input when preservation is part of the contract."
    ),
    (
        "map receives value, index and array; avoid passing a callback that unintentionally interprets "
        "the extra arguments. filter keeps elements whose predicate is truthy. reduce needs an identity "
        "for an empty input unless absence is handled separately. Use (a, b)=>a-b for numeric ordering. "
        "Spread or slice copies the outer array only; copy nested records deliberately when they will be "
        "edited."
    ),
    [
        ("Transformation", "A rule producing new values from existing elements."),
        ("Reduction", "Combining elements into one accumulator result."),
        ("Shallow copy", "A new container retaining references to nested objects."),
        ("Mutation", "Changing the state of an existing object."),
    ],
    [
        ex(
            "Map and filter without changing input",
            "Double 1, 2, 3, 4 and keep results above 4.",
            "6, 8; original array unchanged.",
            (
                "const original = [1, 2, 3, 4];\n"
                "const result = original.map(value => value * 2).filter(value => value > 4);\n"
                "assert.deepEqual(result, [6, 8]);\n"
                "assert.deepEqual(original, [1, 2, 3, 4]);"
            ),
            (
                "The pipeline returns new arrays while retaining the original numeric fixture. Object-valued "
                "elements would need an additional ownership analysis."
            ),
        ),
        ex(
            "Supply a reduction identity",
            "Sum an empty array and 1, 2, 3 using initial 0.",
            "0 and 6.",
            (
                "assert.equal([].reduce((sum, value) => sum + value, 0), 0);\n"
                "assert.equal([1, 2, 3].reduce((sum, value) => sum + value, 0), 6);"
            ),
            (
                "The identity defines the empty case. Omitting it would make an empty array throw and change the "
                "callback's initial state."
            ),
        ),
        ex(
            "Expose default sort coercion",
            "Sort 10, 2, 1 with default and numeric comparators.",
            "default 1, 10, 2; numeric 1, 2, 10.",
            (
                "assert.deepEqual([10, 2, 1].sort(), [1, 10, 2]);\n"
                "assert.deepEqual([10, 2, 1].sort((a, b) => a - b), [1, 2, 10]);"
            ),
            (
                "Default sort compares string representations. A valid array of numbers does not automatically "
                "select numeric order."
            ),
        ),
        ex(
            "Preserve an array while sorting",
            "Use toSorted on 3, 1, 2 and inspect both arrays.",
            "sorted 1, 2, 3; original 3, 1, 2.",
            (
                "const original = [3, 1, 2];\n"
                "const sorted = original.toSorted((a, b) => a - b);\n"
                "assert.deepEqual(sorted, [1, 2, 3]);\n"
                "assert.deepEqual(original, [3, 1, 2]);"
            ),
            (
                "The prepared Node 24 runtime supplies toSorted. The contract is copying rather than mutating; "
                "this distinction matters when another component retains the old array."
            ),
        ),
        ex(
            "Expose a shallow copy alias",
            "Spread an array containing one object and mutate that object through the copy.",
            "original nested value also changes.",
            (
                "const original = [{ value: 1 }];\n"
                "const copy = [...original];\n"
                "copy[0].value = 9;\n"
                "assert.equal(original[0].value, 9);\n"
                "assert.notEqual(copy, original);"
            ),
            (
                "The containers differ but their first elements share identity. A shallow copy cannot preserve "
                "historical nested state by itself."
            ),
        ),
        ex(
            "Copy records for a specific edit",
            "Map records to new objects before changing one field.",
            "edited record changes; original record stays 1.",
            (
                "const original = [{ value: 1 }];\n"
                "const copy = original.map(row => ({ ...row }));\n"
                "copy[0].value = 9;\n"
                "assert.equal(original[0].value, 1);\n"
                "assert.equal(copy[0].value, 9);"
            ),
            (
                "This copy is sufficient for the fixture's flat record. Deeper mutable fields would need their "
                "own policy rather than a claim that spread is a universal deep clone."
            ),
        ),
    ],
    helper="",
    imports="import { strict as assert } from 'node:assert';",
    source="https://tc39.es/ecma262/multipage/indexed-collections.html",
    notes="",
)

add(
    6,
    (
        "Objects associate property keys with values and can inherit properties through a prototype "
        "chain. An own property belongs directly to the object; an inherited property may be found "
        "through lookup even when it is absent from the object's own keys. Object.hasOwn checks this "
        "distinction without relying on a method that an input object could override. A plain object is "
        "useful for records, but Map or a null-prototype dictionary can be clearer for arbitrary external "
        "keys.\n"
        "\n"
        "Destructuring reads properties into bindings, and spread copies enumerable own properties into a "
        "new object. Neither automatically deep-copies nested state or validates a schema. Getters can "
        "execute code during property access, so an object-shaped value is not always passive data. This "
        "lesson uses literal records and controlled prototypes to make lookup, ownership and copying "
        "visible."
    ),
    (
        "Object.create(proto) sets a chosen prototype. The in operator checks inherited as well as own "
        "properties, while Object.hasOwn checks only own membership. Object.keys enumerates own "
        "enumerable string keys. Destructuring defaults apply to undefined values. Object.freeze prevents "
        "direct property changes on that object but does not recursively freeze nested objects."
    ),
    [
        ("Own property", "A property stored directly on an object."),
        ("Prototype chain", "The linked objects consulted during inherited property lookup."),
        ("Destructuring", "Binding selected properties from a value."),
        (
            "Shallow freeze",
            "Preventing direct changes without recursively freezing referenced objects.",
        ),
    ],
    [
        ex(
            "Distinguish own and inherited properties",
            "Create a child inheriting kind and owning name.",
            "kind found by in but not hasOwn; name is own.",
            (
                "const parent = { kind: 'record' };\n"
                "const child = Object.create(parent);\n"
                "child.name = 'sample';\n"
                "assert.equal('kind' in child, true);\n"
                "assert.equal(Object.hasOwn(child, 'kind'), false);\n"
                "assert.equal(Object.hasOwn(child, 'name'), true);"
            ),
            (
                "Property lookup and record schema inspection answer different questions. Accepting inherited "
                "fields as request data can violate a boundary contract."
            ),
        ),
        ex(
            "Copy only own enumerable fields",
            "Spread the child into a plain record and inspect keys.",
            "only name copied.",
            (
                "const child = Object.create({ kind: 'record' });\n"
                "child.name = 'sample';\n"
                "const copy = { ...child };\n"
                "assert.deepEqual(Object.keys(copy), ['name']);\n"
                "assert.equal(copy.kind, undefined);"
            ),
            (
                "Spread does not reproduce the prototype chain. It copies the declared enumerable own surface, "
                "which still may contain mutable nested references."
            ),
        ),
        ex(
            "Use destructuring defaults carefully",
            "Read missing count and explicit null count with default 0.",
            "missing becomes 0; null remains null.",
            (
                "const { count: absent = 0 } = {};\n"
                "const { count: explicit = 0 } = { count: null };\n"
                "assert.equal(absent, 0);\n"
                "assert.equal(explicit, null);"
            ),
            (
                "The default applies to undefined, not every absence-like value. Validation remains necessary "
                "when null is not permitted."
            ),
        ),
        ex(
            "Use a null-prototype dictionary for arbitrary keys",
            "Store __proto__ as data in Object.create(null).",
            "own value preserved; prototype remains null.",
            (
                "const dictionary = Object.create(null);\n"
                "dictionary['__proto__'] = 'literal data';\n"
                "assert.equal(dictionary['__proto__'], 'literal data');\n"
                "assert.equal(Object.getPrototypeOf(dictionary), null);\n"
                "assert.equal(Object.hasOwn(dictionary, '__proto__'), true);"
            ),
            (
                "The fixture treats the key as data without changing a global prototype. A Map is another "
                "explicit choice for arbitrary key-value storage."
            ),
        ),
        ex(
            "Expose shallow freeze",
            "Freeze an outer object and mutate its nested record.",
            "outer reassignment throws; inner value can change.",
            (
                "const value = Object.freeze({ nested: { count: 1 } });\n"
                "assert.throws(() => { value.nested = {}; }, TypeError);\n"
                "value.nested.count = 2;\n"
                "assert.equal(value.nested.count, 2);"
            ),
            (
                "Freezing the container does not recursively freeze reachable objects. The mutation demonstrates "
                "the actual boundary rather than a misleading immutable label."
            ),
        ),
        ex(
            "Observe a getter side effect",
            "Read a controlled getter twice and count calls.",
            "values 1 then 2; getter executed twice.",
            (
                "let calls = 0;\n"
                "const value = { get next() { calls += 1; return calls; } };\n"
                "assert.equal(value.next, 1);\n"
                "assert.equal(value.next, 2);\n"
                "assert.equal(calls, 2);"
            ),
            (
                "Property access can execute behavior. A schema validator handling untrusted objects should not "
                "assume every property read is a passive field lookup."
            ),
        ),
    ],
    helper="",
    imports="import { strict as assert } from 'node:assert';",
    source="https://tc39.es/ecma262/multipage/ordinary-and-exotic-objects-behaviours.html",
    notes="",
)

add(
    7,
    (
        "Map and Set provide collection contracts different from plain object records. Map can use "
        "objects as keys without converting them to string. Object keys are compared by identity, so two "
        "separately created objects with same fields remain distinct keys. Set removes repeated values "
        "under SameValueZero equality, which treats NaN as equal to itself and +0/-0 as the same key. "
        "Iteration follows insertion order, but insertion order is not a semantic numeric or business "
        "sort unless the application defines it that way.\n"
        "\n"
        "Choosing a collection determines which information is retained. A Set loses multiplicity; a Map "
        "keeps one current value per key. Use a frequency Map when repeated events matter. Avoid checking "
        "a lookup result for truthiness when zero, false or undefined can be legitimate stored values; "
        "has distinguishes key presence from the value returned by get."
    ),
    (
        "Map.set inserts or replaces a key, value pair; get returns the value or undefined; has checks "
        "membership. Map.size counts keys. Set.add returns the set itself, while has reports membership. "
        "Iterating map entries yields [key, value] pairs in insertion order. Updating an existing key "
        "does not move it to the end; deleting and reinserting does."
    ),
    [
        ("Reference identity", "Sameness of the actual object rather than its field contents."),
        (
            "SameValueZero",
            "The Map/Set primitive equality rule including NaN equality and merged signed zeros.",
        ),
        ("Multiplicity", "How many times a value appears in the input."),
        ("Membership", "Whether a key or value is present, independent of its stored value."),
    ],
    [
        ex(
            "Keep equal-looking object keys distinct",
            "Create two {id: 1} objects and use them as Map keys.",
            "size 2 and separate values.",
            (
                "const first = { id: 1 };\n"
                "const second = { id: 1 };\n"
                "const map = new Map([[first, 'a'], [second, 'b']]);\n"
                "assert.equal(map.size, 2);\n"
                "assert.equal(map.get(first), 'a');\n"
                "assert.equal(map.get(second), 'b');"
            ),
            (
                "Field equality does not establish object identity. A domain needing value-based keys should "
                "choose a stable canonical identifier explicitly."
            ),
        ),
        ex(
            "Inspect Set equality",
            "Insert NaN twice, +0 and -0.",
            "size 2: one NaN and one zero.",
            (
                "const values = new Set([NaN, NaN, 0, -0]);\n"
                "assert.equal(values.size, 2);\n"
                "assert.equal(values.has(NaN), true);\n"
                "assert.equal(values.has(-0), true);"
            ),
            (
                "The collection equality contract differs from strict NaN comparison and Object.is signed zero "
                "behavior. Know the actual relation used by the container."
            ),
        ),
        ex(
            "Count repeated events",
            "Build a frequency Map for red, blue, red.",
            "red 2, blue 1.",
            (
                "const counts = new Map();\n"
                "for (const value of ['red', 'blue', 'red']) counts.set(value, (counts.get(value) ?? 0) + 1);\n"
                "assert.deepEqual([...counts], [['red', 2], ['blue', 1]]);"
            ),
            (
                "A Set would retain only membership and lose the two red observations. The accumulator uses an "
                "explicit zero for an absent count."
            ),
        ),
        ex(
            "Distinguish a stored zero from absence",
            "Store key a with 0 and compare has/get for a and b.",
            "a present with 0; b absent with undefined.",
            (
                "const map = new Map([['a', 0]]);\n"
                "assert.equal(map.has('a'), true);\n"
                "assert.equal(map.get('a'), 0);\n"
                "assert.equal(map.has('b'), false);\n"
                "assert.equal(map.get('b'), undefined);"
            ),
            "Truthiness would misclassify the valid zero as missing. Presence and value are separate questions.",
        ),
        ex(
            "Trace insertion order updates",
            "Insert a, b, update a, then delete and reinsert a.",
            "update order a, b; reinsertion order b, a.",
            (
                "const map = new Map([['a', 1], ['b', 2]]);\n"
                "map.set('a', 3);\n"
                "assert.deepEqual([...map.keys()], ['a', 'b']);\n"
                "map.delete('a'); map.set('a', 4);\n"
                "assert.deepEqual([...map.keys()], ['b', 'a']);"
            ),
            (
                "The order reflects insertion history. If a report requires sorted keys, sort them rather than "
                "depending on this history accidentally."
            ),
        ),
        ex(
            "Deduplicate while preserving first occurrence",
            "Use Set over b, a, b, c, a and compare the ordered unique values.",
            "b, a, c.",
            (
                "const unique = [...new Set(['b', 'a', 'b', 'c', 'a'])];\n"
                "assert.deepEqual(unique, ['b', 'a', 'c']);"
            ),
            (
                "This operation intentionally loses repeat counts while preserving first appearance order. State "
                "that contract before using it in a data pipeline."
            ),
        ),
    ],
    helper="",
    imports="import { strict as assert } from 'node:assert';",
    source="https://tc39.es/ecma262/multipage/keyed-collections.html",
    notes="",
)

add(
    8,
    (
        "JavaScript strings are sequences of UTF-16 code units. length and indexing count those units, "
        "which do not always correspond to complete Unicode codepoints. A supplementary emoji occupies a "
        "surrogate pair, and a visible letter can combine several codepoints. Iteration with for...of or "
        "spread uses codepoints, while grapheme segmentation requires an additional text policy. "
        "Normalization can map canonically equivalent spellings to one representation, but should not be "
        "applied silently to every identifier or secret.\n"
        "\n"
        "Regular expressions are programs over text, not literal string containers. User text containing "
        "dots, brackets or quantifiers can change a pattern if inserted without escaping. The prepared "
        "Node 24 runtime supports RegExp.escape for literal pattern construction. Bound pattern and input "
        "size when regex work is exposed externally; not every complex pattern has predictable linear "
        "cost."
    ),
    (
        "Use codePointAt and string iteration to inspect codepoints. normalize('NFC') applies a declared "
        "canonical normalization. The u flag enables Unicode-aware regex semantics for codepoints, but "
        "does not turn codepoints into grapheme clusters. RegExp.escape converts a literal string into a "
        "safe pattern fragment. A global regex carries lastIndex state across calls, so reuse requires "
        "understanding or resetting that cursor."
    ),
    [
        ("UTF-16 code unit", "The storage/indexing unit used by JavaScript String."),
        ("Code point", "A Unicode identity represented by one or two code units."),
        ("Normalization", "A declared mapping between equivalent Unicode sequences."),
        ("Pattern escaping", "Treating input text as literal characters rather than regex syntax."),
    ],
    [
        ex(
            "Count code units and codepoints",
            "Inspect A followed by one emoji.",
            "length 3; spread count 2.",
            (
                "const text = 'A🙂';\n"
                "assert.equal(text.length, 3);\n"
                "assert.equal([...text].length, 2);\n"
                "assert.equal(text.codePointAt(1), 0x1f642);"
            ),
            (
                "The emoji uses two code units. Taking a one-unit substring from its middle would not produce a "
                "complete codepoint."
            ),
        ),
        ex(
            "Compare canonical spellings",
            "Compare composed é with e plus combining acute before and after NFC.",
            "raw strings differ; normalized strings equal.",
            (
                "const composed = 'é';\n"
                "const decomposed = 'é';\n"
                "assert.notEqual(composed, decomposed);\n"
                "assert.equal(decomposed.normalize('NFC'), composed);"
            ),
            (
                "Canonical normalization changes representation identity under an explicit policy. It does not "
                "solve every homoglyph or language-specific comparison problem."
            ),
        ),
        ex(
            "Match a literal regex fragment",
            "Escape a.b+ and match it exactly rather than interpreting dot and plus.",
            "literal accepted; axbb rejected.",
            (
                "const literal = 'a.b+';\n"
                "const pattern = new RegExp(`^${RegExp.escape(literal)}$`, 'u');\n"
                "assert.equal(pattern.test('a.b+'), true);\n"
                "assert.equal(pattern.test('axbb'), false);"
            ),
            (
                "The escaped fragment preserves the user text as data. Concatenating raw text into a regex would "
                "change the accepted language."
            ),
        ),
        ex(
            "Observe global regex cursor state",
            "Call /a/g repeatedly on aa and inspect lastIndex.",
            "matches at 0 then 1; third call false resets cursor 0.",
            (
                "const pattern = /a/g;\n"
                "assert.equal(pattern.test('aa'), true); assert.equal(pattern.lastIndex, 1);\n"
                "assert.equal(pattern.test('aa'), true); assert.equal(pattern.lastIndex, 2);\n"
                "assert.equal(pattern.test('aa'), false); assert.equal(pattern.lastIndex, 0);"
            ),
            (
                "The same pattern object is stateful when global or sticky. Reusing it as a pure predicate can "
                "produce surprising alternating results."
            ),
        ),
        ex(
            "Use Unicode-aware dot matching",
            "Compare /^.$/ and /^.$/u on one emoji.",
            "without u false; with u true.",
            "assert.equal(/^.$/.test('🙂'), false);\nassert.equal(/^.$/u.test('🙂'), true);",
            (
                "The u flag changes codepoint handling. It does not guarantee one user-perceived character for "
                "every combining sequence."
            ),
        ),
        ex(
            "Bound a text-validation input",
            "Reject a string longer than 20 code units before applying an anchored ASCII identifier pattern.",
            "item_1 accepted; oversized input rejected.",
            (
                "assert.equal(identifier('item_1'), 'item_1');\n"
                "assert.throws(() => identifier('a'.repeat(21)), TypeError);\n"
                "assert.throws(() => identifier('two words'), TypeError);"
            ),
            (
                "The bound and grammar are explicit. An application needing international identifiers would "
                "require a different policy rather than quietly widening this one."
            ),
        ),
    ],
    helper=(
        "function identifier(value) {\n"
        "  if (typeof value !== 'string' || value.length > 20 || "
        "!/^[A-Za-z_][A-Za-z0-9_]*$/u.test(value)) throw new TypeError('bounded ASCII identifier "
        "required');\n"
        "  return value;\n"
        "}"
    ),
    imports="import { strict as assert } from 'node:assert';",
    source="https://tc39.es/ecma262/multipage/text-processing.html",
    notes=(
        "## Version-specific API\n"
        "\n"
        "`RegExp.escape` is part of the prepared Node 24 baseline. An older host Node installation may "
        "lack it; that is a runtime-version mismatch, not a reason to replace escaping with raw pattern "
        "concatenation. The classroom reference must be checked in the prepared profile. Unicode "
        "codepoint counts are distinct from grapheme cluster counts.\n"
    ),
)

add(
    9,
    (
        "Errors should distinguish an invalid request from an expected missing result and an operational "
        "failure. JavaScript can throw any value, but throwing Error objects preserves a useful message, "
        "stack and cause chain. Validation belongs at an external boundary before state changes or "
        "resource work. A catch that returns a plausible default for every failure can turn corrupted "
        "input into misleading success.\n"
        "\n"
        "This lesson parses a bounded order record with an identifier, positive quantity and integer-cent "
        "price. JSON syntax validity is only the first gate; the parsed value can still be null, an "
        "array, missing fields or semantically invalid. The validator returns a fresh accepted record and "
        "leaves the input untouched. A domain calculation checks integer overflow with "
        "Number.isSafeInteger. Error translation adds context while preserving the original cause."
    ),
    (
        "Use try/catch around the operation whose failure you intend to handle. Check object shape, own "
        "keys, primitive types and value bounds explicitly. Number.isInteger and Number.isSafeInteger "
        "express different numeric contracts. Throw TypeError for a schema/type violation and RangeError "
        "for an out-of-range numeric value under this fixture. Error options can retain cause when "
        "translating an operational failure."
    ),
    [
        ("Validation boundary", "The point where untrusted values are checked before use."),
        ("Error cause", "The original failure retained when adding higher-level context."),
        ("Domain invariant", "A rule every accepted record must satisfy."),
        ("Failure category", "A named distinction guiding diagnosis or recovery."),
    ],
    [
        ex(
            "Accept a valid order",
            "Validate id A, quantity 2, price 125 and calculate integer cents.",
            "total 250; fresh accepted object.",
            (
                "const raw = { id: 'A', quantity: 2, priceCents: 125 };\n"
                "const order = validateOrder(raw);\n"
                "assert.equal(total(order), 250);\n"
                "assert.notEqual(order, raw);"
            ),
            (
                "The accepted record is a copy with a known schema. It does not expose a reference that an "
                "external caller can later edit to invalidate the already checked value."
            ),
        ),
        ex(
            "Reject syntactically valid but wrong-shaped JSON",
            "Parse null, an array and an object with an extra field, then validate.",
            "TypeError for each shape violation.",
            (
                'for (const text of [\'null\', \'[]\', \'{"id":"A","quantity":1,"priceCents":2,"extra":true}\']) '
                "{\n"
                "  assert.throws(() => validateOrder(JSON.parse(text)), TypeError);\n"
                "}"
            ),
            (
                "JSON.parse proves only syntax. It does not know the domain fields or reject a valid JSON value "
                "of the wrong kind."
            ),
        ),
        ex(
            "Reject invalid numeric domain values",
            "Try quantity 0, quantity 1.5 and negative price.",
            "RangeError for each.",
            (
                "for (const raw of [{ id: 'A', quantity: 0, priceCents: 2 }, { id: 'A', quantity: 1.5, "
                "priceCents: 2 }, { id: 'A', quantity: 1, priceCents: -1 }]) {\n"
                "  assert.throws(() => validateOrder(raw), RangeError);\n"
                "}"
            ),
            (
                "A numeric runtime type does not establish a positive integer or nonnegative cent amount. The "
                "validator makes those domain rules explicit."
            ),
        ),
        ex(
            "Prevent unsafe integer multiplication",
            "Use a valid safe unit price with quantity 2 whose product exceeds the safe integer range.",
            "RangeError from total.",
            (
                "const order = validateOrder({ id: 'A', quantity: 2, priceCents: Number.MAX_SAFE_INTEGER });\n"
                "assert.throws(() => total(order), RangeError);"
            ),
            (
                "Inputs can each be valid while their combination exceeds the output representation. Validate the "
                "computed result as well as individual fields."
            ),
        ),
        ex(
            "Preserve a translated cause",
            "Wrap a SyntaxError with a contextual Error using cause.",
            "cause identity retained.",
            (
                "const original = new SyntaxError('invalid fixture JSON');\n"
                "const contextual = new Error('Cannot read order fixture', { cause: original });\n"
                "assert.equal(contextual.cause, original);\n"
                "assert.match(contextual.message, /order fixture/u);"
            ),
            (
                "The added context should not erase the underlying failure type or stack. Callers can inspect the "
                "cause when deciding whether recovery is appropriate."
            ),
        ),
        ex(
            "Prove rejected input caused no mutation",
            "Validate a bad quantity and compare the original object after failure.",
            "input unchanged.",
            (
                "const raw = { id: 'A', quantity: -1, priceCents: 5 };\n"
                "const before = structuredClone(raw);\n"
                "assert.throws(() => validateOrder(raw), RangeError);\n"
                "assert.deepEqual(raw, before);"
            ),
            (
                "Validation should not partially repair or mutate untrusted input before throwing unless that "
                "behavior is explicitly part of the API. A pure boundary is easier to audit."
            ),
        ),
    ],
    helper=(
        "function validateOrder(value) {\n"
        "  if (value === null || typeof value !== 'object' || Array.isArray(value)) throw new "
        "TypeError('order object required');\n"
        "  const keys = Object.keys(value).sort();\n"
        "  if (keys.join(',') !== 'id,priceCents,quantity' || typeof value.id !== 'string' || value.id "
        "=== '') throw new TypeError('exact order schema required');\n"
        "  if (!Number.isSafeInteger(value.quantity) || value.quantity <= 0 || "
        "!Number.isSafeInteger(value.priceCents) || value.priceCents < 0) throw new RangeError('valid "
        "integer quantity and cents required');\n"
        "  return { id: value.id, quantity: value.quantity, priceCents: value.priceCents };\n"
        "}\n"
        "function total(order) {\n"
        "  const result = order.quantity * order.priceCents;\n"
        "  if (!Number.isSafeInteger(result)) throw new RangeError('total exceeds safe integer range');\n"
        "  return result;\n"
        "}"
    ),
    imports="import { strict as assert } from 'node:assert';",
    source="https://nodejs.org/docs/latest-v24.x/api/errors.html",
    notes="",
)
