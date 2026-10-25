<?php

declare(strict_types=1);

// A loopback-only learning server, not a production login service.
header("X-Content-Type-Options: nosniff");
header(
  "Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
);
header("Cache-Control: no-store");

function escapeHtml(string $value): string
{
  return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, "UTF-8");
}

function stopRequest(int $status, string $message): never
{
  http_response_code($status);
  header("Content-Type: text/plain; charset=utf-8");
  echo $message . "\n";
  exit();
}

set_exception_handler(function (Throwable $error): void {
  error_log("Web study lab failure: " . get_class($error));
  stopRequest(
    500,
    "The local lab could not complete this request. Inspect its owned container logs.",
  );
});

$host = $_SERVER["HTTP_HOST"] ?? "";
if (
  !in_array($host, ["127.0.0.1:18088", "localhost:18088", "127.0.0.1:8080", "localhost:8080"], true)
) {
  stopRequest(400, "Unexpected Host header. Use the documented loopback address.");
}
$method = $_SERVER["REQUEST_METHOD"] ?? "";
$path = parse_url($_SERVER["REQUEST_URI"] ?? "/", PHP_URL_PATH);
if ($path === "/health") {
  if ($method !== "GET") {
    header("Allow: GET");
    stopRequest(405, "Method not allowed.");
  }
  stopRequest(200, "ds60 web study lab ready");
}
if (!in_array($path, ["/", "/notes"], true)) {
  stopRequest(404, "Not found.");
}
if (($path === "/" && $method !== "GET") || ($path === "/notes" && $method !== "POST")) {
  header("Allow: " . ($path === "/" ? "GET" : "POST"));
  stopRequest(405, "Method not allowed.");
}

$dataRoot = getenv("WEB_LAB_DATA") ?: "/data";
if (
  !is_dir($dataRoot . "/sessions") &&
  !mkdir($dataRoot . "/sessions", 0700, true) &&
  !is_dir($dataRoot . "/sessions")
) {
  throw new RuntimeException("Cannot prepare session storage");
}
ini_set("session.use_strict_mode", "1");
ini_set("session.use_only_cookies", "1");
ini_set("session.use_trans_sid", "0");
session_save_path($dataRoot . "/sessions");
session_name("DS60_WEB_STUDY");
session_set_cookie_params([
  "httponly" => true,
  // This fixture uses host loopback HTTP only. A real HTTPS deployment needs Secure.
  "secure" => false,
  "samesite" => "Lax",
  "path" => "/",
]);
if (!session_start()) {
  throw new RuntimeException("Cannot start session");
}
if (!isset($_SESSION["owner"], $_SESSION["csrf"])) {
  $_SESSION["owner"] = bin2hex(random_bytes(32));
  $_SESSION["csrf"] = bin2hex(random_bytes(32));
}
$owner = $_SESSION["owner"];
$csrf = $_SESSION["csrf"];
if (!is_string($owner) || !is_string($csrf)) {
  throw new RuntimeException("Invalid stored session");
}
session_write_close();

$db = new PDO("sqlite:" . $dataRoot . "/notes.sqlite", null, null, [
  PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);
$db->exec("PRAGMA busy_timeout = 3000");
$db->exec(
  "CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, owner TEXT NOT NULL, body TEXT NOT NULL CHECK(length(body) BETWEEN 1 AND 500))",
);
$errors = [];
$draft = "";
if ($method === "POST") {
  $length = $_SERVER["CONTENT_LENGTH"] ?? "0";
  if (!ctype_digit($length) || (int) $length > 4096) {
    stopRequest(413, "Request body exceeds the local teaching limit.");
  }
  $origin = $_SERVER["HTTP_ORIGIN"] ?? null;
  if (
    $origin !== null &&
    !in_array($origin, ["http://127.0.0.1:18088", "http://localhost:18088"], true)
  ) {
    stopRequest(403, "Unexpected request origin.");
  }
  $submittedToken = $_POST["csrf"] ?? null;
  if (!is_string($submittedToken) || !hash_equals($csrf, $submittedToken)) {
    stopRequest(403, "CSRF check failed. Reload the local form and try again.");
  }
  $body = $_POST["body"] ?? null;
  if (!is_string($body)) {
    $errors[] = "Enter a text note.";
  } else {
    $draft = trim($body);
    if ($draft === "" || strlen($draft) > 500 || preg_match("//u", $draft) !== 1) {
      $errors[] = "Use 1 to 500 UTF-8 bytes of note text.";
    }
  }
  $count = $db->prepare("SELECT COUNT(*) FROM notes WHERE owner = :owner");
  $count->execute(["owner" => $owner]);
  if ((int) $count->fetchColumn() >= 100) {
    $errors[] = "This session has reached the 100-note teaching limit.";
  }
  if (!$errors) {
    $insert = $db->prepare("INSERT INTO notes (owner, body) VALUES (:owner, :body)");
    $insert->execute(["owner" => $owner, "body" => $draft]);
    header("Location: /", true, 303);
    exit();
  }
  http_response_code(422);
}
$query = $db->prepare("SELECT id, body FROM notes WHERE owner = :owner ORDER BY id DESC LIMIT 100");
$query->execute(["owner" => $owner]);
$notes = $query->fetchAll(PDO::FETCH_ASSOC);
header("Content-Type: text/html; charset=utf-8");
?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Local web study notes</title>
  <style>
    :root { font: 1rem/1.6 system-ui, sans-serif; color: #172033; background: #f8fafc; }
    body { margin: 0; padding: 1.5rem; }
    main { max-width: 45rem; margin-inline: auto; }
    textarea { display: block; box-sizing: border-box; width: 100%; min-height: 8rem; font: inherit; }
    button { font: inherit; padding: .6rem 1rem; margin-block: 1rem; }
    :focus-visible { outline: 3px solid #a34000; outline-offset: 3px; }
    .error { padding: 1rem; border: 2px solid #9c2300; }
    li { overflow-wrap: anywhere; margin-block: .7rem; }
  </style>
</head>
<body>
<main>
  <h1>Local web study notes</h1>
  <p>Anonymous session-owned synthetic notes. This lab has no verified user accounts.</p>
  <?php if ($errors): ?>
    <section class="error" aria-labelledby="error-title">
      <h2 id="error-title">Please correct the note</h2>
      <ul><?php foreach ($errors as $error): ?><li><?= escapeHtml(
  $error,
) ?></li><?php endforeach; ?></ul>
    </section>
  <?php endif; ?>
  <form action="/notes" method="post">
    <input type="hidden" name="csrf" value="<?= escapeHtml($csrf) ?>">
    <label for="body">Study note, 1 to 500 UTF-8 bytes</label>
    <textarea id="body" name="body" required aria-describedby="body-help"<?= $errors
      ? ' aria-invalid="true"'
      : "" ?>><?= escapeHtml($draft) ?></textarea>
    <p id="body-help">Use synthetic learning notes only. The server checks the byte limit and preserves invalid text for correction.</p>
    <button type="submit">Save local note</button>
  </form>
  <section aria-labelledby="notes-title">
    <h2 id="notes-title">This session's notes</h2>
    <?php if (!$notes): ?><p>No notes yet.</p><?php else: ?>
      <ol><?php foreach ($notes as $note): ?><li><?= escapeHtml(
  $note["body"],
) ?></li><?php endforeach; ?></ol>
    <?php endif; ?>
  </section>
</main>
</body>
</html>
