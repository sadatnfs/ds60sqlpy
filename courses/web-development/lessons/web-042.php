<?php

declare(strict_types=1);

// web-042: Namespaces, project layout and Composer boundaries
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Explain what a namespace does and does not install.
// 2. Compare a short imported name with its fully qualified name.
// 3. Design a small project layout with source, tests and a public entrypoint.
// 4. Diagnose a missing class despite a correct namespace declaration.
// 5. Explain why an untrusted include filename is dangerous.
// 6. Describe a deliberate dependency update and lockfile review.
//
// Worked example 1: A qualified name
// namespace Learning;
// final class Label { public static function text(): string { return 'Study'; } }
//
// Worked example 2: A project contract
// { "autoload": { "psr-4": { "Learning\\": "src/" } } }

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-042 attempt finished without a failed check\n";
