<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

$db = new PDO("sqlite::memory:", null, null, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
$db->exec(
  "CREATE TABLE notes (id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL, title TEXT NOT NULL)",
);
$db->exec("INSERT INTO notes VALUES (1, 7, 'Private synthetic note')");
function loadOwnedNote(PDO $db, int $actorId, int $noteId): ?string
{
  $query = $db->prepare("SELECT title FROM notes WHERE id = :id AND owner_id = :owner");
  $query->execute(["id" => $noteId, "owner" => $actorId]);
  $value = $query->fetchColumn();
  return $value === false ? null : $value;
}
check(loadOwnedNote($db, 7, 1) === "Private synthetic note", "Owner read failed");
check(loadOwnedNote($db, 8, 1) === null, "Cross-owner data leak");
check(loadOwnedNote($db, 7, 999) === null, "Missing record handling failed");
echo "Own, other and missing access cases checked.\n";

echo "web-053 reference checks passed\n";
