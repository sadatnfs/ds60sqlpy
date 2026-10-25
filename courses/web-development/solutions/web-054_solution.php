<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

function jsonResponse(int $status, array $body): array
{
    return ['status' => $status, 'headers' => ['Content-Type' => 'application/json'], 'body' => json_encode($body, JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE)];
}
$response = jsonResponse(200, ['topic' => 'café', 'minutes' => 30, 'complete' => false]);
$decoded = json_decode($response['body'], true, 32, JSON_THROW_ON_ERROR);
check(is_int($decoded['minutes']) && is_bool($decoded['complete']), 'JSON type contract failed');
$error = jsonResponse(422, ['error' => ['code' => 'invalid_plan', 'fields' => ['minutes' => 'Use 5 to 120 minutes.']]]);
check($error['status'] === 422, 'Validation status failed');
echo $response['body'] . "\n";
echo $error['body'] . "\n";

echo "web-054 reference checks passed\n";
