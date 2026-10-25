<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

function e(string $value): string
{
  return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, "UTF-8");
}
$label = "<Ada & Bea>";
$html = "<article><h2>" . e($label) . "</h2><p>Local example.</p></article>";
check(str_contains($html, "&lt;Ada &amp; Bea&gt;"), "Text not escaped");
check(!str_contains($html, "<Ada"), "Untrusted tag remained");
check(e('"') === "&quot;", "Quote escaping failed");
echo $html . "\n";

echo "web-045 reference checks passed\n";
