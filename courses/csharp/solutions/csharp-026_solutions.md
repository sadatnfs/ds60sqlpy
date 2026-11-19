# csharp-026: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-026_solution.cs](csharp-026_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Round-trip a small transport record:** Equality checks the modeled data rather than incidental property ordering in JSON text. The restored name and quantity match the original record.

**Validate after structural decoding:** Parsing answers whether the representation is understood. Validation answers whether the application may use it. Valid JSON can decode into a rejected domain value.

## Task answers

### Task 1: Predict and explain

Predict what round-trip equality establishes and what it does not.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Equality checks the modeled data rather than incidental property ordering in JSON text. The restored name and quantity match the original record.

### Task 2: Guided modification

Add a clearly versioned optional description field.

No separate reference answer has been written for this task. Start from Example B: Parsing answers whether the representation is understood. Validation answers whether the application may use it. Valid JSON can decode into a rejected domain value.

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

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: JSON text equality is sensitive to formatting and property ordering. Structural decoding does not enforce every domain invariant. Keep public transport models separate from internal objects carrying credentials or resources.

### Task 5: Boundary evidence

Test malformed JSON, JSON null and an extra unknown field.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Round-trip a small transport record) and Example B (Validate after structural decoding).

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
