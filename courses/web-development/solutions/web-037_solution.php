<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

$label = 'café';
check(strlen($label) === 5, 'Expected UTF-8 byte count');
check(preg_match('//u', $label) === 1, 'Expected valid UTF-8');
$json = json_encode(['label' => $label, 'bytes' => strlen($label)], JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE);
$decoded = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
check($decoded['label'] === $label, 'Unicode round trip failed');
echo $json . "\n";

echo "web-037 reference checks passed\n";
