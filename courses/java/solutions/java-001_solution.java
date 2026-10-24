import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Print a first result
    String message = "Hello, Java";
    System.out.println(message);
    assert message.equals("Hello, Java");

    // Exercise 2: Evaluate before printing
    int total = 2 + 3;
    String line = "total=" + total;
    assert total == 5;
    assert line.equals("total=5");

    // Exercise 3: Trace sequential state
    int count = 1;
    count = count + 1;
    count = count * 3;
    assert count == 6;

    // Exercise 4: Verify assertion mode
    boolean enabled = false;
    assert enabled = true;
    if (!enabled) throw new IllegalStateException("Run with -ea");
    assert enabled;

    // Exercise 5: Separate runtime failure
    boolean dividedByZero = false;
    try {
      int zero = 0;
      int ignored = 10 / zero;
    } catch (ArithmeticException expected) {
      dividedByZero = true;
    }
    assert dividedByZero;

    // Exercise 6: Observe a real compiler diagnostic
    var compiler = javax.tools.ToolProvider.getSystemJavaCompiler();
    assert compiler != null : "A JDK compiler is required";
    var diagnostics = new javax.tools.DiagnosticCollector<javax.tools.JavaFileObject>();
    var source = new javax.tools.SimpleJavaFileObject(
      java.net.URI.create("string:///Broken.java"),
      javax.tools.JavaFileObject.Kind.SOURCE
    ) {
      public CharSequence getCharContent(boolean ignore) {
        return "class Broken { int f() { return 1 } }";
      }
    };
    try (var files = compiler.getStandardFileManager(diagnostics, null, null)) {
      boolean compiled = compiler
        .getTask(
          null,
          files,
          diagnostics,
          List.of("-proc:none", "--release", "21"),
          null,
          List.of(source)
        )
        .call();
      assert !compiled;
      assert diagnostics
        .getDiagnostics()
        .stream()
        .anyMatch(d -> d.getKind() == javax.tools.Diagnostic.Kind.ERROR);
    }
  }
}
