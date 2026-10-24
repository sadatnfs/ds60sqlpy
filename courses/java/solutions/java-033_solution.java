import java.util.*;

public class Main {

  @FunctionalInterface
  interface RootWork {
    void run(java.nio.file.Path root) throws Exception;
  }

  static void withRoot(RootWork work) throws Exception {
    var root = java.nio.file.Files.createTempDirectory("ds60-boundary-").toRealPath();
    try {
      work.run(root);
    } finally {
      try (var paths = java.nio.file.Files.walk(root)) {
        for (var path : paths.sorted(Comparator.reverseOrder()).toList())
          java.nio.file.Files.deleteIfExists(path);
      }
    }
  }

  static byte[] readBounded(java.nio.file.Path root, String relative, int limit)
    throws java.io.IOException {
    if (limit < 0 || limit > 1024) throw new IllegalArgumentException("byte limit0..1024 required");
    var supplied = java.nio.file.Path.of(relative);
    if (supplied.isAbsolute()) throw new SecurityException("relative path required");
    var candidate = root.resolve(supplied).normalize();
    if (!candidate.startsWith(root)) throw new SecurityException("path escape");
    var current = root;
    for (var part : root.relativize(candidate)) {
      current = current.resolve(part);
      if (java.nio.file.Files.isSymbolicLink(current)) throw new SecurityException(
        "symbolic link not allowed"
      );
    }
    var real = candidate.toRealPath();
    if (!real.startsWith(root)) throw new SecurityException("real path escape");
    try (var input = java.nio.file.Files.newInputStream(real)) {
      byte[] bytes = input.readNBytes(limit + 1);
      if (bytes.length > limit) throw new java.io.IOException("byte limit exceeded");
      return bytes;
    }
  }

  public static void main(String[] args) throws Exception {
    // Exercise 1: Read an admitted owned file
    withRoot(root -> {
      java.nio.file.Files.writeString(root.resolve("input.txt"), "hello");
      assert new String(
        readBounded(root, "input.txt", 10),
        java.nio.charset.StandardCharsets.UTF_8
      ).equals("hello");
    });

    // Exercise 2: Reject lexical traversal andabsolute paths
    withRoot(root -> {
      for (String name : List.of("../outside.txt", root.resolve("input.txt").toString())) {
        boolean rejected = false;
        try {
          readBounded(root, name, 10);
        } catch (SecurityException expected) {
          rejected = true;
        }
        assert rejected;
      }
    });

    // Exercise 3: Enforce the byte limit after reading a bounded amount
    withRoot(root -> {
      java.nio.file.Files.writeString(root.resolve("large.txt"), "abcde");
      boolean rejected = false;
      try {
        readBounded(root, "large.txt", 4);
      } catch (java.io.IOException expected) {
        rejected = expected.getMessage().contains("limit");
      }
      assert rejected;
    });

    // Exercise 4: Reject symbolic-link access under the declared policy
    withRoot(root -> {
      java.nio.file.Files.writeString(root.resolve("target.txt"), "fixture");
      boolean created = false;
      try {
        java.nio.file.Files.createSymbolicLink(
          root.resolve("link.txt"),
          java.nio.file.Path.of("target.txt")
        );
        created = true;
      } catch (UnsupportedOperationException | java.io.IOException unavailable) {
        System.out.println("symbolic-link fixture unavailable on this platform");
      }
      if (created) {
        boolean rejected = false;
        try {
          readBounded(root, "link.txt", 20);
        } catch (SecurityException expected) {
          rejected = true;
        }
        assert rejected;
      }
    });

    // Exercise 5: Keep operation names out ofcode execution
    Map<String, String> operations = Map.of("read_fixture", "fixed local reader");
    assert operations.containsKey("read_fixture");
    boolean rejected = false;
    try {
      if (!operations.containsKey("run_shell")) throw new IllegalArgumentException(
        "operation not allowed"
      );
    } catch (IllegalArgumentException expected) {
      rejected = true;
    }
    assert rejected;

    // Exercise 6: Build a restricted diagnostic record
    Map<String, String> raw = Map.of(
      "request_id",
      "r1",
      "operation",
      "read_fixture",
      "status",
      "rejected",
      "token",
      "do-not-log",
      "source_text",
      "private fixture"
    );
    Map<String, String> safe = Map.of(
      "request_id",
      raw.get("request_id"),
      "operation",
      raw.get("operation"),
      "status",
      raw.get("status")
    );
    assert !safe.containsKey("token") && !safe.containsKey("source_text") && safe.size() == 3;
  }
}
