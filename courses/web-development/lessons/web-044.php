<?php

declare(strict_types=1);

// web-044: Testing PHP: examples, boundaries and contract evidence
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Classify a pure-function check and a real database transaction check.
// 2. Add an empty-input test with an explicit expected result.
// 3. Create a test table for a bounded study-duration function.
// 4. Diagnose a test that catches the wrong exception as success.
// 5. Temporarily introduce a known bug in a learner copy.
// 6. Explain why a passing reference is not a bug-free guarantee.
//
// Worked example 1: An independent expected value
// check(totalMinutes([20, 30]) === 50, 'Wrong total');
//
// Worked example 2: A declared failure
// $rejected = false;
// try { totalMinutes([-1]); } catch (InvalidArgumentException) { $rejected = true; }
// check($rejected, 'Negative input accepted');

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-044 attempt finished without a failed check\n";
