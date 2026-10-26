# r-018: reference reasoning

Use the [complete reference](r-018_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The calendar contains leap day. Counting date labels across the boundary therefore gives two days.

Changing the display zone does not change the underlying instant. The elapsed interval is calculated between instants, not by subtracting printed clock strings.

## Explained practice

### Exercise 1

Predict the date after 2024-02-28.

It is 2024-02-29.

**Expected evidence:** It is 2024-02-29.

### Exercise 2

Add two hours to a declared UTC instant.

The instant advances 7200 seconds.

**Expected evidence:** The instant advances 7200 seconds.

### Exercise 3

Parse an explicit ISO calendar date.

as.Date("2025-01-15") retains the calendar date.

**Expected evidence:** as.Date("2025-01-15") retains the calendar date.

### Exercise 4

Diagnose a local timestamp with no zone near a daylight-saving change.

Require the source zone and a defined resolution/rejection policy.

**Expected evidence:** Require the source zone and a defined resolution/rejection policy.

### Exercise 5

Detect invalid date text.

A failed parse is missing and should be counted or rejected.

**Expected evidence:** A failed parse is missing and should be counted or rejected.

### Exercise 6

Separate business-date grouping from event ordering.

Keep both representations with their meanings stated.

**Expected evidence:** Keep both representations with their meanings stated.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
