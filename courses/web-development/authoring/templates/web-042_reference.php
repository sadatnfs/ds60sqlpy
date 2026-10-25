<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

$qualified = '\DateTimeImmutable';
$clock = new $qualified('2024-01-01T00:00:00+00:00');
check($clock instanceof DateTimeImmutable, 'Qualified class resolution failed');
$layout = ['public/index.php', 'src/StudyService.php', 'tests/StudyServiceTest.php', 'composer.json', 'composer.lock'];
check(!in_array('public/composer.lock', $layout, true), 'Dependency metadata should not be public');
echo implode("\n", $layout) . "\n";

echo "web-042 reference checks passed\n";
