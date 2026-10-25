<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

function boundedMinutes(int $value): int
{
  if ($value < 0 || $value > 120) {
    throw new InvalidArgumentException("Outside range");
  }
  return $value;
}
foreach ([0, 30, 120] as $value) {
  check(boundedMinutes($value) === $value, "Valid case failed");
}
foreach ([-1, 121] as $value) {
  $rejected = false;
  try {
    boundedMinutes($value);
  } catch (InvalidArgumentException) {
    $rejected = true;
  }
  check($rejected, "Invalid case accepted");
}
echo "Three valid and two invalid boundaries checked.\n";

echo "web-044 reference checks passed\n";
