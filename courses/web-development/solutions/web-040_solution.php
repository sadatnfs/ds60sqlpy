<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

final class StudySession
{
    public function __construct(public readonly string $topic, public readonly int $minutes)
    {
        if (trim($topic) === '' || $minutes < 0) { throw new InvalidArgumentException('Invalid session'); }
    }
    public function label(): string { return $this->topic . ': ' . $this->minutes . ' minutes'; }
}
$session = new StudySession('CSS', 45);
check($session->label() === 'CSS: 45 minutes', 'Label failed');
$failed = false;
try { new StudySession('', 10); } catch (InvalidArgumentException) { $failed = true; }
check($failed, 'Empty topic accepted');
echo $session->label() . "\n";

echo "web-040 reference checks passed\n";
