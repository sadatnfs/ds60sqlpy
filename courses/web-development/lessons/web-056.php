<?php

declare(strict_types=1);

// web-056: PHP milestone: a tested study-planner application core
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Draw the trust boundary around actor identity and form values.
// 2. Write the acceptance matrix before implementing the service.
// 3. Build a tested planner core with validation and prepared storage.
// 4. Diagnose a service that writes before validating all fields.
// 5. Test cross-owner retrieval and an invalid duration.
// 6. Explain the remaining work before this core becomes a deployed application.
//
// Worked example 1: Separate trust roles
// $result = createPlan($db, $trustedActorId, $untrustedInput);
//
// Worked example 2: Acceptance before styling
// Invalid minutes -> validation error -> zero inserted rows
// Valid plan -> stored under actor -> visible only to that actor

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Synthetic fixture for the exercises.
$db = new PDO("sqlite::memory:", null, null, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
$db->exec(
  "CREATE TABLE plans (id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL, topic TEXT NOT NULL, minutes INTEGER NOT NULL CHECK(minutes BETWEEN 5 AND 120))",
);

// Write your implementation here and add one check() call for each case you test.

echo "web-056 attempt finished without a failed check\n";
