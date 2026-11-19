<?php

declare(strict_types=1);

// web-041: Interfaces, composition and replaceable dependencies
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Identify the dependency hidden by the interface.
// 2. Supply an in-memory store with a known count.
// 3. Build a summary service with an injected repository.
// 4. Diagnose a test double that returns impossible domain values.
// 5. Test zero completed lessons.
// 6. Explain what remains untested by an in-memory repository.
//
// Worked example 1: A narrow dependency
// interface ProgressStore { public function completedCount(): int; }
//
// Worked example 2: Composition
// final class Summary { public function __construct(private ProgressStore $store) {}
//   public function label(): string { return $this->store->completedCount() . ' complete'; }
// }

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-041 attempt finished without a failed check\n";
