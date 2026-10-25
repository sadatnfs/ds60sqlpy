<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

$db = new PDO("sqlite::memory:", null, null, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
$db->exec("CREATE TABLE notes (id INTEGER PRIMARY KEY, title TEXT NOT NULL)");
$title = "Ada's notes; DROP TABLE notes;";
$insert = $db->prepare("INSERT INTO notes (title) VALUES (:title)");
$insert->execute(["title" => $title]);
$select = $db->prepare("SELECT title FROM notes WHERE id = :id");
$select->execute(["id" => 1]);
check($select->fetchColumn() === $title, "Value did not round trip");
check(
  (int) $db->query("SELECT COUNT(*) FROM notes")->fetchColumn() === 1,
  "Table changed unexpectedly",
);
echo "Prepared value round trip passed in disposable SQLite memory.\n";

echo "web-051 reference checks passed\n";
