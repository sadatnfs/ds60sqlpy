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
  "CREATE TABLE plans (id INTEGER PRIMARY KEY, minutes INTEGER NOT NULL CHECK(minutes >= 0), version INTEGER NOT NULL)",
);
$db->exec("INSERT INTO plans VALUES (1, 30, 1)");
$update = $db->prepare(
  "UPDATE plans SET minutes = :minutes, version = version + 1 WHERE id = :id AND version = :version",
);
$update->execute(["minutes" => 40, "id" => 1, "version" => 1]);
check($update->rowCount() === 1, "Initial update failed");
$update->execute(["minutes" => 50, "id" => 1, "version" => 1]);
check($update->rowCount() === 0, "Stale update accepted");
$db->beginTransaction();
$db->exec("UPDATE plans SET minutes = 99 WHERE id = 1");
$db->rollBack();
check(
  (int) $db->query("SELECT minutes FROM plans WHERE id = 1")->fetchColumn() === 40,
  "Rollback failed",
);
echo "Version conflict and rollback checked in one SQLite connection.\n";

echo "web-052 reference checks passed\n";
