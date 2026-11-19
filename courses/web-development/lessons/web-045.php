<?php

declare(strict_types=1);

// web-045: Templates and context-specific output escaping
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Predict the escaped form of a name containing < and &.
// 2. Add an escaping helper with an explicit UTF-8 contract.
// 3. Render a study-card template from synthetic untrusted labels.
// 4. Explain why the same helper is insufficient for a JavaScript string.
// 5. Test quotes, ampersands and an attack-shaped tag string.
// 6. Explain why validated text still needs output escaping.
//
// Worked example 1: HTML text escaping
// $name = '<Ada & Bea>';
// echo htmlspecialchars($name, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
//
// Worked example 2: A bounded template
// $html = '<p>Hello, ' . e($name) . '</p>';

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-045 attempt finished without a failed check\n";
