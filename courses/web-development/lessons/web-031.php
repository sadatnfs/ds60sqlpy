<?php

declare(strict_types=1);

// web-031: PHP begins: interpreter, CLI and server execution
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Predict which characters in the greeting source appear in output.
// 2. Change the planned minutes while preserving the label.
// 3. Write a PHP program that prints a study topic and computed duration.
// 4. Diagnose a missing semicolon as a parse error.
// 5. Print literal angle brackets and explain the output surface.
// 6. Compare the CLI lifecycle with a server request lifecycle.
//
// Worked example 1: First output
// <?php
// echo "Hello, classroom.\n";
//
// Worked example 2: A named value
// $minutes = 30;
// echo "Planned minutes: " . $minutes . "\n";

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-031 attempt finished without a failed check\n";
