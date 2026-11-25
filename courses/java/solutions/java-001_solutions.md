# java-001: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

A Java program begins as text. The compiler checks syntax and types, then writes bytecode in a class file. The Java Virtual Machine loads that bytecode and invokes a recognized entry point. Compilation and execution are different stages: a missing semicolon prevents compilation, while division by zero can fail after the program starts. This course uses a public class named Main stored in Main.java. The main method is static so the launcher can call it without first creating an object. Its String array parameter contains command-line arguments. Assertions are optional in ordinary Java launches, so the classroom deliberately enables them with -ea. A printed success message cannot replace a check that would fail on incorrect behavior.

**Source:** Human-readable Java text compiled before execution.

**Bytecode:** Instructions stored in a class file for the JVM.

**Entry point:** The method the launcher invokes to start the program.

## Reading the reference

The class braces enclose methods, and the main-method braces enclose statements. public makes the entry point accessible, static associates it with the class, void means it returns no value, and String[] declares an array of text arguments. System.out.println writes one line. A semicolon ends most statements. javac --release 21 selects the source/API target; java-ea Main loads the compiled class from the classpath. Read the first compiler diagnostic before looking for runtime output.

## Exercise 1: Print a first result: change one input

Task: Change `String message = "Hello, Java";` to `String message = "Hello, Java!";` in Example A and predict which assertion fails and why.

The variable holds a reference to a String value. println adds a line separator, while the assertion checks the content independently of terminal formatting.

The unchanged code is the part that Example A adds:

```java
String message = "Hello, Java";
System.out.println(message);
assert message.equals("Hello, Java");
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `message.equals("Hello, Java")`.

**Verify:** Name the value that makes `message.equals("Hello, Java")` false, then restore the line.

## Exercise 2: Evaluate before printing: diagnose an edited check

Task: Example B's new assertion was edited to `assert line.equals("total=6");`. Explain why it fails for unchanged state and restore it.

The numeric addition happens before concatenation because it is assigned first. Mixing strings and numbers in one expression can change which plus operators mean concatenation.

The unchanged code is the part that Example B adds:

```java
int total = 2 + 3;
String line = "total=" + total;
assert total == 5;
assert line.equals("total=5");
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `line.equals("total=5")`; the restored assertion passes.

**Verify:** Explain why the edited assertion rejects the state that `line.equals("total=5")` accepts.

## Exercise 3: Trace sequential state

Task: Start count 1, increment it, then multiply it by 3.

Statements execute in order within this single thread. Reversing the last two operations would produce 4, so the final value depends on the state transition sequence.

```java
int count = 1;
count = count + 1;
count = count * 3;
assert count == 6;
```

**Expected:** final count 6.

**Verify:** Control: changing `count = count + 1;` to `count = count - 1;` must fail the assertion on `count == 6`.

## Exercise 4: Verify assertion mode

Task: Use an assertion side effect only to detect whether this teaching launch enabled assertions; fail explicitly otherwise.

Production logic must never depend on assertion side effects. This diagnostic intentionally detects the launcher mode so missing-ea cannot silently bypass the reference checks.

```java
boolean enabled = false;
assert enabled = true;
if (!enabled) throw new IllegalStateException("Run with -ea");
assert enabled;
```

**Expected:** assertion-enabled flag true.

**Verify:** Control: changing `assert enabled = true;` to `assert enabled = false;` inside the assertion must make it fail.

## Exercise 5: Separate runtime failure

Task: Divide an integer by a variable containing 0 and catch exactly ArithmeticException.

The source is well typed and can compile, but the operation fails at runtime. Catching the specific exception distinguishes this expected fixture from unrelated failures.

```java
boolean dividedByZero = false;
try {
  int zero = 0;
  int ignored = 10 / zero;
} catch (ArithmeticException expected) {
  dividedByZero = true;
}
assert dividedByZero;
```

**Expected:** ArithmeticException observed; program continues after the catch.

**Verify:** Control: changing `int zero = 0;` to `int zero = 1;` must fail the assertion on `dividedByZero`.

## Exercise 6: Observe a real compiler diagnostic

Task: Compile a small in-memory Broken class whose return statement lacks a semicolon; capture diagnostics without executing it.

The compiler checks an intentionally invalid source and returns a structured diagnostic. No class is executed. The helper is a diagnostic demonstration; a beginner can reproduce the same missing-semicolon case with javac in a saved scratch file.

```java
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
```

**Expected:** compiler result false and at least one ERROR diagnostic.

**Verify:** Control: changing `.anyMatch(d -> d.getKind() == javax.tools.Diagnostic.Kind.ERROR);` to `.anyMatch(d -> d.getKind() != javax.tools.Diagnostic.Kind.ERROR);` inside the assertion must make it fail.

## After comparing the answer

Break a different rule in the Exercise 6 source, such as using an undeclared variable, and confirm that the compiler again reports an ERROR diagnostic while no class runs.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
