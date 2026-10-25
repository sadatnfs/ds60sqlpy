<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

$raw = '{"minutes":30,"topic":"HTML"}';
if (strlen($raw) > 1024) { throw new InvalidArgumentException('Input too large'); }
$data = json_decode($raw, true, 32, JSON_THROW_ON_ERROR);
check(is_array($data) && is_int($data['minutes'] ?? null), 'Invalid record');
$stream = fopen('php://temp', 'w+');
if ($stream === false) { throw new RuntimeException('Cannot create temporary stream'); }
try {
    check(fwrite($stream, $raw) === strlen($raw), 'Incomplete write');
    rewind($stream);
    check(stream_get_contents($stream) === $raw, 'Stream round trip failed');
} finally { fclose($stream); }
echo 'Validated local record for ' . $data['topic'] . "\n";

echo "web-038 reference checks passed\n";
