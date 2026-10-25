<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

function touchSession(array $session, int $now): ?array
{
  if (
    !isset($session["user_id"], $session["last_seen"]) ||
    !is_int($session["last_seen"]) ||
    $now < $session["last_seen"] ||
    $now - $session["last_seen"] > 1800
  ) {
    return null;
  }
  $session["last_seen"] = $now;
  return $session;
}
$session = ["user_id" => 7, "last_seen" => 1000];
check(touchSession($session, 2800) !== null, "Declared timeout boundary failed");
check(touchSession($session, 2801) === null, "Expired session accepted");
check(touchSession($session, 999) === null, "Backward clock accepted");
echo "Pure expiry transitions checked; no HTTP session was created.\n";

echo "web-048 reference checks passed\n";
