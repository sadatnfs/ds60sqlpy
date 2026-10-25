<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

$phrase = 'synthetic-demo-passphrase';
$hash = password_hash($phrase, PASSWORD_BCRYPT, ['cost' => 10]);
check(password_verify($phrase, $hash), 'Correct phrase rejected');
check(!password_verify('different-phrase', $hash), 'Wrong phrase accepted');
check(!password_needs_rehash($hash, PASSWORD_BCRYPT, ['cost' => 10]), 'Unexpected parameters');
echo "Correct and incorrect synthetic candidates checked. No credentials were logged.\n";

echo "web-050 reference checks passed\n";
