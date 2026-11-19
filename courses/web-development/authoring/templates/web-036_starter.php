<?php

declare(strict_types=1);

// web-036: Functions, contracts, closures and reusable logic
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Explain the difference between returning and echoing a value.
// 2. Add a value-range guard to a typed function.
// 3. Build reusable duration calculation and display functions.
// 4. Diagnose a result depending on an undocumented global.
// 5. Test zero, a normal value and a negative input.
// 6. Explain when a closure improves a transformation.
//
// Worked example 1: A typed calculation
// function doubleMinutes(int $minutes): int {
//   if ($minutes < 0) throw new InvalidArgumentException('Negative minutes');
//   return $minutes * 2;
// }
//
// Worked example 2: A small closure
// $doubled = array_map(fn(int $value): int => $value * 2, [10, 20]);

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-036 attempt finished without a failed check\n";
