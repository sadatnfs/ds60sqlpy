<?php

declare(strict_types=1);

// web-055: Pagination, caching and bounded application workloads
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Explain why pagination needs an explicit stable order.
// 2. Add a maximum page-size rule.
// 3. Implement a cursor-based slice over synthetic records.
// 4. Diagnose a cache key shared by all authenticated users.
// 5. Test an empty page and an invalid page size.
// 6. Explain what must be measured before claiming a faster database endpoint.
//
// Worked example 1: A stable cursor predicate
// SELECT
//   id,
//   title
// FROM
//   notes
// WHERE
//   owner_id = :actor
//   AND id > :after_id
// ORDER BY
//   id ASC
// LIMIT :page_size;
//
// Worked example 2: A scoped cache key
// $key = 'notes:user:' . $actorId . ':version:' . $version;

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Synthetic fixture for the exercises.
$rows = [["id" => 1], ["id" => 2], ["id" => 3], ["id" => 4]];

// Write your implementation here and add one check() call for each case you test.

echo "web-055 attempt finished without a failed check\n";
