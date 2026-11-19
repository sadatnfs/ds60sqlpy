<?php

declare(strict_types=1);

// web-034: Conditions, loops and bounded control flow
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Trace the accumulator after each iteration.
// 2. Add a guard against negative durations.
// 3. Build a bounded weekly-duration summary with a route label.
// 4. Diagnose a while loop whose condition never changes.
// 5. Test an empty collection.
// 6. Explain match versus switch for a typed mapping.
//
// Worked example 1: A bounded accumulation
// $total = 0;
// foreach ([20, 30, 15] as $minutes) { $total += $minutes; }
//
// Worked example 2: A deliberate mapping
// $label = match ('beginner') { 'beginner' => 'Start here', 'advanced' => 'Project work', default => 'Review route' };

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-034 attempt finished without a failed check\n";
