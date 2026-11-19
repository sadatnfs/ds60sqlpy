<?php

declare(strict_types=1);

// web-043: Dates, time zones and deterministic clocks
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Explain an instant versus a local clock reading.
// 2. Convert a fixed instant to a named time zone.
// 3. Build a deterministic study-session time report.
// 4. Diagnose a test that fails around midnight.
// 5. Compare elapsed seconds with a calendar-day operation near a clock change.
// 6. Explain why a numeric offset is not a complete regional time-zone rule.
//
// Worked example 1: A fixed instant
// $instant = new DateTimeImmutable('2024-01-01T12:00:00+00:00');
//
// Worked example 2: A display conversion
// $local = $instant->setTimezone(new DateTimeZone('America/New_York'));
// echo $local->format('Y-m-d H:i P');

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-043 attempt finished without a failed check\n";
