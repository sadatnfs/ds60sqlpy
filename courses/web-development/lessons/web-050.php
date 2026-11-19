<?php

declare(strict_types=1);

// web-050: Password hashing and authentication boundaries
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Explain hashing versus reversible encryption for passwords.
// 2. Verify both a correct and incorrect synthetic phrase.
// 3. Build a password-verification demonstration without printing the hash or secret.
// 4. Diagnose using a general fast hash such as SHA-256 for password storage.
// 5. Explain an algorithm-specific input-length boundary and a hash that needs an upgrade.
// 6. List the additional controls required around a real login.
//
// Worked example 1: Hash and verify
// $options = ['memory_cost' => 19456, 'time_cost' => 2, 'threads' => 1];
// $hash = password_hash('synthetic-demo-passphrase', PASSWORD_ARGON2ID, $options);
// $valid = password_verify('synthetic-demo-passphrase', $hash);
// $upgrade = password_needs_rehash($hash, PASSWORD_ARGON2ID, $options);
//
// Worked example 2: A wrong candidate
// $wrong = password_verify('different-phrase', $hash);

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-050 attempt finished without a failed check\n";
