<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

$rows = [['subject' => 'HTML', 'minutes' => 40], ['subject' => 'PHP', 'minutes' => 20]];
$visible = array_values(array_filter($rows, fn(array $row): bool => $row['minutes'] >= 30));
check(count($visible) === 1, 'Filter failed');
check(array_is_list($visible), 'Expected list shape');
check(count($rows) === 2, 'Original records changed');
echo json_encode($visible, JSON_THROW_ON_ERROR) . "\n";

echo "web-035 reference checks passed\n";
