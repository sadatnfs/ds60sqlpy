<?php

declare(strict_types=1);

// web-033: Expressions, integer money and deliberate conversion
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Predict 125 cents times three units.
// 2. Add a fixed 50-cent fee with a named intermediate value.
// 3. Implement a bounded quantity calculation and cents formatter.
// 4. Diagnose a concatenation expression that hides arithmetic grouping.
// 5. Reject a negative quantity and test zero.
// 6. Explain when integer cents are insufficient.
//
// Worked example 1: Integer minor units
// $unitCents = 125;
// $quantity = 3;
// $totalCents = $unitCents * $quantity;
//
// Worked example 2: Display without losing the unit
// $label = intdiv($totalCents, 100) . '.' . str_pad((string) ($totalCents % 100), 2, '0', STR_PAD_LEFT);

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-033 attempt finished without a failed check\n";
