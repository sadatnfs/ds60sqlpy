from render import add, ex
TS = 'https://www.typescriptlang.org/docs/handbook/2/'

add(19,
'''TypeScript adds a static checker to JavaScript. The checker reasons about possible values and operations before execution; the emitted program still follows JavaScript semantics. A type annotation does not create a runtime validator, convert a string to a number, or freeze an object. This distinction is essential when data comes from JSON, files, network responses or another program.

Inference lets the checker learn types from initial values and expressions. An explicit annotation is useful at a public boundary or when the intended set of values is broader than the initial expression. Repeating every obvious inferred type adds noise without necessarily improving the contract. Strict checking includes checks such as strictNullChecks and noImplicitAny, but it does not enable every possible compiler option. In particular, this profile does not silently claim exactOptionalPropertyTypes or noUncheckedIndexedAccess.

The prepared route compiles main.mts with TypeScript 5.9.3 using NodeNext resolution and noEmitOnError, then runs the resulting ES module on Node 24. An incorrect typed program is a compiler failure before runtime. Each deliberate negative type example is placed in an uncalled function with @ts-expect-error. The directive requires the next line to produce a compiler diagnostic; if that error disappears, the compiler reports an unused directive. These functions are teaching checks, not code paths to execute or broad permission to suppress errors.''',
'''A parameter annotation follows its name, and a return annotation follows the parameter list. const often preserves a literal primitive type, whereas let permits later assignment and commonly widens to the primitive category. A type alias names a compile-time description. unknown requires checking before use; any bypasses many checks and should not become the default for external input. The as syntax asserts what the author wants the checker to assume and performs no conversion.''',
[('Static type','A compile-time description of values and supported operations.'),('Inference','Deriving a type from code without an explicit annotation.'),('Erasure','Removal of type-only syntax from the emitted JavaScript.'),('Unknown boundary','An external value requiring runtime inspection before trusted use.')],[
ex('Annotate a numeric function','Define a function accepting two numbers and returning their sum; inspect its runtime value.','sum 5 with runtime typeof number.',r'''function add(left: number, right: number): number { return left + right; }
const result = add(2, 3);
assert.equal(result, 5);
assert.equal(typeof result, 'number');
function negativeTypeCheck(): void {
  // @ts-expect-error A string is not a numeric argument.
  add('2', 3);
}
void negativeTypeCheck;''','The annotation describes accepted calls to checked TypeScript code. It is erased during compilation; the emitted function still performs JavaScript addition and would need validation at an untyped boundary.'),
ex('Show that an assertion does not convert data','Assert that an unknown string is a number, then inspect the actual runtime type.','the runtime value remains the string wrong.',r'''const external: unknown = 'wrong';
const claimed = external as number;
assert.equal(typeof claimed, 'string');
assert.equal(String(claimed), 'wrong');''','This intentionally unsafe assertion demonstrates the escape hatch. The correct repair for external data is a runtime check or parser, not a stronger-looking cast.'),
ex('Compare literal preservation and widening','Use const for a fixed tag and let for a changing text value.','fixed tag remains ready; mutable text can change to done.',r'''const fixed = 'ready';
let mutable = 'ready';
mutable = 'done';
function acceptReady(value: 'ready'): string { return value; }
assert.equal(acceptReady(fixed), 'ready');
assert.equal(mutable, 'done');
function negativeTypeCheck(): void {
  // @ts-expect-error mutable is string, not the literal type ready.
  acceptReady(mutable);
}
void negativeTypeCheck;''','A literal type can describe one exact protocol tag. A mutable binding must allow its intended future values; inference therefore often widens it to string.'),
ex('Handle null explicitly under strict checking','Write a length function accepting string or null.','length 3 for abc and 0 for null.',r'''function lengthOrZero(value: string | null): number {
  return value === null ? 0 : value.length;
}
assert.equal(lengthOrZero('abc'), 3);
assert.equal(lengthOrZero(null), 0);
function negativeTypeCheck(value: string | null): void {
  // @ts-expect-error value may be null before a guard.
  void value.length;
}
void negativeTypeCheck;''','The null branch establishes a runtime fact that the checker can use. A non-null assertion would silence the diagnostic without adding this behavior.'),
ex('Observe type erasure through object keys','Declare a record type and create a compatible object.','runtime keys contain only id and count, with no type alias metadata.',r'''type Item = { id: string; count: number };
const item: Item = { id: 'A', count: 2 };
assert.deepEqual(Object.keys(item), ['id', 'count']);
assert.equal('Item' in item, false);''','A type alias is not a constructor or a runtime schema. Code that needs a schema must represent and execute validation separately.'),
ex('Narrow unknown before numeric use','Accept only a finite number from an unknown value.','12 doubles to 24; string 12 and Infinity reject.',r'''function doubleFinite(value: unknown): number {
  if (typeof value !== 'number' || !Number.isFinite(value)) throw new TypeError('finite number required');
  return value * 2;
}
assert.equal(doubleFinite(12), 24);
assert.throws(() => doubleFinite('12'), TypeError);
assert.throws(() => doubleFinite(Infinity), TypeError);''','The typeof branch narrows the static type, while the finite check enforces an additional domain property that ordinary number typing does not guarantee.')],source=TS+'everyday-types.html')

add(20,
'''A union type describes a value that may belong to one of several alternatives. Until code proves which alternative is present, only operations valid for all alternatives are safe. Narrowing uses control flow to refine that set. typeof checks, equality checks, property checks and explicit discriminants can provide evidence. Truthiness is sometimes too coarse: an empty string is still a valid string even though it is falsy.

A discriminated union uses a shared property with distinct literal values, such as kind: success or kind: failure. Each alternative can then carry exactly the fields appropriate to that state. This is more precise than one object with several optional fields, which may admit impossible combinations such as success with no value. A switch over the discriminant connects runtime branching to static knowledge of the payload.

Exhaustiveness means accounting for every alternative. A function accepting never can mark a branch that should be unreachable after complete narrowing. Adding a new union member then creates a compile error at that branch until the handler is updated. This protects checked internal code. A JSON payload still needs validation: a type assertion can inject a value that violates the union and reaches the supposedly impossible branch at runtime.''',
'''Use a union operator between alternatives, then compare a literal discriminant with switch or equality. Within each branch, the checker exposes only that variant's fields. assertNever throws in the runtime fallback while requiring a never argument statically. User-defined type predicates can guide narrowing, but TypeScript trusts their declared claim; an incorrect predicate can make unsafe code compile. Prefer simple guards whose runtime checks actually establish the claimed property.''',
[('Union','A value belonging to one of several alternatives.'),('Narrowing','Refining a type using control-flow evidence.'),('Discriminant','A shared field whose literal value identifies a variant.'),('Exhaustiveness','Handling every possible alternative in a closed union.')],[
ex('Handle a result union','Format both successful value 7 and a failure message.','value:7 and error:offline.',r'''assert.equal(formatResult({ kind: 'success', value: 7 }), 'value:7');
assert.equal(formatResult({ kind: 'failure', message: 'offline' }), 'error:offline');''','The kind check determines which payload exists. A failure result cannot accidentally be read as if it contained the success value.'),
ex('Preserve an empty string during narrowing','Handle string or undefined using an explicit undefined comparison.','empty string has length 0; absent value returns missing.',r'''function describe(value: string | undefined): number | 'missing' {
  return value === undefined ? 'missing' : value.length;
}
assert.equal(describe(''), 0);
assert.equal(describe(undefined), 'missing');''','if(value) would merge the empty-string case with absence. A guard should encode the domain distinction, not merely satisfy the checker.'),
ex('Reject access to another variant payload','Demonstrate that a failure branch cannot read value.','expected compiler error on value; valid failure formatting remains unchanged.',r'''function negativeTypeCheck(result: Result): void {
  if (result.kind === 'failure') {
    // @ts-expect-error failure has message, not value.
    void result.value;
  }
}
void negativeTypeCheck;
assert.equal(formatResult({ kind: 'failure', message: 'bad' }), 'error:bad');''','The type prevents a concrete impossible-state mistake. It is stronger than optional fields that would allow reading undefined and hoping the caller checks it later.'),
ex('Catch an unhandled new variant at compile time','Add a pending variant and intentionally omit it from a switch in an uncalled function.','expected compiler error at assertNever for pending.',r'''type Extended = Result | { kind: 'pending'; attempt: number };
function negativeTypeCheck(result: Extended): string {
  switch (result.kind) {
    case 'success': return String(result.value);
    case 'failure': return result.message;
    default:
      // @ts-expect-error pending remains possible here.
      return assertNever(result);
  }
}
void negativeTypeCheck;
assert.equal(formatResult({ kind: 'success', value: 0 }), 'value:0');''','The missing handler becomes a compiler obligation when the union grows. The error is evidence that the exhaustiveness guard is connected to the actual type.'),
ex('Use an honest unknown-value predicate','Check for a record with a finite numeric value before consuming it.','valid record accepted; null, arrays and string-valued records rejected.',r'''function hasFiniteValue(value: unknown): value is { value: number } {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
    && 'value' in value && typeof value.value === 'number' && Number.isFinite(value.value);
}
assert.equal(hasFiniteValue({ value: 2 }), true);
for (const value of [null, [], { value: '2' }, { value: NaN }]) assert.equal(hasFiniteValue(value), false);''','The predicate inspects every property it claims. A declaration of value is SomeType is not automatically verified against the function body by the compiler.'),
ex('Expose the runtime limit of an asserted union','Force a malformed external value into Result for demonstration and call the handler.','runtime fallback throws rather than fabricating success.',r'''const malformed: unknown = { kind: 'unexpected' };
assert.throws(() => formatResult(malformed as Result), /unhandled variant/u);''','The intentionally unsafe assertion shows why exhaustiveness does not validate external data. The runtime fallback preserves diagnosis, but a real input boundary should reject the malformed value earlier.')],helper='''type Result = { kind: 'success'; value: number } | { kind: 'failure'; message: string };
function assertNever(value: never): never {
  throw new Error('unhandled variant: ' + JSON.stringify(value));
}
function formatResult(result: Result): string {
  switch (result.kind) {
    case 'success': return `value:${result.value}`;
    case 'failure': return `error:${result.message}`;
    default: return assertNever(result);
  }
}''',source=TS+'narrowing.html')

add(21,
'''TypeScript object types describe the properties an operation requires. Compatibility is largely structural: an object with the required fields can be accepted even if it was not created by a named class. A fresh object literal receives additional excess-property checking, which catches likely misspellings, but assigning the same wider object through a variable can be allowed. Neither rule is a runtime exact-schema validator.

readonly restricts writes through a particular typed view. It does not freeze the runtime object, and another mutable alias may still change it. A shallow readonly property containing a mutable object also leaves that nested object mutable unless its type says otherwise. Readonly arrays prevent mutating methods through their interface, but ordinary copy and transformation operations remain available.

An optional property may be absent. Under this route's strict profile, reading it produces a value that may be undefined. The profile does not enable exactOptionalPropertyTypes, so explicit undefined assignment has different checking behavior from a stricter configuration that distinguishes absence from an explicitly present undefined. Be precise about the actual compiler flags and the wire-format policy. JSON serialization can omit undefined fields, further separating runtime presence from serialized presence.''',
'''Use property?: Type for optional fields and readonly property: Type for a restricted view. Readonly<T> is shallow: it changes the write permissions of the immediate fields in the type, not the underlying objects. readonly T[] or ReadonlyArray<T> disallows push through that reference. Object.freeze is a runtime operation with its own shallow boundary. Object.hasOwn can distinguish property presence independently of its value.''',
[('Structural compatibility','Acceptance based on required members rather than a declared class identity.'),('Excess-property checking','Extra scrutiny of fresh object literals for unexpected properties.'),('Readonly view','A type-level restriction on writes through a particular reference.'),('Optional property','A field that may be absent and must be handled accordingly.')],[
ex('Use structural compatibility','Pass a wider named object with id and count to a function requiring only id.','label A; original count remains 2.',r'''function label(value: { id: string }): string { return value.id; }
const wider = { id: 'A', count: 2 };
assert.equal(label(wider), 'A');
assert.equal(wider.count, 2);
function negativeTypeCheck(): void {
  // @ts-expect-error A fresh literal is checked for excess properties.
  label({ id: 'A', count: 2 });
}
void negativeTypeCheck;''','Structural acceptance is useful for small interfaces, but does not strip extra fields. Treating an accepted type as an exact serialization schema can leak fields that still exist at runtime.'),
ex('Observe mutation through an alias','Create a readonly view of a mutable record, then mutate the original reference.','readonly view observes count changing from 1 to 4.',r'''const mutable = { count: 1 };
const view: Readonly<{ count: number }> = mutable;
mutable.count = 4;
assert.equal(view.count, 4);
function negativeTypeCheck(): void {
  // @ts-expect-error Writes through the readonly view are forbidden.
  view.count = 9;
}
void negativeTypeCheck;''','The view and original reference point to the same object. Readonly is a static access restriction, not a historical snapshot or deep immutability guarantee.'),
ex('Handle absent and zero-valued optional counts','Use a nullish fallback on an optional count.','absent becomes 10; explicit 0 remains 0.',r'''type Options = { count?: number };
function count(options: Options): number { return options.count ?? 10; }
assert.equal(count({}), 10);
assert.equal(count({ count: 0 }), 0);''','The optional field forces the caller to account for undefined. Nullish fallback preserves a valid zero, unlike a truthiness fallback.'),
ex('Distinguish runtime presence from undefined','Compare an absent property with an explicitly present undefined property.','hasOwn is false versus true; JSON serializes both as empty objects.',r'''const absent: { count?: number } = {};
const present: { count?: number } = { count: undefined };
assert.equal(Object.hasOwn(absent, 'count'), false);
assert.equal(Object.hasOwn(present, 'count'), true);
assert.equal(JSON.stringify(absent), '{}');
assert.equal(JSON.stringify(present), '{}');''','This code matches the actual compiler profile without exactOptionalPropertyTypes. Serialization can erase a runtime distinction, so patch/update APIs must define whether absence and explicit removal differ.'),
ex('Show shallow readonly and shallow freeze boundaries','Freeze an outer record containing a nested mutable object and update the nested count.','nested count becomes 3; outer object is frozen.',r'''const record = Object.freeze({ nested: { count: 1 } });
record.nested.count = 3;
assert.equal(record.nested.count, 3);
assert.equal(Object.isFrozen(record), true);
assert.equal(Object.isFrozen(record.nested), false);''','Both the inferred readonly property and runtime freeze protect the outer reference. Neither automatically traverses the nested object graph.'),
ex('Transform a readonly array without mutation','Accept readonly numbers, return a doubled array, and demonstrate push is rejected statically.','new array 2,4; input remains 1,2.',r'''const values: readonly number[] = [1, 2];
const doubled = values.map(value => value * 2);
assert.deepEqual(doubled, [2, 4]);
assert.deepEqual(values, [1, 2]);
function negativeTypeCheck(): void {
  // @ts-expect-error A readonly array has no mutable push operation.
  values.push(3);
}
void negativeTypeCheck;''','A read-only consumer can compute a new value without requiring mutation rights. This often makes a function easier to reuse with both mutable and readonly callers.')],source=TS+'objects.html')

add(22,
'''Generics express a relationship between types across a reusable operation. An identity function returning any loses information about the relationship between input and output. A generic identity function returns the same type T supplied by its caller. The parameter is not a runtime argument or a request to create a new specialized JavaScript function for every type; it is a compile-time relation checked against one implementation.

A constraint gives the implementation only the operations known to exist. T extends {length: number} permits reading length, but does not permit replacing the input with an arbitrary object containing length and claiming it is still the caller's exact T. The caller may have supplied an array, a string or a richer record with additional invariants.

keyof and indexed access types connect property keys to property result types. A generic getProperty<T,K extends keyof T> returns T[K], preserving whether the chosen field is a string or a number. This is useful when the relationship is real. Overly elaborate generics can make an API harder to understand; prefer a concrete parameter type when only one domain shape is needed. Generics cannot validate unknown JSON or prove that an external service honored a claimed schema.''',
'''Declare type parameters in angle brackets on the function. T names a caller-selected type; extends constrains its allowed structure. K extends keyof T restricts a key to known properties, and T[K] gives the corresponding value type. A generic function returning the first element should expose T | undefined for an empty input even when the project's indexed-access checking is less strict. Runtime control flow must implement the same absence policy.''',
[('Type parameter','A placeholder describing a relationship selected at a call site.'),('Constraint','The minimum structure a generic implementation may rely on.'),('Keyof','A type operator producing the known keys of a type.'),('Indexed access type','A type expression selecting the type associated with a key.')],[
ex('Preserve identity type and object identity','Pass a number and an object through identity.','number remains 7; object is the same reference.',r'''const value: number = identity(7);
const record = { id: 'A' };
assert.equal(value, 7);
assert.equal(identity(record), record);
function negativeTypeCheck(): void {
  // @ts-expect-error identity preserves number rather than inventing string.
  const text: string = identity(7);
  void text;
}
void negativeTypeCheck;''','The generic relationship preserves static information without copying data. Runtime identity is still a separate observation checked by the assertion.'),
ex('Connect a key to its exact result type','Read id and count from one record with getProperty.','id is string A; count is number 2.',r'''const row = { id: 'A', count: 2 };
const id: string = getProperty(row, 'id');
const count: number = getProperty(row, 'count');
assert.equal(id, 'A');
assert.equal(count, 2);
function negativeTypeCheck(): void {
  // @ts-expect-error missing is not a key of this record.
  getProperty(row, 'missing');
}
void negativeTypeCheck;''','Returning a broad string|number union would lose the connection between the selected key and its payload. T[K] preserves that correlation.'),
ex('Expose absence in a generic first function','Read the first item from a nonempty and an empty readonly array.','4 and undefined.',r'''assert.equal(first([4, 5]), 4);
assert.equal(first<number>([]), undefined);
function negativeTypeCheck(): void {
  // @ts-expect-error The function promises possible absence.
  const definite: number = first<number>([]);
  void definite;
}
void negativeTypeCheck;''','The signature deliberately includes undefined. Depending on an unchecked array access that happens to compile would misrepresent the empty-input behavior.'),
ex('Use only the constrained length property','Apply a length operation to a string and an array; reject a number at compile time.','lengths 3 and 2.',r'''assert.equal(measuredLength('abc'), 3);
assert.equal(measuredLength([1, 2]), 2);
function negativeTypeCheck(): void {
  // @ts-expect-error number has no required length property.
  measuredLength(7);
}
void negativeTypeCheck;''','A constraint permits one shared capability across otherwise different types. It does not assert that the values have the same domain meaning or interchangeable methods.'),
ex('Transform while preserving output element type','Map numbers to labels through a generic map function.','string array item:2,item:4; input unchanged.',r'''const values = [2, 4];
const labels: string[] = mapValues(values, value => `item:${value}`);
assert.deepEqual(labels, ['item:2', 'item:4']);
assert.deepEqual(values, [2, 4]);''','Two type parameters represent the input element and output element. The callback supplies the actual transformation, and the resulting array type follows it.'),
ex('Avoid pretending a constraint is the exact caller type','Show that a replacement object cannot be returned as arbitrary T even if it meets the constraint.','expected compile error for returning a fabricated length-only object.',r'''function negativeTypeCheck<T extends { length: number }>(value: T): T {
  void value;
  // @ts-expect-error T may require additional fields or a more specific shape.
  return { length: 0 };
}
void negativeTypeCheck;
assert.equal(measuredLength({ length: 5, id: 'A' }), 5);''','A constraint is a lower bound on required capabilities, not the full identity of every allowed type. Fabricating a minimal object could discard fields the caller was promised.')],helper='''function identity<T>(value: T): T { return value; }
function getProperty<T, K extends keyof T>(value: T, key: K): T[K] { return value[key]; }
function first<T>(values: readonly T[]): T | undefined { return values.length === 0 ? undefined : values[0]; }
function measuredLength<T extends { length: number }>(value: T): number { return value.length; }
function mapValues<T, U>(values: readonly T[], convert: (value: T) => U): U[] { return values.map(convert); }''',source=TS+'generics.html')

add(23,
'''Type operators can derive one static description from another, reducing duplicated declarations that drift apart. A mapped type iterates over a type's property keys, changing their value types or modifiers. Pick selects known fields, Omit excludes them, Partial makes immediate properties optional, and Readonly restricts immediate writes. These operators change the checker-visible shape, not the runtime object. Assigning a wider record to Omit<SecretRecord, 'secret'> does not remove the secret bytes.

Conditional types select a result type based on an assignability relation. When the checked side is a naked type parameter, applying the conditional to a union distributes across its members. Wrapping both sides in tuples changes the test to treat the union as a whole. This matters when a utility unexpectedly returns a union of arrays rather than one array whose elements may have several types.

infer introduces a type variable extracted from a matched shape, such as the element type of an array. Built-in utilities such as ReturnType and Awaited express common relations. They do not inspect runtime values, execute a function, wait for a Promise or validate an endpoint response. Use type-level transformations to model real API relationships; keep runtime selection, validation and serialization explicit.''',
'''A mapped type uses [K in keyof T] to visit each property key. A modifier such as readonly or an optional question mark affects the generated property declaration. A conditional T extends U ? X : Y chooses a static result; infer names a matched component. The satisfies operator checks compatibility while retaining the expression's more specific inferred shape. It can catch missing or extra literal keys without replacing the runtime object or adding validation code.''',
[('Mapped type','A type constructed by transforming a set of property keys.'),('Conditional type','A type-level branch based on assignability.'),('Distributivity','Applying a conditional independently to members of a union.'),('Type derivation','Describing one API shape in terms of another without runtime transformation.')],[
ex('Map a record into field flags','Create a boolean flag type from id and count fields.','id true and count false; a missing flag is a compile error.',r'''type Row = { id: string; count: number };
type Flags<T> = { [K in keyof T]: boolean };
const flags: Flags<Row> = { id: true, count: false };
assert.deepEqual(flags, { id: true, count: false });
function negativeTypeCheck(): void {
  // @ts-expect-error Every Row key must have a flag.
  const incomplete: Flags<Row> = { id: true };
  void incomplete;
}
void negativeTypeCheck;''','The mapped type follows the source keys, so adding a field to Row creates a new required flag. The actual object still needs to be constructed by ordinary code.'),
ex('Prove Omit does not remove runtime secrets','Assign a wider record to an Omit type, then compare with an explicit public projection.','typed view still has secret at runtime; explicit projection does not.',r'''type RecordWithSecret = { id: string; secret: string };
const full: RecordWithSecret = { id: 'A', secret: 'fixture-only' };
const view: Omit<RecordWithSecret, 'secret'> = full;
assert.equal(Object.hasOwn(view, 'secret'), true);
const publicRecord: Pick<RecordWithSecret, 'id'> = { id: full.id };
assert.equal(Object.hasOwn(publicRecord, 'secret'), false);
assert.equal(JSON.stringify(publicRecord), '{"id":"A"}');''','Type erasure makes this a concrete data-exposure risk. The public object must be constructed with an explicit field allowlist before serialization.'),
ex('Compare distributed and whole-union array types','Define both conditional utilities and demonstrate their different assignment behavior.','whole-union array accepts mixed values; distributed array rejects them.',r'''type Distributed<T> = T extends unknown ? T[] : never;
type Whole<T> = [T] extends [unknown] ? T[] : never;
const mixed: Whole<string | number> = ['A', 2];
assert.deepEqual(mixed, ['A', 2]);
function negativeTypeCheck(): void {
  // @ts-expect-error Distributed<string|number> is string[] | number[].
  const invalid: Distributed<string | number> = ['A', 2];
  void invalid;
}
void negativeTypeCheck;''','The tuple wrapper prevents the naked parameter from distributing. The difference is between choosing one homogeneous array alternative and allowing a union at each element position.'),
ex('Infer an array element type','Extract the element type of a readonly array and use it in a checked value.','element type permits number 7 and rejects text.',r'''type ElementOf<T> = T extends readonly (infer Item)[] ? Item : never;
const value: ElementOf<readonly number[]> = 7;
assert.equal(value, 7);
function negativeTypeCheck(): void {
  // @ts-expect-error The extracted element type is number.
  const invalid: ElementOf<readonly number[]> = 'seven';
  void invalid;
}
void negativeTypeCheck;''','infer binds the matched component in the true branch. A non-array type would produce never under this utility, making unsupported use explicit.'),
ex('Derive an asynchronous result type without executing it','Use ReturnType and Awaited for a small async function, then actually call it separately.','declared resolved shape and actual result both have count 3.',r'''async function load(): Promise<{ count: number }> { return { count: 3 }; }
type Loaded = Awaited<ReturnType<typeof load>>;
const expected: Loaded = { count: 3 };
assert.deepEqual(await load(), expected);''','The type aliases perform no I/O and no waiting. The await expression is the actual runtime operation, and the assertion compares its observed result.'),
ex('Check a configuration with satisfies','Require exactly the literal success/failure keys on a label table.','valid table remains usable; misspelled literal key is a compiler error.',r'''const labels = { success: 'Ready', failure: 'Retry' } satisfies Record<'success' | 'failure', string>;
assert.equal(labels.success, 'Ready');
function negativeTypeCheck(): void {
  // @ts-expect-error typo is not a permitted literal key and failure is absent.
  const invalid = { success: 'Ready', typo: 'Retry' } satisfies Record<'success' | 'failure', string>;
  void invalid;
}
void negativeTypeCheck;''','satisfies checks the expression against the required relation without functioning as a runtime parser. Dynamic external keys still need validation before they become trusted configuration.')],source=TS+'mapped-types.html',notes='''### A useful boundary for advanced types

A utility should preserve a relationship the program actually implements. If a response mapper claims to omit private fields but returns the same object, the type has become misleading documentation. If a conditional type takes several minutes to understand and serves one call site, a simple named type may be easier to maintain. Check compiler diagnostics on changed types, runtime serialization on changed values, and the cost of explaining the API to another developer. These are separate forms of evidence.''')

add(24,
'''An external payload should enter typed code as unknown. JSON parsing establishes syntactic validity, but the result may be null, an array, a primitive or an object with the wrong fields. A runtime validator must inspect the shape and domain constraints before producing a trusted typed value. A type assertion skips this work; it cannot turn malformed input into valid data.

This lesson validates a small order with an id and an array of line items. Each item has a nonempty SKU and a positive safe-integer quantity. The validator returns a discriminated result instead of throwing for expected user-data errors, and includes a path such as items[1].quantity so the caller can identify the failing field. It copies accepted records so later edits to the original JSON object do not invalidate the already validated value.

Validation depth and resource budgets must be chosen together. An arbitrary recursive schema can consume excessive stack, CPU or memory. Here the structure has two bounded levels, at most twenty items, and bounded string lengths. Unknown extra keys are rejected deliberately. This is an exact fixture schema, not a claim that every API should reject forward-compatible fields. A permissive protocol might retain or ignore extras under a documented versioning policy.''',
'''A record guard checks typeof object, non-null and non-array before exposing string-key access as unknown. Domain checks then establish primitive types and bounds. The success branch carries an Order value; the failure branch carries a code, path and message. The JSON wrapper separates parse failure from schema failure. When validating an array, check each element and build a new typed output; do not cast the entire array after inspecting only the first row.''',
[('Unknown input','A value whose structure has not yet been established.'),('Schema validation','Runtime checks for the required object and collection shape.'),('Domain validation','Checks for business constraints beyond primitive types.'),('Diagnostic path','A stable field location identifying where validation failed.')],[
ex('Validate and copy a complete order','Parse an order with two line items and inspect the typed success.','success with total quantity 5; independent copied item records.',r'''const raw: unknown = { id: 'A', items: [{ sku: 'X', quantity: 2 }, { sku: 'Y', quantity: 3 }] };
const result = validateOrder(raw);
if (!result.ok) throw new Error(result.message);
assert.equal(result.ok, true);
assert.equal(result.value.items.reduce((sum, item) => sum + item.quantity, 0), 5);
assert.notEqual(result.value, raw);''','The successful branch provides a typed value only after all fields pass. The result contains new objects, separating validation from later mutation of the input graph.'),
ex('Report a nested domain failure precisely','Validate a second item with quantity zero.','failure code schema and path items[1].quantity.',r'''const result = validateOrder({ id: 'A', items: [{ sku: 'X', quantity: 2 }, { sku: 'Y', quantity: 0 }] });
assert.equal(result.ok, false);
if (result.ok) throw new Error('expected rejection');
assert.equal(result.code, 'schema');
assert.equal(result.path, 'items[1].quantity');''','Checking every element prevents a valid first row from legitimizing invalid later rows. A stable path is more useful to the caller than a generic invalid input message.'),
ex('Separate JSON syntax failure from schema failure','Parse malformed JSON and valid JSON null.','codes json and schema respectively.',r'''const malformed = parseOrder('{broken');
const wrongShape = parseOrder('null');
assert.equal(malformed.ok, false);
assert.equal(wrongShape.ok, false);
if (malformed.ok || wrongShape.ok) throw new Error('expected failures');
assert.equal(malformed.code, 'json');
assert.equal(wrongShape.code, 'schema');''','The two failure categories identify different repair actions. A client can fix JSON syntax before reasoning about missing domain fields.'),
ex('Reject unknown fields and excessive item counts','Add an extra top-level field, then exceed the twenty-item limit.','paths $ and items respectively.',r'''const extra = validateOrder({ id: 'A', items: [], admin: true });
const tooMany = validateOrder({ id: 'A', items: Array.from({ length: 21 }, () => ({ sku: 'X', quantity: 1 })) });
assert.equal(extra.ok, false);
assert.equal(tooMany.ok, false);
if (extra.ok || tooMany.ok) throw new Error('expected failures');
assert.equal(extra.path, '$');
assert.equal(tooMany.path, 'items');''','Exact keys and bounded collection sizes are explicit choices of this schema. They prevent unnoticed extra configuration and keep work proportional to a small known limit.'),
ex('Preserve the validated value after input mutation','Validate a mutable source and edit its first item afterward.','validated quantity stays 2 while input becomes 9.',r'''const raw = { id: 'A', items: [{ sku: 'X', quantity: 2 }] };
const result = validateOrder(raw);
if (!result.ok) throw new Error(result.message);
raw.items[0].quantity = 9;
assert.equal(result.value.items[0].quantity, 2);
assert.equal(raw.items[0].quantity, 9);''','Validation alone does not freeze references. Constructing a fresh output ensures that external aliases cannot silently modify the accepted state after the boundary.'),
ex('Exercise numeric and string boundaries','Reject NaN, fractional quantities, empty SKU and oversized identifiers.','every malformed fixture is rejected; an empty items array remains valid.',r'''for (const quantity of [NaN, 1.5, Number.MAX_SAFE_INTEGER + 1]) {
  assert.equal(validateOrder({ id: 'A', items: [{ sku: 'X', quantity }] }).ok, false);
}
assert.equal(validateOrder({ id: 'A', items: [{ sku: '', quantity: 1 }] }).ok, false);
assert.equal(validateOrder({ id: 'A'.repeat(41), items: [] }).ok, false);
assert.equal(validateOrder({ id: 'A', items: [] }).ok, true);''','A number type includes NaN, infinities and fractions, so the integer domain needs explicit checks. An empty item array is deliberately accepted here; changing that business rule requires a matching validator and test change.')],helper='''type LineItem = { sku: string; quantity: number };
type Order = { id: string; items: LineItem[] };
type Failure = { ok: false; code: 'json' | 'schema'; path: string; message: string };
type Validation = { ok: true; value: Order } | Failure;
function record(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}
function fail(path: string, message: string): Failure { return { ok: false, code: 'schema', path, message }; }
function shortText(value: unknown): value is string {
  return typeof value === 'string' && value.length > 0 && value.length <= 40;
}
function validateOrder(value: unknown): Validation {
  if (!record(value) || Object.keys(value).sort().join(',') !== 'id,items') return fail('$', 'exact order object required');
  if (!shortText(value.id)) return fail('id', 'nonempty id up to 40 code units required');
  if (!Array.isArray(value.items) || value.items.length > 20) return fail('items', 'at most 20 items required');
  const items: LineItem[] = [];
  for (let index = 0; index < value.items.length; index += 1) {
    const item: unknown = value.items[index];
    if (!record(item) || Object.keys(item).sort().join(',') !== 'quantity,sku') return fail(`items[${index}]`, 'exact line item required');
    if (!shortText(item.sku)) return fail(`items[${index}].sku`, 'bounded nonempty SKU required');
    if (typeof item.quantity !== 'number' || !Number.isSafeInteger(item.quantity) || item.quantity <= 0) return fail(`items[${index}].quantity`, 'positive safe integer required');
    items.push({ sku: item.sku, quantity: item.quantity });
  }
  return { ok: true, value: { id: value.id, items } };
}
function parseOrder(text: string): Validation {
  let value: unknown;
  try { value = JSON.parse(text); }
  catch { return { ok: false, code: 'json', path: '$', message: 'invalid JSON syntax' }; }
  return validateOrder(value);
}''',source=TS+'narrowing.html',notes='''### Trust and object provenance

These boundaries assume JSON-like passive data produced by JSON.parse or the controlled literals in the exercises. An arbitrary same-process object can contain getters or proxies that execute code on property reads. Treating hostile executable objects as inert JSON requires a different trust boundary. The validator is not advertised as a security sandbox for arbitrary JavaScript objects. The CLI or HTTP layer must also bound the raw payload before JSON.parse, since a post-parse item limit cannot undo memory already spent parsing an enormous request.''')
