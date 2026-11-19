<?php

declare(strict_types=1);

// web-051: PDO, prepared statements and the value-query boundary
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Explain what a prepared value parameter can and cannot replace.
// 2. Insert a title containing an apostrophe.
// 3. Build a local PDO note store with prepared insert and lookup.
// 4. Diagnose concatenating an untrusted sort key into SQL.
// 5. Test an empty result and an attack-shaped title.
// 6. Explain which checks must be repeated when moving to PostgreSQL.
//
// Worked example 1: A value parameter
// $stmt = $db->prepare('INSERT INTO notes (title) VALUES (:title)');
// $stmt->execute(['title' => "Ada's notes"]);
//
// Worked example 2: An allowlisted identifier
// $columns = ['title' => 'title', 'created' => 'id'];
// $orderBy = $columns[$requested] ?? 'id';

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Synthetic fixture for the exercises.
$db = new PDO("sqlite::memory:", null, null, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
$db->exec("CREATE TABLE notes (id INTEGER PRIMARY KEY, title TEXT NOT NULL)");

// Write your implementation here and add one check() call for each case you test.

echo "web-051 attempt finished without a failed check\n";
