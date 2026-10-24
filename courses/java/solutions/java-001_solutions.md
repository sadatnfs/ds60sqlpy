# java-001: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A Java program begins as text. The compiler checks syntax and types, then writes bytecode in a class file. The Java Virtual Machine loads that bytecode and invokes a recognized entry point. Compilation and execution are different stages: a missing semicolon prevents compilation, while division by zero can fail after the program starts. This course uses a public class named Main stored in Main.java. The main method is static so the launcher can call it without first creating an object. Its String array parameter contains command-line arguments. Assertions are optional in ordinary Java launches, so the classroom deliberately enables them with-ea. A printed success message cannot replace a check that would fail on incorrect behavior.

**Source:** Human-readable Java text compiled before execution.

**Bytecode:** Instructions stored in a class file for the JVM.

**Entry point:** The method the launcher invokes to start the program.

## Reading the reference

The class braces enclose methods, and the main-method braces enclose statements. public makes the entry point accessible, static associates it with the class, void means it returns no value, and String[] declares an array of text arguments. System.out.println writes one line. A semicolon ends most statements. javac --release21 selects the source/API target; java-ea Main loads the compiled class from the classpath. Read the first compiler diagnostic before looking for runtime output.

## Exercise 1: Print a first result

Task: Create a message variable containing Hello, Java and print it once.

The variable holds a reference to a String value. println adds a line separator, while the assertion checks the content independently of terminal formatting.

```java
String message = "Hello, Java";
System.out.println(message);
assert message.equals("Hello, Java");
```

**Expected:** one line Hello, Java.

**Verify:** Compare the program values or named exception with one line Hello, Java. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Evaluate before printing

Task: Compute2+3 into an int and build the string total=5.

The numeric addition happens before concatenation because it is assigned first. Mixing strings and numbers in one expression can change which plus operators mean concatenation.

```java
int total = 2 + 3;
String line = "total=" + total;
assert total == 5;
assert line.equals("total=5");
```

**Expected:** integer5 and text total=5.

**Verify:** Compare the program values or named exception with integer5 and text total=5. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Trace sequential state

Task: Start count1,increment it,then multiply it by3.

Statements execute in order within this single thread. Reversing the last two operations would produce4, so the final value depends on the state transition sequence.

```java
int count = 1;
count = count + 1;
count = count * 3;
assert count == 6;
```

**Expected:** final count6.

**Verify:** Compare the program values or named exception with final count6. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

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

**Verify:** Compare the program values or named exception with assertion-enabled flag true. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Separate runtime failure

Task: Divide an integer by a variable containing0 and catch exactly ArithmeticException.

The source is well typed and can compile, but the operation fails at runtime. Catching the specific exception distinguishes this expected fixture from unrelated failures.

```java
boolean dividedByZero = false;
try { int zero = 0; int ignored = 10 / zero; }
catch (ArithmeticException expected) { dividedByZero = true; }
assert dividedByZero;
```

**Expected:** ArithmeticException observed;program continues after the catch.

**Verify:** Compare the program values or named exception with ArithmeticException observed;program continues after the catch. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Observe a real compiler diagnostic

Task: Compile a small in-memory Broken class whose return statement lacks a semicolon; capture diagnostics without executing it.

The compiler checks an intentionally invalid source and returns a structured diagnostic. No class is executed. The helper is a diagnostic demonstration; a beginner can reproduce the same missing-semicolon case with javac in a saved scratch file.

```java
var compiler = javax.tools.ToolProvider.getSystemJavaCompiler();
assert compiler != null : "A JDK compiler is required";
var diagnostics = new javax.tools.DiagnosticCollector<javax.tools.JavaFileObject>();
var source = new javax.tools.SimpleJavaFileObject(java.net.URI.create("string:///Broken.java"), javax.tools.JavaFileObject.Kind.SOURCE) {
    public CharSequence getCharContent(boolean ignore) { return "class Broken { int f() { return 1 } }"; }
};
try (var files = compiler.getStandardFileManager(diagnostics, null, null)) {
    boolean compiled = compiler.getTask(null, files, diagnostics, List.of("-proc:none", "--release", "21"), null, List.of(source)).call();
    assert !compiled;
    assert diagnostics.getDiagnostics().stream().anyMatch(d -> d.getKind() == javax.tools.Diagnostic.Kind.ERROR);
}
```

**Expected:** compiler result false and at least one ERROR diagnostic.

**Verify:** Compare the program values or named exception with compiler result false and at least one ERROR diagnostic. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
