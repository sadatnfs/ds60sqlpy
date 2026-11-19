<?php

declare(strict_types=1);

// web-035: Arrays, records, keys and transformations
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Explain how a list differs from a keyed record.
// 2. Add a second validated study row.
// 3. Filter and summarize study records without changing the originals.
// 4. Diagnose JSON output changing from an array to an object shape.
// 5. Test an empty result and a missing required field.
// 6. Explain the risk of a lingering foreach reference.
//
// Worked example 1: A small record
// $row = ['subject' => 'CSS', 'minutes' => 55];
// echo $row['subject'];
//
// Worked example 2: A filtered list
// $visible = array_values(array_filter($rows, fn(array $row): bool => $row['minutes'] >= 40));

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-035 attempt finished without a failed check\n";
