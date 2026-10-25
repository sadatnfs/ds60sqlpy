<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

function validatePlan(array $input): array
{
    $errors = [];
    $topic = $input['topic'] ?? null;
    $minutes = $input['minutes'] ?? null;
    if (!is_string($topic) || !in_array($topic, ['HTML', 'CSS', 'PHP'], true)) { $errors['topic'] = 'Choose HTML, CSS or PHP.'; }
    if (!is_string($minutes) || preg_match('/^[0-9]{1,3}$/D', $minutes) !== 1 || (int) $minutes < 5 || (int) $minutes > 120) { $errors['minutes'] = 'Use 5 to 120 whole minutes.'; }
    return ['value' => $errors ? null : ['topic' => $topic, 'minutes' => (int) $minutes], 'errors' => $errors];
}
check(validatePlan(['topic' => 'HTML', 'minutes' => '30'])['value']['minutes'] === 30, 'Valid plan failed');
check(validatePlan(['topic' => ['HTML'], 'minutes' => '30'])['value'] === null, 'Array input accepted');
check(validatePlan([])['value'] === null, 'Missing input accepted');
echo json_encode(validatePlan(['topic' => 'CSS', 'minutes' => '121']), JSON_THROW_ON_ERROR) . "\n";

echo "web-047 reference checks passed\n";
