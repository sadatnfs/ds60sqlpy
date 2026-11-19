<?php

declare(strict_types=1);

// web-048: Cookies, sessions and a request-to-request lifecycle
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Explain which data is in the browser and which is on the server.
// 2. Add a fixed-clock inactivity check.
// 3. Model session activity and expiry with explicit state transitions.
// 4. Explain why a client-supplied user id is not a trusted session.
// 5. Test activity exactly at and beyond the timeout boundary.
// 6. Describe a real HTTP session acceptance test.
//
// Worked example 1: A session policy
// session_set_cookie_params(['httponly' => true, 'secure' => true, 'samesite' => 'Lax']);
// ini_set('session.use_strict_mode', '1');
//
// Worked example 2: An explicit expiry rule
// $expired = $now - $session['last_seen'] > 1800;

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-048 attempt finished without a failed check\n";
