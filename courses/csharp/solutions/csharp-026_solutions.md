# csharp-026: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-026_solution.cs](csharp-026_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Round-trip a small transport record:** Equality checks the modeled data rather than incidental property ordering in JSON text. The restored name and quantity match the original record.

**Validate after structural decoding:** Parsing answers whether the representation is understood. Validation answers whether the application may use it. Valid JSON can decode into a rejected domain value.

## Task answers

### Task 1: Predict and explain

Predict what round-trip equality establishes and what it does not.

**Written answer.** `restored == original` establishes that this record, serialized by `JsonSerializer` and deserialized by the same serializer with the same options, comes back with equal `Name` and `Quantity`. It does not establish that the JSON text matches an agreed external contract, that JSON produced by another system or an older version decodes correctly, that missing or unknown fields are handled the way you intend, or that the decoded value satisfies domain rules such as a nonnegative quantity.

**Why it is correct.** A round trip tests the serializer against itself. Any naming or default that is wrong in the same way on both sides cancels out, so the test passes even when the wire format would surprise a partner system.

**Plausible wrong approach.** Treating the round trip as a full contract test leads to shipping a renamed property: the round trip still passes, while every stored document and every other client breaks.

**How to verify.** Add a fixed JSON literal written by hand from the contract, deserialize it, and compare it with an expected record. Example B shows the separate domain check that a round trip cannot provide.

### Task 2: Guided modification

Add a clearly versioned optional description field.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
string v1 = "{\"Name\":\"pear\",\"Quantity\":3}";
string v2 = "{\"Version\":2,\"Name\":\"pear\",\"Quantity\":3," +
            "\"Description\":\"green\"}";
string Describe(string json) {
  using var document = JsonDocument.Parse(json);
  var root = document.RootElement;
  int version = 1;
  if (root.TryGetProperty("Version", out var number))
    version = number.GetInt32();
  if (version < 2 || !root.TryGetProperty("Description", out var text))
    return "";
  return text.GetString() ?? "";
}
Check(Describe(v1) == "", "version 1 has no description");
Check(Describe(v2) == "green", "version 2 description");
var old = JsonSerializer.Deserialize<ItemDto>(v2);
Check(old == new ItemDto("pear", 3), "version 1 reader still works");
```

**Observe:** A version 1 document has no description, a version 2 document yields green and the old ItemDto reader still decodes the version 2 document.

The new field is optional and tied to an explicit `Version` number: a document without `Version` is treated as version 1, and only version 2 or later is asked for `Description`. The old `ItemDto` contract keeps working because `System.Text.Json` ignores unknown properties by default, so adding a field is a compatible change for existing readers.

**Plausible wrong approach.** Making `Description` required, or reading it without checking the version, breaks every stored version 1 document. Reusing an existing property name with a new meaning breaks old readers silently instead of loudly.

**How to verify.** Remove `Description` from `v2` and confirm `Describe` returns an empty string instead of throwing. Change `Version` to 1 in `v2` and confirm the description is ignored.

### Task 3: Independent construction

Write a decoder returning explicit validation errors for missing name and negative quantity.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
List<string> Decode(string json) {
  var errors = new List<string>();
  var item = JsonSerializer.Deserialize<ItemDto>(json);
  if (item is null || string.IsNullOrWhiteSpace(item.Name)) {
    errors.Add("name is required");
  }
  if (item is not null && item.Quantity < 0) {
    errors.Add("quantity must be nonnegative");
  }
  return errors;
}
string valid = "{\"Name\":\"pear\",\"Quantity\":2}";
Check(Decode(valid).Count == 0, "valid item");
Check(Decode("{\"Quantity\":-1}").Count == 2, "both errors reported");
```

**Observe:** A valid item gives no errors; a missing name with quantity -1 gives two errors.

Decoding and validation are separate steps, and the decoder reports every problem it finds instead of stopping at the first.

### Task 4: Diagnose a defect

Diagnose trusting default values from missing JSON fields.

**Written answer.** `JsonSerializer.Deserialize<ItemDto>("{\"Name\":\"pear\"}")` succeeds and produces `Quantity` 0. The missing field was filled with the default value of `int`, so the decoder cannot tell "the sender said 0" from "the sender forgot the field". Code that trusts the result records a real zero stock level for data that was never sent. Make the field required: set `RespectRequiredConstructorParameters = true` in `JsonSerializerOptions` for a positional record, mark the property with `[JsonRequired]`, or inspect the document for the property before accepting it.

**Why it is correct.** By default the serializer binds only what is present and uses `default(T)` for everything else. For a value type, the default is a legal value, so absence leaves no trace in the decoded object.

**Plausible wrong approach.** Checking `item.Quantity == 0` afterwards rejects legitimate zero quantities as well. Making `Quantity` an `int?` without changing the validation only moves the ambiguity, unless null is then rejected explicitly.

**How to verify.** Decode the document without `Quantity` and observe 0. With the required setting enabled, check that the same call throws `JsonException`, while an explicit `"Quantity":0` still decodes to 0.

### Task 5: Boundary evidence

Test malformed JSON, JSON null and an extra unknown field.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
bool malformed = false;
try {
  JsonSerializer.Deserialize<ItemDto>("{\"Name\":");
} catch (JsonException) {
  malformed = true;
}
Check(malformed, "malformed JSON throws JsonException");
var nothing = JsonSerializer.Deserialize<ItemDto>("null");
Check(nothing is null, "JSON null decodes to a null reference");
string extra = "{\"Name\":\"pear\",\"Quantity\":2,\"Color\":\"green\"}";
var item = JsonSerializer.Deserialize<ItemDto>(extra);
Check(item == new ItemDto("pear", 2), "unknown field ignored");
```

**Observe:** Truncated JSON throws JsonException, the literal null decodes to null and an unknown Color field is ignored.

The three inputs fail at different layers. Truncated text is not JSON at all, so the parser throws. `null` is valid JSON whose value is nothing, so the result is a null reference even though the declared type is a non-nullable `ItemDto`; the caller must check for it. An extra property is valid JSON that the contract does not mention, and the default policy skips it, which keeps old readers compatible with newer writers.

**Plausible wrong approach.** Using `Deserialize<ItemDto>(json)!` and continuing turns the `null` input into a `NullReferenceException` far from the decoder. Expecting the unknown field to throw assumes a strict policy that is not the default.

**How to verify.** Pass options with `UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow` for the extra-field case and confirm it now throws `JsonException`. Decide which policy the contract wants and keep a test for it.

### Task 6: Transfer and justify

Design a migration from a renamed quantity field while retaining old saved records.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Serialization**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

JSON provides a portable syntax for values, arrays and objects; it does not define the business schema. Deserializing into a type supplies a structural mapping, but required domain rules still need validation. A missing property can become a default value, and a syntactically valid object can still be meaningless for the application.

Schema evolution requires deciding what happens when fields are added, removed or renamed. A version field and explicit migration can preserve meaning. Do not equate a successful deserialize call with a safe external object. Validate ranges and identities before admitting the object into domain logic, and avoid serializing internal secrets merely because a public property exists.

`JsonSerializer.Serialize` creates JSON text. `Deserialize<T>` maps it into T and can return null. Records provide compact transport shapes. Serialization options control naming and formatting but do not replace domain validation.

JSON text equality is sensitive to formatting and property ordering. Structural decoding does not enforce every domain invariant. Keep public transport models separate from internal objects carrying credentials or resources.

## Review before continuing

Run the reference and confirm that it prints `csharp-026: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
