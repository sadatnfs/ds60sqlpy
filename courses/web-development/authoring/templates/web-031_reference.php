<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

$topic = "HTML and PHP";
$minutes = 20 + 10;
check($minutes === 30, "Duration calculation failed");
echo "Topic: " . $topic . "\n";
echo "Planned minutes: " . $minutes . "\n";

echo "web-031 reference checks passed\n";
