<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

$durations = [20, 30, 15];
$total = 0;
foreach ($durations as $minutes) {
  if ($minutes < 0) {
    throw new InvalidArgumentException("Negative duration");
  }
  $total += $minutes;
}
$label = match (true) {
  $total >= 60 => "Weekly target met",
  default => "Keep a flexible pace",
};
check($total === 65, "Wrong accumulated duration");
echo $label . ": " . $total . " minutes\n";

echo "web-034 reference checks passed\n";
