<?php

declare(strict_types=1);

// web-039: Exceptions, errors and useful failure boundaries
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Trace the statements executed after requirePositive(0).
// 2. Add a specific catch around a recoverable validation error.
// 3. Build a failure-aware parser with explicit success and error paths.
// 4. Diagnose a catch-all that returns zero for every failure.
// 5. Test cleanup after both success and exception.
// 6. Explain the difference between learner diagnostics and public production errors.
//
// Worked example 1: An explicit contract failure
// function requirePositive(int $value): int {
//   if ($value <= 0) throw new InvalidArgumentException('Use a positive value');
//   return $value;
// }
//
// Worked example 2: Cleanup independent of success
// try { $result = requirePositive(0); }
// catch (InvalidArgumentException $error) { echo $error->getMessage(); }
// finally { echo "\nAttempt finished\n"; }

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-039 attempt finished without a failed check\n";
