<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

interface ProgressStore
{
  public function completedCount(): int;
}
final class MemoryProgress implements ProgressStore
{
  public function __construct(private array $completed) {}
  public function completedCount(): int
  {
    return count($this->completed);
  }
}
final class Summary
{
  public function __construct(private ProgressStore $store) {}
  public function label(): string
  {
    return $this->store->completedCount() . " complete";
  }
}
check(new Summary(new MemoryProgress([]))->label() === "0 complete", "Empty summary failed");
$summary = new Summary(new MemoryProgress(["web-001", "web-002"]));
check($summary->label() === "2 complete", "Summary failed");
echo $summary->label() . "\n";

echo "web-041 reference checks passed\n";
