<?php

declare(strict_types=1);

// web-037: Strings, UTF-8, bytes and contextual encoding
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Predict the UTF-8 byte length of é.
// 2. Encode a Unicode label as JSON with explicit error handling.
// 3. Build a text inspection report that labels bytes honestly.
// 4. Diagnose a truncated string that splits a multibyte sequence.
// 5. Compare a plain ASCII label and a Unicode label.
// 6. Explain validation, normalization and output escaping separately.
//
// Worked example 1: Bytes are not letters
// $text = 'é';
// echo strlen($text);
//
// Worked example 2: Safe JSON text
// $json = json_encode(['label' => 'café'], JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE);

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-037 attempt finished without a failed check\n";
