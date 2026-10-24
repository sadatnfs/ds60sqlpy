import { strict as assert } from "node:assert";

type LineItem = { sku: string; quantity: number };
type Order = { id: string; items: LineItem[] };
type Failure = { ok: false; code: "json" | "schema"; path: string; message: string };
type Validation = { ok: true; value: Order } | Failure;
function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
function fail(path: string, message: string): Failure {
  return { ok: false, code: "schema", path, message };
}
function shortText(value: unknown): value is string {
  return typeof value === "string" && value.length > 0 && value.length <= 40;
}
function validateOrder(value: unknown): Validation {
  if (!record(value) || Object.keys(value).sort().join(",") !== "id,items")
    return fail("$", "exact order object required");
  if (!shortText(value.id)) return fail("id", "nonempty id up to 40 code units required");
  if (!Array.isArray(value.items) || value.items.length > 20)
    return fail("items", "at most 20 items required");
  const items: LineItem[] = [];
  for (let index = 0; index < value.items.length; index += 1) {
    const item: unknown = value.items[index];
    if (!record(item) || Object.keys(item).sort().join(",") !== "quantity,sku")
      return fail(`items[${index}]`, "exact line item required");
    if (!shortText(item.sku)) return fail(`items[${index}].sku`, "bounded nonempty SKU required");
    if (
      typeof item.quantity !== "number" ||
      !Number.isSafeInteger(item.quantity) ||
      item.quantity <= 0
    )
      return fail(`items[${index}].quantity`, "positive safe integer required");
    items.push({ sku: item.sku, quantity: item.quantity });
  }
  return { ok: true, value: { id: value.id, items } };
}
function parseOrder(text: string): Validation {
  let value: unknown;
  try {
    value = JSON.parse(text);
  } catch {
    return { ok: false, code: "json", path: "$", message: "invalid JSON syntax" };
  }
  return validateOrder(value);
}

export async function verify(): Promise<{ checks: number; status: string }> {
  // Exercise 1: Validate and copy a complete order
  {
    const raw: unknown = {
      id: "A",
      items: [
        { sku: "X", quantity: 2 },
        { sku: "Y", quantity: 3 },
      ],
    };
    const result = validateOrder(raw);
    if (!result.ok) throw new Error(result.message);
    assert.equal(result.ok, true);
    assert.equal(
      result.value.items.reduce((sum, item) => sum + item.quantity, 0),
      5,
    );
    assert.notEqual(result.value, raw);
  }

  // Exercise 2: Report a nested domain failure precisely
  {
    const result = validateOrder({
      id: "A",
      items: [
        { sku: "X", quantity: 2 },
        { sku: "Y", quantity: 0 },
      ],
    });
    assert.equal(result.ok, false);
    if (result.ok) throw new Error("expected rejection");
    assert.equal(result.code, "schema");
    assert.equal(result.path, "items[1].quantity");
  }

  // Exercise 3: Separate JSON syntax failure from schema failure
  {
    const malformed = parseOrder("{broken");
    const wrongShape = parseOrder("null");
    assert.equal(malformed.ok, false);
    assert.equal(wrongShape.ok, false);
    if (malformed.ok || wrongShape.ok) throw new Error("expected failures");
    assert.equal(malformed.code, "json");
    assert.equal(wrongShape.code, "schema");
  }

  // Exercise 4: Reject unknown fields and excessive item counts
  {
    const extra = validateOrder({ id: "A", items: [], admin: true });
    const tooMany = validateOrder({
      id: "A",
      items: Array.from({ length: 21 }, () => ({ sku: "X", quantity: 1 })),
    });
    assert.equal(extra.ok, false);
    assert.equal(tooMany.ok, false);
    if (extra.ok || tooMany.ok) throw new Error("expected failures");
    assert.equal(extra.path, "$");
    assert.equal(tooMany.path, "items");
  }

  // Exercise 5: Preserve the validated value after input mutation
  {
    const raw = { id: "A", items: [{ sku: "X", quantity: 2 }] };
    const result = validateOrder(raw);
    if (!result.ok) throw new Error(result.message);
    raw.items[0].quantity = 9;
    assert.equal(result.value.items[0].quantity, 2);
    assert.equal(raw.items[0].quantity, 9);
  }

  // Exercise 6: Exercise numeric and string boundaries
  {
    for (const quantity of [NaN, 1.5, Number.MAX_SAFE_INTEGER + 1]) {
      assert.equal(validateOrder({ id: "A", items: [{ sku: "X", quantity }] }).ok, false);
    }
    assert.equal(validateOrder({ id: "A", items: [{ sku: "", quantity: 1 }] }).ok, false);
    assert.equal(validateOrder({ id: "A".repeat(41), items: [] }).ok, false);
    assert.equal(validateOrder({ id: "A", items: [] }).ok, true);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));
