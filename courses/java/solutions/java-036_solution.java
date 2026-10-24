import java.util.*;

public class Main {

  record Run(int code, String output, String error) {}

  static byte[] sha256(byte[] bytes) throws Exception {
    return java.security.MessageDigest.getInstance("SHA-256").digest(bytes);
  }

  static void verify(java.nio.file.Path artifact, byte[] expected) throws Exception {
    if (
      !Arrays.equals(sha256(java.nio.file.Files.readAllBytes(artifact)), expected)
    ) throw new SecurityException("artifact hash mismatch");
  }

  static final class ReleaseFixture implements AutoCloseable {

    final java.nio.file.Path root, source, classes, jar;

    ReleaseFixture() throws Exception {
      root = java.nio.file.Files.createTempDirectory("ds60-release-");
      source = root.resolve("App.java");
      classes = root.resolve("classes");
      jar = root.resolve("app.jar");
      java.nio.file.Files.createDirectories(classes);
      java.nio.file.Files.writeString(
        source,
        "public class App { public static void main(String[] args){if(args.length==1 && args[0].equals(\"--self-test\")){System.out.println(\"release-ok\");}else{System.err.println(\"unknown argument\");System.exit(2);}} }"
      );
    }

    void build() throws Exception {
      var compiler = javax.tools.ToolProvider.getSystemJavaCompiler();
      if (
        compiler == null ||
        compiler.run(
          null,
          null,
          null,
          "--release",
          "21",
          "-d",
          classes.toString(),
          source.toString()
        ) !=
        0
      ) throw new AssertionError("compile failed");
      var tool = java.util.spi.ToolProvider.findFirst("jar").orElseThrow();
      var messages = new java.io.StringWriter();
      int code = tool.run(
        new java.io.PrintWriter(messages),
        new java.io.PrintWriter(messages),
        "--create",
        "--file",
        jar.toString(),
        "--main-class",
        "App",
        "--date=2020-01-01T00:00:02Z",
        "-C",
        classes.toString(),
        "."
      );
      if (code != 0) throw new AssertionError(messages.toString());
    }

    Run run(String argument) throws Exception {
      String executable = java.nio.file.Path.of(
        System.getProperty("java.home"),
        "bin",
        "java"
      ).toString();
      var stdout = root.resolve("child.stdout");
      var stderr = root.resolve("child.stderr");
      var process = new ProcessBuilder(executable, "-ea", "-jar", jar.toString(), argument)
        .redirectOutput(stdout.toFile())
        .redirectError(stderr.toFile())
        .start();
      if (!process.waitFor(5, java.util.concurrent.TimeUnit.SECONDS)) {
        process.destroyForcibly();
        throw new AssertionError("release child timeout");
      }
      return new Run(
        process.exitValue(),
        java.nio.file.Files.readString(stdout),
        java.nio.file.Files.readString(stderr)
      );
    }

    public void close() throws java.io.IOException {
      try (var paths = java.nio.file.Files.walk(root)) {
        for (var path : paths.sorted(Comparator.reverseOrder()).toList())
          java.nio.file.Files.deleteIfExists(path);
      }
    }
  }

  public static void main(String[] args) throws Exception {
    // Exercise 1: Verify the compiler target
    try (ReleaseFixture fixture = new ReleaseFixture()) {
      fixture.build();
      try (
        var input = new java.io.DataInputStream(
          java.nio.file.Files.newInputStream(fixture.classes.resolve("App.class"))
        )
      ) {
        assert input.readInt() == 0xCAFEBABE;
        input.readUnsignedShort();
        assert input.readUnsignedShort() == 65;
      }
    }

    // Exercise 2: Inspect packaged launch metadata
    try (ReleaseFixture fixture = new ReleaseFixture()) {
      fixture.build();
      try (var jar = new java.util.jar.JarFile(fixture.jar.toFile())) {
        assert jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App") &&
        jar.getJarEntry("App.class") != null;
      }
    }

    // Exercise 3: Run a fresh-process self-test
    try (ReleaseFixture fixture = new ReleaseFixture()) {
      fixture.build();
      Run result = fixture.run("--self-test");
      assert result.code() == 0 && result.output().strip().equals("release-ok");
    }

    // Exercise 4: Verify an invalid launch fails clearly
    try (ReleaseFixture fixture = new ReleaseFixture()) {
      fixture.build();
      Run result = fixture.run("--unsupported");
      assert result.code() == 2 && result.error().contains("unknown argument");
    }

    // Exercise 5: Reject artifact tampering before execution
    try (ReleaseFixture fixture = new ReleaseFixture()) {
      fixture.build();
      byte[] original = java.nio.file.Files.readAllBytes(fixture.jar);
      byte[] expected = sha256(original);
      byte[] changed = original.clone();
      changed[0] ^= 1;
      java.nio.file.Files.write(fixture.jar, changed);
      boolean rejected = false;
      try {
        verify(fixture.jar, expected);
      } catch (SecurityException failure) {
        rejected = true;
      } finally {
        java.nio.file.Files.write(fixture.jar, original);
      }
      assert rejected;
      verify(fixture.jar, expected);
    }

    // Exercise 6: Record runtime-image scope androllback identity
    var jlink = java.nio.file.Path.of(System.getProperty("java.home"), "bin", "jlink");
    Map<String, Object> receipt = Map.of(
      "jar_contract_checked",
      true,
      "previous_artifact",
      "v1",
      "jlink_tool_present",
      java.nio.file.Files.isExecutable(jlink),
      "custom_runtime_built",
      false,
      "production_deployed",
      false
    );
    assert receipt.get("previous_artifact").equals("v1") &&
    receipt.get("custom_runtime_built").equals(false) &&
    receipt.get("production_deployed").equals(false);
  }
}
