<?php

declare(strict_types=1);

// web-038: Structured data, streams and bounded file handling
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Explain why valid JSON can still be invalid application input.
// 2. Add a bounded decoding depth and explicit parse errors.
// 3. Parse a small study record and round-trip it through a temporary stream.
// 4. Diagnose an empty read caused by the stream cursor position.
// 5. Reject an unexpected field type and an oversized input string.
// 6. Explain why user-controlled paths need an ownership policy.
//
// Worked example 1: Parse then validate
// $data = json_decode('{"minutes":30}', true, 32, JSON_THROW_ON_ERROR);
// if (!is_int($data['minutes'] ?? null)) throw new InvalidArgumentException('Expected integer minutes');
//
// Worked example 2: A temporary stream
// $stream = fopen('php://temp', 'w+');
// fwrite($stream, 'notes');
// rewind($stream);
// echo stream_get_contents($stream);

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-038 attempt finished without a failed check\n";
