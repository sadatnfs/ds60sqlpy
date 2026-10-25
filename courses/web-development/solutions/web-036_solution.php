<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

function totalMinutes(array $values): int
{
  $total = 0;
  foreach ($values as $value) {
    if (!is_int($value) || $value < 0 || $value > 1440) {
      throw new InvalidArgumentException("Invalid duration");
    }
    $total += $value;
  }
  return $total;
}
check(totalMinutes([]) === 0, "Empty total failed");
check(totalMinutes([20, 30]) === 50, "Total failed");
$failed = false;
try {
  totalMinutes([-1]);
} catch (InvalidArgumentException) {
  $failed = true;
}
check($failed, "Negative duration accepted");
echo "Total: " . totalMinutes([20, 30]) . "\n";

echo "web-036 reference checks passed\n";
