<?php

declare(strict_types=1);

// web-047: Server form validation and redisplay without data loss
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Predict what happens when a caller sends topic[]=HTML.
// 2. Add an allowlist for supported topics.
// 3. Build a validator returning cleaned values and field-specific errors.
// 4. Diagnose trimming an array-shaped request value.
// 5. Test missing fields, arrays, out-of-range minutes and valid data.
// 6. Explain the limits of POST redirect GET.
//
// Worked example 1: Reject the wrong shape
// $raw = $input['topic'] ?? null;
// if (!is_string($raw)) { $errors['topic'] = 'Choose a topic.'; }
//
// Worked example 2: Validate a bounded decimal field
// if (!is_string($rawMinutes) || !preg_match('/^[0-9]{1,3}$/D', $rawMinutes)) { $errors['minutes'] = 'Use whole minutes.'; }

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-047 attempt finished without a failed check\n";
