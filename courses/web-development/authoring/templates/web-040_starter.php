<?php

declare(strict_types=1);

// web-040: Objects, constructors and immutable value boundaries
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Name the invariant enforced by the constructor.
// 2. Add a method that formats the duration.
// 3. Build a validated study-session value object.
// 4. Diagnose a setter that allows invalid state after construction.
// 5. Test an empty topic and zero duration.
// 6. Explain shallow readonly versus deep immutability.
//
// Worked example 1: A validated value
// final class Duration {
//   public function __construct(public readonly int $minutes) {
//     if ($minutes < 0) throw new InvalidArgumentException('Negative duration');
//   }
// }
//
// Worked example 2: Derived behavior
// $duration = new Duration(45);
// echo $duration->minutes . ' minutes';

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-040 attempt finished without a failed check\n";
