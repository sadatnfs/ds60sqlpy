<?php

declare(strict_types=1);

// web-049: CSRF defenses and deliberate state-changing requests
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Explain why a hidden form field alone does not prevent CSRF.
// 2. Add wrong-type and missing-token rejection.
// 3. Build a state-change decision that checks method, token and authorization.
// 4. Diagnose a token placed in a URL.
// 5. Test mismatched, empty and matching synthetic tokens.
// 6. Explain the relationship between CSRF, SameSite and XSS.
//
// Worked example 1: Production token generation
// $token = bin2hex(random_bytes(32));
//
// Worked example 2: Comparison at the boundary
// $valid = is_string($submitted) && hash_equals($sessionToken, $submitted);

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-049 attempt finished without a failed check\n";
