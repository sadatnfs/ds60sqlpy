<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

function totalCents(int $unitCents, int $quantity): int
{
  if ($unitCents < 0 || $unitCents > 100000 || $quantity < 0 || $quantity > 1000) {
    throw new InvalidArgumentException("Values outside teaching limits");
  }
  return $unitCents * $quantity;
}
$total = totalCents(125, 3);
check($total === 375, "Wrong total");
check(totalCents(125, 0) === 0, "Zero quantity failed");
echo intdiv($total, 100) . "." . str_pad((string) ($total % 100), 2, "0", STR_PAD_LEFT) . "\n";

echo "web-033 reference checks passed\n";
