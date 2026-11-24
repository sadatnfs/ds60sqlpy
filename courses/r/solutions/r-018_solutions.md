# r-018: reference reasoning

Use the [complete reference](r-018_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The calendar contains leap day. Counting date labels across the boundary therefore gives two days.

Changing the display zone does not change the underlying instant. The elapsed interval is calculated between instants, not by subtracting printed clock strings.

## Explained practice

### Exercise 1

Predict the date after 2024-02-28.

It is 2024-02-29.

**Approach:** Parse the first starter value with `as.Date()` and add 1. Date arithmetic counts whole calendar days, so no time of day or zone is involved.

**Why it holds here:** 2024 is divisible by 4 and is not a century year, so February has 29 days. One day after 2024-02-28 is therefore 2024-02-29, and the starter's second value, 2024-03-01, is two days after the first rather than one.

**Tempting mistake:** Incrementing the day field of the string and rolling over to March after day 28. That produces 2024-03-01 and silently drops leap day, which is exactly the boundary this input was chosen to test.

**Verify:** `format(as.Date("2024-02-28") + 1)` returns "2024-02-29", and `as.numeric(as.Date(dates[2]) - as.Date(dates[1]))` returns 2.

### Exercise 2

Add two hours to a declared UTC instant.

The instant advances 7200 seconds.

**Approach:** Parse the timestamp with an explicit format and `tz = "UTC"`, then add 7200, because arithmetic on POSIXct values is in seconds.

**Why it holds here:** UTC never shifts for daylight saving, so two clock hours and two elapsed hours agree for this instant. 12:00 becomes 14:00 on the same date, and difftime reports the gap in the unit that was asked for rather than one R picks.

**Tempting mistake:** Writing `instant + 2` to mean two hours. POSIXct counts seconds, so the result is 12:00:02, a value that looks almost unchanged when printed to the minute and is easy to miss in review.

**Verify:** `as.numeric(difftime(instant + 7200, instant, units = "hours"))` returns 2, and `format(instant + 7200, "%H:%M", tz = "UTC")` shows "14:00".

### Exercise 3

Parse an explicit ISO calendar date.

as.Date("2025-01-15") retains the calendar date.

**Approach:** Parse "2025-01-15" with `as.Date()` and keep it as a Date, since the source records a day and no time of day.

**Why it holds here:** A Date carries no zone, so it prints as 2025-01-15 in every session and on every machine. Its arithmetic is in days, which is what a due date or a reporting day needs.

**Tempting mistake:** Storing the day as `as.POSIXct("2025-01-15", tz = "UTC")`. That invents a midnight UTC time, and formatting it for New York shows 2025-01-14 19:00, moving the record to the previous day.

**Verify:** `inherits(as.Date("2025-01-15"), "Date")` returns TRUE, and `format(as.Date("2025-01-15"))` returns "2025-01-15".

### Exercise 4

Diagnose a local timestamp with no zone near a daylight-saving change.

Require the source zone and a defined resolution/rejection policy.

**Approach:** Ask the data owner for the source zone, then check whether each label falls in the skipped spring hour or the repeated autumn hour and apply a written policy: reject, or choose the earlier or later offset.

**Why it holds here:** In New York the labels 02:00 to 02:59 never occurred on 2025-03-09, and 01:00 to 01:59 occurred twice on 2025-11-02, first as EDT and then as EST. A bare "2025-11-02 01:30" therefore names two instants one hour apart, and nothing in the text says which.

**Tempting mistake:** Parsing without tz. R then uses the session zone, so the same file yields different instants on a laptop set to UTC and on a server set to New York, and a nonexistent label may become NA or shift depending on the platform.

**Verify:** `format(as.POSIXct(c("2025-11-02 05:30", "2025-11-02 06:30"), tz = "UTC"), "%H:%M %Z", tz = "America/New_York")` shows "01:30 EDT" and "01:30 EST", one label for two instants.

### Exercise 5

Detect invalid date text.

A failed parse is missing and should be counted or rejected.

**Approach:** Parse with an explicit format, then count results that are NA where the raw text was not, and stop or report those rows before any date arithmetic.

**Why it holds here:** With a format supplied, `as.Date("not-a-date", format = "%Y-%m-%d")` returns NA and raises no error, so the program keeps running unless the result is inspected. The NA would later vanish from a grouped count or make a range NA.

**Tempting mistake:** Relying on as.Date to fail loudly. Without a format it stops only when the first non-missing value matches no default format; if an earlier row parses, later bad rows quietly become NA, and with a format no row ever errors.

**Verify:** `is.na(as.Date("not-a-date", format = "%Y-%m-%d"))` returns TRUE, and `sum(is.na(parsed) & !is.na(raw))` shows how many rows failed.

### Exercise 6

Separate business-date grouping from event ordering.

Keep both representations with their meanings stated.

**Approach:** Keep the UTC instant as the canonical column for ordering, and derive a separate business date with `as.Date(instant, tz = "America/New_York")` for grouping and labels.

**Why it holds here:** The reference instant, 12:00 UTC, is 07:00 in New York on the same date, but an order at 02:00 UTC on January 16 belongs to the store's January 15. Ordering uses the stored seconds, which no display zone changes, so both columns can coexist without conflict.

**Tempting mistake:** Sorting by the formatted local clock text. On 2025-11-02 an event at 01:45 EDT happened before one at 01:15 EST, yet the strings sort 01:15 first, reversing the true order.

**Verify:** `as.Date(as.POSIXct("2025-01-16 02:00", tz = "UTC"), tz = "America/New_York")` returns 2025-01-15, and `as.numeric(instant + 1) > as.numeric(instant)` returns TRUE.

## What the checks establish

The reference makes 6 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
