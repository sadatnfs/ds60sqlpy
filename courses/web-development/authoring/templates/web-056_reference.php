<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

$db = new PDO('sqlite::memory:', null, null, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
$db->exec('CREATE TABLE plans (id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL, topic TEXT NOT NULL, minutes INTEGER NOT NULL CHECK(minutes BETWEEN 5 AND 120))');
function createPlan(PDO $db, int $actorId, array $input): int
{
    $topic = $input['topic'] ?? null; $minutes = $input['minutes'] ?? null;
    if ($actorId < 1 || !is_string($topic) || !in_array($topic, ['HTML', 'CSS', 'PHP'], true) || !is_int($minutes) || $minutes < 5 || $minutes > 120) { throw new InvalidArgumentException('Invalid plan'); }
    $insert = $db->prepare('INSERT INTO plans (owner_id, topic, minutes) VALUES (:owner, :topic, :minutes)');
    $insert->execute(['owner' => $actorId, 'topic' => $topic, 'minutes' => $minutes]);
    return (int) $db->lastInsertId();
}
$id = createPlan($db, 7, ['topic' => 'PHP', 'minutes' => 30]);
$failed = false;
try { createPlan($db, 7, ['topic' => 'PHP', 'minutes' => 121]); } catch (InvalidArgumentException) { $failed = true; }
check($failed, 'Invalid plan accepted');
check((int) $db->query('SELECT COUNT(*) FROM plans')->fetchColumn() === 1, 'Rejected input wrote data');
$query = $db->prepare('SELECT topic FROM plans WHERE id = :id AND owner_id = :owner');
$query->execute(['id' => $id, 'owner' => 8]);
check($query->fetchColumn() === false, 'Cross-owner read exposed data');
echo "Planner core checked. HTTP integration remains separate.\n";

echo "web-056 reference checks passed\n";
