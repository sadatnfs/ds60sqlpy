# js-006: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

Objects associate property keys with values and can inherit properties through a prototype chain. An own property belongs directly to the object; an inherited property may be found through lookup even when it is absent from the object's own keys. Object.hasOwn checks this distinction without relying on a method that an input object could override. A plain object is useful for records, but Map or a null-prototype dictionary can be clearer for arbitrary external keys.

Destructuring reads properties into bindings, and spread copies enumerable own properties into a new object. Neither automatically deep-copies nested state or validates a schema. Getters can execute code during property access, so an object-shaped value is not always passive data. This lesson uses literal records and controlled prototypes to make lookup, ownership and copying visible.

**Own property:** A property stored directly on an object.

**Prototype chain:** The linked objects consulted during inherited property lookup.

**Destructuring:** Binding selected properties from a value.

**Shallow freeze:** Preventing direct changes without recursively freezing referenced objects.

## Reading the implementation

Object.create(proto) sets a chosen prototype. The in operator checks inherited as well as own properties, while Object.hasOwn checks only own membership. Object.keys enumerates own enumerable string keys. Destructuring defaults apply to undefined values. Object.freeze prevents direct property changes on that object but does not recursively freeze nested objects.

## Exercise 1: Distinguish own and inherited properties

Task: Create a child inheriting kind and owning name.

Property lookup and record schema inspection answer different questions. Accepting inherited fields as request data can violate a boundary contract.

```javascript
const parent = { kind: 'record' };
const child = Object.create(parent);
child.name = 'sample';
assert.equal('kind' in child, true);
assert.equal(Object.hasOwn(child, 'kind'), false);
assert.equal(Object.hasOwn(child, 'name'), true);
```

**Expected:** kind found by in but not hasOwn; name is own.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Copy only own enumerable fields

Task: Spread the child into a plain record and inspect keys.

Spread does not reproduce the prototype chain. It copies the declared enumerable own surface, which still may contain mutable nested references.

```javascript
const child = Object.create({ kind: 'record' });
child.name = 'sample';
const copy = { ...child };
assert.deepEqual(Object.keys(copy), ['name']);
assert.equal(copy.kind, undefined);
```

**Expected:** only name copied.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Use destructuring defaults carefully

Task: Read missing count and explicit null count with default 0.

The default applies to undefined, not every absence-like value. Validation remains necessary when null is not permitted.

```javascript
const { count: absent = 0 } = {};
const { count: explicit = 0 } = { count: null };
assert.equal(absent, 0);
assert.equal(explicit, null);
```

**Expected:** missing becomes 0; null remains null.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Use a null-prototype dictionary for arbitrary keys

Task: Store __proto__ as data in Object.create(null).

The fixture treats the key as data without changing a global prototype. A Map is another explicit choice for arbitrary key-value storage.

```javascript
const dictionary = Object.create(null);
dictionary['__proto__'] = 'literal data';
assert.equal(dictionary['__proto__'], 'literal data');
assert.equal(Object.getPrototypeOf(dictionary), null);
assert.equal(Object.hasOwn(dictionary, '__proto__'), true);
```

**Expected:** own value preserved; prototype remains null.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Expose shallow freeze

Task: Freeze an outer object and mutate its nested record.

Freezing the container does not recursively freeze reachable objects. The mutation demonstrates the actual boundary rather than a misleading immutable label.

```javascript
const value = Object.freeze({ nested: { count: 1 } });
assert.throws(() => {
  value.nested = {};
}, TypeError);
value.nested.count = 2;
assert.equal(value.nested.count, 2);
```

**Expected:** outer reassignment throws; inner value can change.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Observe a getter side effect

Task: Read a controlled getter twice and count calls.

Property access can execute behavior. A schema validator handling untrusted objects should not assume every property read is a passive field lookup.

```javascript
let calls = 0;
const value = {
  get next() {
    calls += 1;
    return calls;
  },
};
assert.equal(value.next, 1);
assert.equal(value.next, 2);
assert.equal(calls, 2);
```

**Expected:** values 1 then 2; getter executed twice.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
