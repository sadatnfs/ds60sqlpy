<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

$record = ['minutes' => 0, 'note' => null];
check($record['minutes'] === 0, 'Zero was lost');
check(array_key_exists('note', $record), 'Null key should exist');
check(!isset($record['note']), 'isset treats null as unset');
check('0' !== 0, 'Types must differ');
echo get_debug_type($record['minutes']) . "\n";
echo ($record['note'] ?? 'No note') . "\n";

echo "web-032 reference checks passed\n";
