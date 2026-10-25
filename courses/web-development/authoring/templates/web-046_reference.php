<?php

declare(strict_types=1);

function check(bool $condition, string $message): void
{
  if (!$condition) {
    throw new RuntimeException($message);
  }
}

function route(string $method, string $path): array
{
  if ($path !== "/health") {
    return ["status" => 404, "body" => "Not found"];
  }
  if ($method !== "GET") {
    return ["status" => 405, "headers" => ["Allow" => "GET"], "body" => "Method not allowed"];
  }
  return [
    "status" => 200,
    "headers" => ["Content-Type" => "text/plain; charset=utf-8"],
    "body" => "ok",
  ];
}
check(route("GET", "/health")["status"] === 200, "Health failed");
check(route("POST", "/health")["status"] === 405, "Wrong method accepted");
check(route("GET", "/missing")["status"] === 404, "Unknown path accepted");
echo json_encode(route("GET", "/health"), JSON_THROW_ON_ERROR) . "\n";

echo "web-046 reference checks passed\n";
