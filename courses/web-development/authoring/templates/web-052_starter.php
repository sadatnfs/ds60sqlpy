<?php

declare(strict_types=1);

// web-052: Transactions, constraints and concurrent changes
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Explain atomicity without claiming every transaction is serializable.
// 2. Add a database constraint for nonnegative minutes.
// 3. Implement a version-checked update in a disposable database.
// 4. Diagnose accepting a zero-row update as success.
// 5. Force a failure after a write and verify rollback.
// 6. Explain the limits of the single-connection concurrency demonstration.
//
// Worked example 1: A guarded update
// UPDATE
//   plans
// SET
//   minutes = :minutes,
//   version = version + 1
// WHERE
//   id = :id
//   AND version = :expected_version;
//
// Worked example 2: Rollback ownership
// $db->beginTransaction();
// try { /* related writes */ $db->commit(); }
// catch (Throwable $error) { if ($db->inTransaction()) $db->rollBack(); throw $error; }

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Synthetic fixture for the exercises.
$db = new PDO("sqlite::memory:", null, null, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
$db->exec(
  "CREATE TABLE plans (id INTEGER PRIMARY KEY, minutes INTEGER NOT NULL, version INTEGER NOT NULL)",
);
$db->exec("INSERT INTO plans VALUES (1, 30, 1)");

// Write your implementation here and add one check() call for each case you test.

echo "web-052 attempt finished without a failed check\n";
