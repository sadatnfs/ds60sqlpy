<?php

declare(strict_types=1);

// web-032: Values, types, strict comparisons and null
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Predict strict equality for '0', 0 and false.
// 2. Add a typed diagnostic to a value before converting it.
// 3. Model an optional note without confusing missing, empty and null.
// 4. Repair a loose comparison that accepts an unintended type.
// 5. Test zero as a valid numeric boundary.
// 6. Explain the limited scope of strict_types.
//
// Worked example 1: Type matters
// $text = '0';
// $number = 0;
// var_export($text === $number);
//
// Worked example 2: Missing versus null
// $record = ['note' => null];
// var_export(array_key_exists('note', $record));
// var_export($record['note'] ?? 'No note');

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-032 attempt finished without a failed check\n";
