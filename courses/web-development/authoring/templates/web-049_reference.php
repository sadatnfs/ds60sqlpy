<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

function validCsrf(mixed $submitted, string $expected): bool
{
    return $expected !== '' && is_string($submitted) && $submitted !== '' && hash_equals($expected, $submitted);
}
$fakeSessionToken = str_repeat('a', 64);
check(validCsrf($fakeSessionToken, $fakeSessionToken), 'Matching fixture rejected');
check(!validCsrf(str_repeat('b', 64), $fakeSessionToken), 'Wrong fixture accepted');
check(!validCsrf([], $fakeSessionToken), 'Array token accepted');
check(!validCsrf('', ''), 'Empty token accepted');
echo "Synthetic CSRF comparison cases checked; use random_bytes for real tokens.\n";

echo "web-049 reference checks passed\n";
