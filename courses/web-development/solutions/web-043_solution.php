<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

$instant = new DateTimeImmutable('2024-01-01T12:00:00+00:00');
$local = $instant->setTimezone(new DateTimeZone('America/New_York'));
check($instant->getTimestamp() === $local->getTimestamp(), 'Zone conversion changed the instant');
check($local->format('H:i P') === '07:00 -05:00', 'Unexpected fixed-date conversion');
$later = $instant->modify('+30 minutes');
check($later->getTimestamp() - $instant->getTimestamp() === 1800, 'Duration failed');
echo $local->format('Y-m-d H:i P') . "\n";

echo "web-043 reference checks passed\n";
