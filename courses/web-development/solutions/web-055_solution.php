<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

function pageAfter(array $rows, int $after, int $size): array
{
    if ($size < 1 || $size > 3 || $after < 0) { throw new InvalidArgumentException('Invalid page request'); }
    $visible = array_values(array_filter($rows, fn(array $row): bool => $row['id'] > $after));
    return array_slice($visible, 0, $size);
}
$rows = [['id' => 1], ['id' => 2], ['id' => 3], ['id' => 4]];
$first = pageAfter($rows, 0, 2);
$second = pageAfter($rows, $first[1]['id'], 2);
check(array_column($first, 'id') === [1, 2], 'First page failed');
check(array_column($second, 'id') === [3, 4], 'Second page failed');
check(pageAfter($rows, 4, 2) === [], 'Empty page failed');
echo json_encode([$first, $second], JSON_THROW_ON_ERROR) . "\n";

echo "web-055 reference checks passed\n";
