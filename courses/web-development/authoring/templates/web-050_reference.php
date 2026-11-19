<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

$phrase = "synthetic-demo-passphrase";
// OWASP minimum for Argon2id: 19 MiB of memory (in KiB), 2 iterations, 1 thread.
$options = ["memory_cost" => 19456, "time_cost" => 2, "threads" => 1];
$hash = password_hash($phrase, PASSWORD_ARGON2ID, $options);
check(str_starts_with($hash, '$argon2id$'), "Expected an Argon2id encoding");
check(password_verify($phrase, $hash), "Correct phrase rejected");
check(!password_verify("different-phrase", $hash), "Wrong phrase accepted");
check(!password_needs_rehash($hash, PASSWORD_ARGON2ID, $options), "Unexpected parameters");

$legacy = password_hash($phrase, PASSWORD_BCRYPT, ["cost" => 10]);
check(password_verify($phrase, $legacy), "Legacy bcrypt hash rejected");
check(password_needs_rehash($legacy, PASSWORD_ARGON2ID, $options), "Legacy hash not flagged");
$default = password_hash($phrase, PASSWORD_DEFAULT);
check(str_starts_with($default, '$2y$12$'), "Expected the PHP 8.4 bcrypt default cost");
echo "Correct and incorrect synthetic candidates checked. No credentials were logged.\n";

echo "web-050 reference checks passed\n";
