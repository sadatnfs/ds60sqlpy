<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

function requirePositive(int $value): int
{
    if ($value <= 0) { throw new InvalidArgumentException('Use a positive value'); }
    return $value;
}
$cleaned = false;
$caught = false;
try { requirePositive(0); } catch (InvalidArgumentException $error) {
    $caught = true;
    echo $error->getMessage() . "\n";
} finally { $cleaned = true; }
check($caught && $cleaned, 'Failure boundary or cleanup failed');
check(requirePositive(3) === 3, 'Valid value rejected');

echo "web-039 reference checks passed\n";
