<?php

declare(strict_types=1);

// web-046: HTTP requests, response models and routing
// Exercises. Hints are in the guide; answers are in the solutions folder.
// 1. Identify status, headers and body in the response model.
// 2. Add a not-found response for an unknown path.
// 3. Build a pure router for health and lesson-summary requests.
// 4. Diagnose headers sent after body output in a real adapter.
// 5. Test a known path with the wrong method.
// 6. Explain what a CLI response model does not prove.
//
// Worked example 1: A response value
// $response = ['status' => 200, 'headers' => ['Content-Type' => 'text/plain; charset=utf-8'], 'body' => 'Ready'];
//
// Worked example 2: Method-aware routing
// if ($path === '/health' && $method === 'GET') { return ['status' => 200, 'body' => 'ok']; }

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

// Write your implementation here and add one check() call for each case you test.

echo "web-046 attempt finished without a failed check\n";
