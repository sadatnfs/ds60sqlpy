import { strict as assert } from "node:assert";

function parts(date) {
  const formatter = new Intl.DateTimeFormat("en-US", {
    timeZone: "America/New_York",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
    timeZoneName: "longOffset",
  });
  return Object.fromEntries(formatter.formatToParts(date).map((part) => [part.type, part.value]));
}
function calendarDate(text) {
  if (typeof text !== "string" || !/^\d{4}-\d{2}-\d{2}$/u.test(text))
    throw new RangeError("YYYY-MM-DD required");
  const date = new Date(text + "T00:00:00.000Z");
  if (!Number.isFinite(date.getTime()) || date.toISOString().slice(0, 10) !== text)
    throw new RangeError("invalid calendar date");
  return text;
}

export async function verify() {
  // Exercise 1: Compare offset spellings of one instant
  {
    const utc = new Date("2024-01-01T00:00:00Z");
    const offset = new Date("2023-12-31T19:00:00-05:00");
    assert.equal(utc.getTime(), offset.getTime());
    assert.equal(offset.toISOString(), "2024-01-01T00:00:00.000Z");
  }

  // Exercise 2: Observe a spring-forward clock gap
  {
    const before = new Date("2024-03-10T06:30:00Z");
    const after = new Date("2024-03-10T07:30:00Z");
    assert.equal(parts(before).hour, "01");
    assert.equal(parts(after).hour, "03");
    assert.equal(after.getTime() - before.getTime(), 60 * 60 * 1000);
  }

  // Exercise 3: Reject impossible or ambiguous calendar text
  {
    assert.equal(calendarDate("2024-02-29"), "2024-02-29");
    for (const text of ["2023-02-29", "01/02/2024", "2024-13-01"])
      assert.throws(() => calendarDate(text), RangeError);
  }

  // Exercise 4: Distinguish repeated fall-back clock readings
  {
    const first = new Date("2024-11-03T05:30:00Z");
    const second = new Date("2024-11-03T06:30:00Z");
    assert.equal(parts(first).hour, "01");
    assert.equal(parts(second).hour, "01");
    assert.equal(parts(first).minute, parts(second).minute);
    assert.notEqual(parts(first).timeZoneName, parts(second).timeZoneName);
    assert.equal(second.getTime() - first.getTime(), 3600000);
  }

  // Exercise 5: Inspect locale number parts without parsing display text
  {
    const value = 1234.5;
    const us = new Intl.NumberFormat("en-US").formatToParts(value);
    const de = new Intl.NumberFormat("de-DE").formatToParts(value);
    assert.equal(us.find((part) => part.type === "decimal").value, ".");
    assert.equal(de.find((part) => part.type === "decimal").value, ",");
    assert.equal(value, 1234.5);
  }

  // Exercise 6: Reject invalid timestamp and timezone assumptions
  {
    const invalid = new Date("not an ISO instant");
    assert.equal(Number.isNaN(invalid.getTime()), true);
    assert.throws(() => invalid.toISOString(), RangeError);
    assert.throws(
      () => new Intl.DateTimeFormat("en-US", { timeZone: "Invalid/Nowhere" }),
      RangeError,
    );
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));
