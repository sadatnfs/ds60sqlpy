<?php

declare(strict_types=1);

// web-053: Authorization, ownership and object-level access
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Explain why knowing a record id is not sufficient permission.
// 2. Add owner scoping to a prepared read query.
// 3. Build an object-access function with separate trusted actor and requested id inputs.
// 4. Diagnose trusting owner_id from a submitted form.
// 5. Test own, other and missing records.
// 6. Explain why hiding an edit button is only a user-interface convenience.
//
// Worked example 1: Scope a read
// SELECT
//   title
// FROM
//   notes
// WHERE
//   id = :id
//   AND owner_id = :actor_id;
//
// Worked example 2: Separate input roles
// $title = loadOwnedNote($db, $trustedActorId, $requestedNoteId);

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Synthetic fixture for the exercises.
$db = new PDO("sqlite::memory:", null, null, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
$db->exec(
  "CREATE TABLE notes (id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL, title TEXT NOT NULL)",
);
$db->exec("INSERT INTO notes VALUES (1, 7, 'Private synthetic note')");

// Write your implementation here and add one check() call for each case you test.

echo "web-053 attempt finished without a failed check\n";
