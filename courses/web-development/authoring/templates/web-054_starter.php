<?php

declare(strict_types=1);

// web-054: JSON APIs, schemas and consistent error responses
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Distinguish a JSON number from a numeric-looking string.
// 2. Add a consistent error code to invalid-input responses.
// 3. Build a response model that maps success and validation failure consistently.
// 4. Diagnose an internal exception serialized directly to a public response.
// 5. Round-trip a Unicode label and a boolean through JSON.
// 6. Explain a backward-compatible versus breaking API change.
//
// Worked example 1: A successful representation
// $body = ['topic' => 'CSS', 'minutes' => 30, 'complete' => false];
//
// Worked example 2: A validation error
// { "error": { "code": "invalid_plan", "fields": { "minutes": "Use 5 to 120 minutes." } } }

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-054 attempt finished without a failed check\n";
