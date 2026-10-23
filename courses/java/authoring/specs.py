from render import add,ex
add(1,
'''A Java program begins as text. The compiler checks syntax and types, then writes bytecode in a class file. The Java Virtual Machine loads that bytecode and invokes a recognized entry point. Compilation and execution are different stages: a missing semicolon prevents compilation, while division by zero can fail after the program starts. This course uses a public class named Main stored in Main.java. The main method is static so the launcher can call it without first creating an object. Its String array parameter contains command-line arguments. Assertions are optional in ordinary Java launches, so the classroom deliberately enables them with-ea. A printed success message cannot replace a check that would fail on incorrect behavior.''',
'''The class braces enclose methods, and the main-method braces enclose statements. public makes the entry point accessible, static associates it with the class, void means it returns no value, and String[] declares an array of text arguments. System.out.println writes one line. A semicolon ends most statements. javac --release21 selects the source/API target; java-ea Main loads the compiled class from the classpath. Read the first compiler diagnostic before looking for runtime output.''',
[('Source','Human-readable Java text compiled before execution.'),('Bytecode','Instructions stored in a class file for the JVM.'),('Entry point','The method the launcher invokes to start the program.')],[
ex('Print a first result','Create a message variable containing Hello,Java and print it once.','one line Hello, Java.', '''String message = "Hello, Java";
System.out.println(message);
assert message.equals("Hello, Java");''','The variable holds a reference to a String value. println adds a line separator, while the assertion checks the content independently of terminal formatting.'),
ex('Evaluate before printing','Compute2+3 into an int and build the string total=5.','integer5 and text total=5.', '''int total = 2 + 3;
String line = "total=" + total;
assert total == 5;
assert line.equals("total=5");''','The numeric addition happens before concatenation because it is assigned first. Mixing strings and numbers in one expression can change which plus operators mean concatenation.'),
ex('Trace sequential state','Start count1,increment it,then multiply it by3.','final count6.', '''int count = 1;
count = count + 1;
count = count * 3;
assert count == 6;''','Statements execute in order within this single thread. Reversing the last two operations would produce4, so the final value depends on the state transition sequence.'),
ex('Verify assertion mode','Use an assertion side effect only to detect whether this teaching launch enabled assertions; fail explicitly otherwise.','assertion-enabled flagtrue.', '''boolean enabled = false;
assert enabled = true;
if (!enabled) throw new IllegalStateException("Run with -ea");
assert enabled;''','Production logic must never depend on assertion side effects. This diagnostic intentionally detects the launcher mode so missing-ea cannot silently bypass the reference checks.'),
ex('Separate runtime failure','Divide an integer by a variable containing0 and catch exactly ArithmeticException.','ArithmeticException observed;program continues after the catch.', '''boolean dividedByZero = false;
try { int zero = 0; int ignored = 10 / zero; }
catch (ArithmeticException expected) { dividedByZero = true; }
assert dividedByZero;''','The source is well typed and can compile, but the operation fails at runtime. Catching the specific exception distinguishes this expected fixture from unrelated failures.'),
ex('Observe a real compiler diagnostic','Compile a small in-memory Broken class whose return statement lacks a semicolon; capture diagnostics without executing it.','compiler resultfalse and at least one ERROR diagnostic.', '''var compiler = javax.tools.ToolProvider.getSystemJavaCompiler();
assert compiler != null : "A JDK compiler is required";
var diagnostics = new javax.tools.DiagnosticCollector<javax.tools.JavaFileObject>();
var source = new javax.tools.SimpleJavaFileObject(java.net.URI.create("string:///Broken.java"), javax.tools.JavaFileObject.Kind.SOURCE) {
    public CharSequence getCharContent(boolean ignore) { return "class Broken { int f() { return 1 } }"; }
};
try (var files = compiler.getStandardFileManager(diagnostics, null, null)) {
    boolean compiled = compiler.getTask(null, files, diagnostics, List.of("-proc:none", "--release", "21"), null, List.of(source)).call();
    assert !compiled;
    assert diagnostics.getDiagnostics().stream().anyMatch(d -> d.getKind() == javax.tools.Diagnostic.Kind.ERROR);
}''','The compiler checks an intentionally invalid source and returns a structured diagnostic. No class is executed. The helper is a diagnostic demonstration; a beginner can reproduce the same missing-semicolon case with javac in a saved scratch file.')])
add(2,
'''A numeric type defines both a range and a set of operations. Java int arithmetic uses fixed-width signed integers and can wrap on overflow. Integer division discards the fractional part toward zero, while a floating-point operand changes the operation to approximate real-number arithmetic. A cast can narrow a value and lose information; it does not prove the value fits. BigDecimal represents decimal arithmetic with explicit precision and rounding choices, useful when exact decimal meaning matters. Construct it from text when the source is decimal text, because constructing from a binary floating-point value preserves that prior approximation. Choose types from the domain contract rather than from the apparent size of one example.''',
'''L suffix creates a long literal. A widening conversion fromint tolong preserves the integer value, but the multiplication must occur after widening if it would overflowint. Math.addExact throws on overflow rather than wrapping. BigDecimal.add returns a new value because BigDecimal is immutable. compareTo compares numeric value, while equals also considers scale, so1.0 and1.00 need a declared equality policy.''',
[('Primitive','A built-in value type such asint orboolean.'),('Overflow','A result outside the range of its chosen representation.'),('Narrowing conversion','A conversion that can lose range or precision.')],[
ex('Compare integer and decimal division','Calculate7/2 and7/2.0.','integer3 and double3.5.', '''int whole = 7 / 2;
double fractional = 7 / 2.0;
assert whole == 3 && fractional == 3.5;''','The operand types select the operation. Assigning7/2 to a double afterward would preserve the already-truncated value3.0.'),
ex('Widen before multiplication','Compute50000 squared with an explicitly widened left operand.','2500000000L;int product differs.', '''long safe = (long) 50_000 * 50_000;
int wrapped = 50_000 * 50_000;
assert safe == 2_500_000_000L;
assert wrapped != safe;''','The cast affects the multiplication itself. Casting the wrappedint result tolong afterward cannot recover lost information.'),
ex('Detect overflow explicitly','Add1 to Integer.MAX_VALUE withMath.addExact.','ArithmeticException.', '''boolean rejected = false;
try { Math.addExact(Integer.MAX_VALUE, 1); }
catch (ArithmeticException expected) { rejected = true; }
assert rejected;''','Exact arithmetic helpers turn silent wraparound into a named boundary failure. Use them when overflow violates the domain contract.'),
ex('Preserve decimal source meaning','Add BigDecimal values constructed from strings0.10 and0.20.','exact decimal0.30.', '''var amount = new java.math.BigDecimal("0.10").add(new java.math.BigDecimal("0.20"));
assert amount.equals(new java.math.BigDecimal("0.30"));''','Text construction preserves the supplied decimal digits. A binary floating-point constructor can introduce a long decimal expansion before the addition begins.'),
ex('Distinguish value from scale','Compare BigDecimal1.0 and1.00 withcompareTo andequals.','compareTo0;equalsfalse.', '''var one = new java.math.BigDecimal("1.0");
var scaled = new java.math.BigDecimal("1.00");
assert one.compareTo(scaled) == 0 && !one.equals(scaled);''','The two objects have the same numeric value but different scale. Collection keys and domain equality need an explicit policy rather than a casual interchange of the two methods.'),
ex('Reject an unsupported exact division','Divide decimal1 by3 without a rounding policy, then supply scale2 andHALF_UP.','exact division throws;rounded result0.33.', '''boolean repeating = false;
try { java.math.BigDecimal.ONE.divide(new java.math.BigDecimal("3")); }
catch (ArithmeticException expected) { repeating = true; }
assert repeating;
assert java.math.BigDecimal.ONE.divide(new java.math.BigDecimal("3"), 2, java.math.RoundingMode.HALF_UP).toPlainString().equals("0.33");''','One third has no finite decimal expansion. A rounding policy is part of the calculation definition, not merely a display setting.')])
add(3,
'''Control flow chooses which statements run and how often. A boolean expression has a truth value, while short-circuit operators can skip an operand entirely. That behavior lets a null check guard a later method call. A loop invariant is a statement that remains true before and after each iteration; it connects a repeated computation to its intended result. For a prefix sum, the accumulator equals the sum of elements already visited. Boundary cases such as an empty array or a limit of zero test whether the initial state and termination condition are correct. A loop that works for one nonempty example can still have an off-by-one error.''',
'''if selects a branch. && evaluates the right operand only when the left istrue;|| evaluates it only when needed. A for loop has initialization,condition andupdate. Use index<length for zero-based arrays. The prefix-sum invariant starts with index0,sum0, then adds exactly the element at the current index before advancing. Break exits the loop;continue skips to the next iteration and can accidentally bypass an update in a while loop.''',
[('Short circuit','Skipping an operand once a boolean result is determined.'),('Loop invariant','A property preserved at every iteration boundary.'),('Boundary case','An input at an edge of the accepted domain.')],[
ex('Guard a nullable value','Use textnull and testtext!=null before callingisEmpty.','conditionfalse with noNullPointerException.', '''String text = null;
boolean nonempty = text != null && !text.isEmpty();
assert !nonempty;''','The right operand is not evaluated when the left isfalse. Reversing the operands would attempt the method call before the guard.'),
ex('Trace a prefix sum','Sum array2,4,6 while retaining the invariant thatsum covers indices belowi.','prefix sums2,6,12;final12.', '''int[] values = {2, 4, 6}; int sum = 0;
List<Integer> prefixes = new ArrayList<>();
for (int i = 0; i < values.length; i++) { sum += values[i]; prefixes.add(sum); }
assert prefixes.equals(List.of(2, 6, 12)) && sum == 12;''','The accumulator begins at the additive identity0. Each iteration adds one new element, so no record is skipped or counted twice.'),
ex('Handle an empty loop','Run the same sum pattern over an emptyint array.','sum0 and zero iterations.', '''int emptySum = 0; int iterations = 0;
for (int value : new int[0]) { emptySum += value; iterations++; }
assert emptySum == 0 && iterations == 0;''','An empty collection is a valid case for this sum contract. The initial value already represents the result, so no special fabricated element is needed.'),
ex('Count a half-open interval','Count integers starting0 whilei<5.','visited0,1,2,3,4;count5.', '''List<Integer> visited = new ArrayList<>();
for (int i = 0; i < 5; i++) visited.add(i);
assert visited.equals(List.of(0, 1, 2, 3, 4));''','Half-open bounds align naturally with array indices. Using<= would include5 and create six iterations.'),
ex('Stop at the first match','Search3,8,8 for the first8 and stop immediately.','index1.', '''int[] items = {3, 8, 8}; int found = -1;
for (int i = 0; i < items.length; i++) { if (items[i] == 8) { found = i; break; } }
assert found == 1;''','Without thebreak, later matches would overwrite the first index. The sentinel-1 represents absence and cannot be mistaken for index0.'),
ex('Expose a wrong boundary','Compare a loop usingi<=length with the validi<length contract on a one-element array.','wrong loop raisesArrayIndexOutOfBoundsException.', '''boolean failed = false; int[] single = {7};
try { for (int i = 0; i <= single.length; i++) { int ignored = single[i]; } }
catch (ArrayIndexOutOfBoundsException expected) { failed = true; }
assert failed;''','The invalid condition reachesindex1 whenlength1. This tiny counterexample localizes the off-by-one error more clearly than a large dataset.')])
add(4,
'''A method packages a computation behind a contract: which inputs it accepts, what it returns, what state it changes and how it reports invalid input. Parameters are local variables initialized from argument values. Java always passes values. For an object argument, the copied value is a reference, so both caller and callee can refer to the same mutable object. Reassigning the parameter changes only the local reference; mutating the referenced object can be visible to the caller. Overloading selects among methods by parameter types at compile time, while overriding is a different runtime mechanism introduced later. Small explicit contracts make methods testable without reading every caller.''',
'''A method declaration includes return type,name and parameter list. return sends one value to the caller and ends that invocation. Validate a domain precondition before calculating. Overloaded methods need different parameter signatures, not merely different return types. A defensive copy can prevent a helper from changing caller-owned mutable data. Use named exceptions when an argument violates the contract.''',
[('Parameter','A local variable receiving an argument value.'),('Return value','The result passed back when a method completes.'),('Pass by value','Copying argument values into method parameters.')],[
ex('Call a pure calculation','ImplementdoubleValue(intx) and evaluate7 and0.','14 and0.', '''assert doubleValue(7) == 14;
assert doubleValue(0) == 0;''','The result depends only on the argument and the method changes no external state. That makes normal and boundary cases easy to test independently.'),
ex('Validate a precondition','ImplementpositiveArea(width,height) rejecting nonpositive dimensions.','3by4 gives12;zero width throwsIllegalArgumentException.', '''assert positiveArea(3, 4) == 12;
boolean badArea = false;
try { positiveArea(0, 4); } catch (IllegalArgumentException expected) { badArea = true; }
assert badArea;''','A zero dimension is rejected because this method models a strictly positive rectangle. Another domain could allow zero, but its contract must say so.'),
ex('Observe copied primitive values','Passint5 to a helper that reassigns its local parameter to99.','caller value remains5.', '''int original = 5; reassignInt(original); assert original == 5;''','The callee receives a copy of the integer. Reassigning its parameter does not create a link back to the caller variable.'),
ex('Observe shared object mutation','Pass a list containing1 to a helper that appends2.','caller list becomes1,2.', '''List<Integer> list = new ArrayList<>(List.of(1)); append(list);
assert list.equals(List.of(1, 2));''','The reference value is copied, and both references identify the same list. Mutating that object is visible through either reference.'),
ex('Distinguish reference reassignment','Pass the list to a helper that replaces only its local parameter with a new list.','caller list remains1,2.', '''replace(list); assert list.equals(List.of(1, 2));''','Reassigning a local reference does not mutate the original object and does not reassign the caller variable. This is still pass by value.'),
ex('Inspect overload selection','Call describe withint1 andlong1L using two overloads.','int andlong respectively.', '''assert describe(1).equals("int");
assert describe(1L).equals("long");''','The literal type selects the overload. This compile-time selection is distinct from polymorphic dispatch on an object receiver.')],helper='''static int doubleValue(int x) { return Math.multiplyExact(x, 2); }
static int positiveArea(int width, int height) {
    if (width <= 0 || height <= 0) throw new IllegalArgumentException("positive dimensions required");
    return Math.multiplyExact(width, height);
}
static void reassignInt(int value) { value = 99; }
static void append(List<Integer> values) { values.add(2); }
static void replace(List<Integer> values) { values = new ArrayList<>(); }
static String describe(int value) { return "int"; }
static String describe(long value) { return "long"; }
''')
add(5,
'''An array is a fixed-length indexed container. A String is immutable text represented in UTF-16 code units. Those code units are not always complete Unicode characters: an emoji outside the basic multilingual plane uses a surrogate pair. String.length counts code units, while codePointCount counts Unicode code points. Even code points do not always equal user-perceived characters, because combining marks can join a base letter. Indexing and slicing therefore need a declared unit. Immutability means a transformation returns a new String rather than editing the original; it does not mean every object containing a String is immutable.''',
'''Array indices start at0 and stop beforelength. Arrays.copyOf creates a separate array, while assigning another variable shares the original array reference. String.codePoints produces integer Unicode values. substring uses UTF-16 offsets and can split a surrogate pair if given an arbitrary index. Normalizer.normalize with NFC is an explicit identity policy, not an automatic rule for every text field.''',
[('Array index','A zero-based position in a fixed-length container.'),('UTF-16 code unit','A16-bit storage unit used by Java String indexing.'),('Code point','A Unicode scalar identity represented by one or two UTF-16 units.')],[
ex('Copy array storage','Copy array1,2,3,mutate the copy and compare the original.','original starts1;copy starts9.', '''int[] original = {1, 2, 3}; int[] copy = Arrays.copyOf(original, original.length); copy[0] = 9;
assert original[0] == 1 && copy[0] == 9;''','The new array owns its storage. A simple assignmentcopy=original would alias the same array and make the mutation visible through both variables.'),
ex('Count text units','Inspect stringA followed by an emoji.','length3 code units;2 code points.', '''String text = "A\uD83D\uDE42";
assert text.length() == 3;
assert text.codePointCount(0, text.length()) == 2;''','The emoji occupies a surrogate pair. Treatinglength as a visible-character count would overcount this simple example.'),
ex('Observe String immutability','Convert lowercasered to uppercase and retain both references.','originalred;newRED.', '''String lower = "red"; String upper = lower.toUpperCase(Locale.ROOT);
assert lower.equals("red") && upper.equals("RED");''','The method returns a new value rather than changinglower. Locale.ROOT makes the case policy explicit for a language-neutral fixture.'),
ex('Select by code-point offset','Find the UTF-16 offset of the second code point and take the remaining substring.','substring is the intact emoji withlength2.', '''int offset = text.offsetByCodePoints(0, 1); String emoji = text.substring(offset);
assert emoji.length() == 2 && emoji.codePointCount(0, emoji.length()) == 1;''','Converting a code-point position to a UTF-16 offset respects surrogate boundaries. Arbitrarily slicing at the second surrogate would create malformed text.'),
ex('Normalize deliberately','Compare composedé ande plus combining acute before and afterNFC.','raw strings differ;normalized strings equal.', '''String composed = "\u00E9"; String decomposed = "e\u0301";
assert !composed.equals(decomposed);
assert java.text.Normalizer.normalize(decomposed, java.text.Normalizer.Form.NFC).equals(composed);''','Normalization can merge representations that look equivalent. Whether that is appropriate for an identifier, password or display field is a domain decision.'),
ex('Reject an invalid array index','Readindex3 from a length3 array and catch the boundary failure.','ArrayIndexOutOfBoundsException.', '''boolean invalid = false;
try { int ignored = original[3]; } catch (ArrayIndexOutOfBoundsException expected) { invalid = true; }
assert invalid;''','The highest valid index islength-1. A container having three elements does not makeindex3 valid.')])
add(6,
'''Lists preserve an ordered sequence and may contain duplicates. Sets represent membership without duplicate equal elements. Maps associate keys with values. Choosing among them changes what information is retained: converting a list to a set loses multiplicity, while a map keeps only one current value per equal key. ArrayList supports indexed access and resizing, while HashMap and HashSet use hashing and equality. Their iteration order is not a sorting contract. Use an explicitly ordered collection or sort a derived list when the output order matters. Immutable factory collections reject mutation; they are useful for fixed fixtures but should not be confused with mutable working state.''',
'''List.of creates a fixed unmodifiable list; newArrayList<>(...) creates a mutable copy. Map.merge combines an existing value with a new contribution and is convenient for counting. getOrDefault supplies a fallback without inserting it. Set.add returns whether membership changed. When comparing collection results, use equals for logical contents and sort keys explicitly before claiming a deterministic presentation order.''',
[('List','An ordered collection retaining duplicates.'),('Set','A collection of unique equal elements.'),('Map','A mapping from unique keys to associated values.')],[
ex('Retain sequence multiplicity','Create a mutable listred,blue,red and appendgreen.','size4;red appears twice.', '''List<String> colors = new ArrayList<>(List.of("red", "blue", "red")); colors.add("green");
assert colors.size() == 4 && Collections.frequency(colors, "red") == 2;''','A list records positions and repeated observations. Removing duplicates would change the meaning if each entry represents an event.'),
ex('Count with a map','Count each color withMap.merge.','red2,blue1,green1.', '''Map<String, Integer> counts = new HashMap<>();
for (String color : colors) counts.merge(color, 1, Integer::sum);
assert counts.equals(Map.of("red", 2, "blue", 1, "green", 1));''','The merge function defines how repeated keys combine. Replacingput on every iteration would retain only the final contribution1.'),
ex('Inspect set insertion','Insertred twice into a HashSet and inspect return values.','firsttrue,secondfalse,size1.', '''Set<String> unique = new HashSet<>();
assert unique.add("red"); assert !unique.add("red"); assert unique.size() == 1;''','The boolean return indicates whether membership changed. It does not count how many times the input value was observed.'),
ex('Create deterministic output order','Sort the count-map keys before presenting them.','blue,green,red.', '''List<String> keys = new ArrayList<>(counts.keySet()); Collections.sort(keys);
assert keys.equals(List.of("blue", "green", "red"));''','A HashMap may iterate consistently in one run without promising that order. Sorting makes the presentation contract independent of internal hashing layout.'),
ex('Distinguish lookup from insertion','Readmissing withgetOrDefault0 and compare map size.','value0;map stillsize3.', '''int before = counts.size(); int absent = counts.getOrDefault("missing", 0);
assert absent == 0 && counts.size() == before && !counts.containsKey("missing");''','A fallback value is not a stored entry. This distinction matters when zero is a legitimate observation and absence has different meaning.'),
ex('Respect unmodifiable fixtures','Try adding toList.of(1,2) and catch the specific exception.','UnsupportedOperationException.', '''boolean fixed = false;
try { List.of(1, 2).add(3); } catch (UnsupportedOperationException expected) { fixed = true; }
assert fixed;''','An unmodifiable collection prevents structural mutation through that interface. Mutable elements inside such a collection still need their own ownership policy.')])
add(7,
'''An object combines state with operations that preserve its rules. Encapsulation means callers cannot bypass those rules by directly assigning internal fields. A small account object stores a nonnegative balance in integer cents. Deposits and withdrawals validate inputs before changing state, so a rejected operation leaves the balance unchanged. The constructor creates a valid starting object, and instance methods operate on a particular receiver. Two separately constructed accounts have independent state even when their balances initially match. Encapsulation is useful when a domain has invariants; it is not a reason to hide simple immutable values behind unnecessary getters and setters.''',
'''private fields are accessed by methods inside the class. this denotes the current object when needed to distinguish fields and parameters. A method should calculate and validate a candidate state before assigning it. Math.addExact prevents integer overflow from turning a positive deposit into a negative balance. Public accessors can expose a value without exposing a mutable internal collection.''',
[('Instance','A particular object with its own state.'),('Encapsulation','Controlling state changes through operations that preserve rules.'),('Invariant','A property required to hold for every valid object state.')],[
ex('Create independent accounts','Construct accounts with100 and100 cents,deposit50 into the first.','balances150 and100.', '''Account first = new Account(100); Account second = new Account(100); first.deposit(50);
assert first.balance() == 150 && second.balance() == 100;''','Equal initial values do not mean shared identity. Eachnew expression creates a separate object whose field can evolve independently.'),
ex('Withdraw within the contract','Withdraw40 cents from the first account.','balance110.', '''first.withdraw(40); assert first.balance() == 110;''','The method validates the amount against current state, then performs one state change. The caller does not calculate and assign a raw field.'),
ex('Reject overdraft atomically','Attempt to withdraw111 from balance110.','IllegalArgumentException;balance still110.', '''boolean overdraft = false;
try { first.withdraw(111); } catch (IllegalArgumentException expected) { overdraft = true; }
assert overdraft && first.balance() == 110;''','Validation precedes mutation. Subtracting first and throwing afterward would leave an invalid object behind.'),
ex('Reject negative input','Attempt a deposit of-1.','IllegalArgumentException;balance unchanged.', '''boolean negative = false;
try { first.deposit(-1); } catch (IllegalArgumentException expected) { negative = true; }
assert negative && first.balance() == 110;''','A negative deposit is not silently interpreted as a withdrawal. Each operation has a clear domain meaning and validation path.'),
ex('Reject invalid construction','Construct an account with-1 cents.','constructor throwsIllegalArgumentException.', '''boolean invalidStart = false;
try { new Account(-1); } catch (IllegalArgumentException expected) { invalidStart = true; }
assert invalidStart;''','An invariant should hold from the moment an object becomes available. Requiring a laterrepair call would expose invalid intermediate state to every user.'),
ex('Protect against overflow','Create an account atInteger.MAX_VALUE and deposit1.','ArithmeticException;original maximum balance preserved.', '''Account full = new Account(Integer.MAX_VALUE); boolean overflow = false;
try { full.deposit(1); } catch (ArithmeticException expected) { overflow = true; }
assert overflow && full.balance() == Integer.MAX_VALUE;''','The right-hand calculation fails before field assignment, so the prior valid value remains. Overflow is distinct from an ordinary insufficient-funds domain error.')],helper='''static final class Account {
    private int cents;
    Account(int cents) { if (cents < 0) throw new IllegalArgumentException("negative balance"); this.cents = cents; }
    int balance() { return cents; }
    void deposit(int amount) { if (amount < 0) throw new IllegalArgumentException("negative deposit"); cents = Math.addExact(cents, amount); }
    void withdraw(int amount) { if (amount < 0 || amount > cents) throw new IllegalArgumentException("invalid withdrawal"); cents -= amount; }
}
''')
add(8,
'''A record is a concise carrier for a fixed set of components, with generated accessors, equality, hashing and a descriptive string. It is shallowly immutable: the component references cannot be reassigned, but a mutable object referenced by a component can still change. A compact constructor can validate and normalize incoming component values before the record is created. Defensive copying is necessary when the record owns a collection. Constructor validation should reject invalid domain state consistently, so every successfully created value can be trusted to satisfy its invariant. Records are appropriate for value-like data, not a substitute for every stateful object.''',
'''record Order(String id,List<String>items) declares component accessorsid() anditems(). In a compact constructor, assign a normalized parameter such asid=id.strip(); implicit field assignment occurs afterward. List.copyOf makes an unmodifiable shallow copy, preventing later structural changes through the caller list. It also rejects null elements, which becomes part of the chosen contract.''',
[('Record','A value-oriented class with declared components and generated methods.'),('Compact constructor','Validation and normalization code for record components.'),('Defensive copy','An owned copy preventing external mutation through shared storage.')],[
ex('Normalize at construction','Create an Order with idspaceAspace and itemx.','idA and items[x].', '''Order order = new Order(" A ", List.of("x"));
assert order.id().equals("A") && order.items().equals(List.of("x"));''','Normalization occurs once at the boundary. Every later accessor sees the canonical ID, rather than requiring callers to remember to trim it.'),
ex('Copy caller-owned collections','Create an Order from a mutable list,then append to the original list.','record retains its original single item.', '''List<String> supplied = new ArrayList<>(List.of("x")); Order copied = new Order("B", supplied); supplied.add("y");
assert copied.items().equals(List.of("x"));''','Without the copy, a caller could change the record observed value after construction. Final component references alone would not prevent that mutation.'),
ex('Use value equality','Construct another Order with normalizedA and itemx.','equals true and equalhashCode.', '''Order same = new Order("A", List.of("x"));
assert order.equals(same) && order.hashCode() == same.hashCode();''','Record equality compares component values. This is useful for stable data carriers and differs from default object identity equality.'),
ex('Reject blank identity','Construct an Order with an all-space ID.','IllegalArgumentException.', '''boolean blank = false;
try { new Order("  ", List.of("x")); } catch (IllegalArgumentException expected) { blank = true; }
assert blank;''','A syntactically valid String can still violate a domain invariant. Validate after normalization so whitespace-only values cannot slip through.'),
ex('Protect the exposed collection','Attempt to add toorder.items().','UnsupportedOperationException.', '''boolean protectedItems = false;
try { order.items().add("z"); } catch (UnsupportedOperationException expected) { protectedItems = true; }
assert protectedItems;''','The accessor returns the owned unmodifiable list. If its elements were mutable objects, their internal state would still need separate treatment.'),
ex('Reject null collection members','Try creating an Order whose items containsnull.','NullPointerException from the declaredcopy policy.', '''boolean nullItem = false;
try { new Order("C", Arrays.asList("x", null)); } catch (NullPointerException expected) { nullItem = true; }
assert nullItem;''','The constructor usesList.copyOf, whose null policy is explicit. An alternative domain could allow missing items, but should encode that meaning instead of accidentally accepting null.')],helper='''record Order(String id, List<String> items) {
    Order {
        Objects.requireNonNull(id, "id"); id = id.strip();
        if (id.isEmpty()) throw new IllegalArgumentException("blank id");
        items = List.copyOf(items);
    }
}
''')
add(9,
'''Exceptions separate normal return values from failure. A checked exception is declared or handled by callers; an unchecked exception often signals an invalid argument or programming error. Resource lifetime is a different concern: a resource must close whether the body succeeds or fails. try-with-resources closes resources in reverse declaration order. If the body throws and closing also throws, the body exception remains primary and close failures are attached as suppressed exceptions. Catching everything and returning a default would erase that information. This lesson uses tiny in-memory AutoCloseable probes to make lifetime order and suppression observable without opening external files.''',
'''A try(resource declarations) block owns the declared resources until control exits. AutoCloseable.close may throwException. getSuppressed exposes secondary close failures. Use a specific catch when a failure is expected, and preserve the original cause when translating to a domain exception. A finally block is useful for cleanup patterns not covered by resources, but throwing fromfinally can replace an important earlier failure.''',
[('Checked exception','A failure type that callers must declare or handle.'),('Resource lifetime','The interval during which an owned resource is usable.'),('Suppressed exception','A secondary close failure retained beside a primary exception.')],[
ex('Close on normal completion','Open a Probe resource,recordbody,then inspect closure order.','eventsbody,closeA.', '''List<String> events = new ArrayList<>();
try (Probe resource = new Probe("A", events, false)) { events.add("body"); }
assert events.equals(List.of("body", "closeA"));''','Leaving the block triggers close even without an explicit call in the body. Ownership is visible in the block structure.'),
ex('Close in reverse order','Declare resourcesA thenB and leave the block.','closeB beforecloseA.', '''events.clear();
try (Probe a = new Probe("A", events, false); Probe b = new Probe("B", events, false)) { events.add("body"); }
assert events.equals(List.of("body", "closeB", "closeA"));''','Later resources often depend on earlier ones, so reverse closure is deliberate. The event trace proves the actual order for this fixture.'),
ex('Close after body failure','ThrowIllegalStateException in the body and inspect events after catching it.','closeA stillrecorded.', '''events.clear(); boolean bodyFailed = false;
try (Probe a = new Probe("A", events, false)) { throw new IllegalStateException("body"); }
catch (IllegalStateException expected) { bodyFailed = true; }
assert bodyFailed && events.equals(List.of("closeA"));''','Exceptional control flow does not skip resource closure. A manually placedclose after the body statement would never execute in this case.'),
ex('Preserve suppressed close failure','Make the body throw and the resource close throw too.','primary messagebody;one suppressed exceptioncloseA.', '''events.clear();
try (Probe a = new Probe("A", events, true)) { throw new IllegalStateException("body"); }
catch (IllegalStateException expected) {
    assert expected.getMessage().equals("body");
    assert expected.getSuppressed().length == 1;
    assert expected.getSuppressed()[0].getMessage().equals("closeA");
}''','The primary failure is not lost. Suppressed exceptions retain cleanup diagnostics without pretending they were the original cause.'),
ex('Observe close-only failure','Let the body succeed butclose throwIOException.','IOExceptioncloseA is primary.', '''boolean closeFailed = false;
try (Probe a = new Probe("A", events, true)) { }
catch (java.io.IOException expected) { closeFailed = expected.getMessage().equals("closeA"); }
assert closeFailed;''','When there is no body exception, a close failure becomes the primary failure. Resource cleanup is part of the operation outcome.'),
ex('Retain a translated cause','Wrap anIOException inIllegalStateException with a domain message and inspectcause.','cause remains the originalIOException.', '''var original = new java.io.IOException("read failed");
var translated = new IllegalStateException("Cannot load lesson fixture", original);
assert translated.getCause() == original && translated.getMessage().contains("fixture");''','A useful translation adds context while preserving diagnostic ancestry. Creating a new exception with only the old message would discard type and stack information.')],helper='''static final class Probe implements AutoCloseable {
    private final String name; private final List<String> events; private final boolean fail;
    Probe(String name, List<String> events, boolean fail) { this.name=name; this.events=events; this.fail=fail; }
    public void close() throws java.io.IOException { events.add("close"+name); if(fail) throw new java.io.IOException("close"+name); }
}
''')
add(10,
'''An interface describes behavior a caller can rely on without depending on one implementation. Polymorphism lets a reference typed as that interface dispatch to the concrete object method at runtime. The caller should depend on the contract rather than inspect implementation class names. Composition builds a new behavior by holding another object and delegating to it, often making policy combinations clearer than a deep inheritance tree. Substitution requires preserving accepted inputs and promised outputs; matching a method signature alone is insufficient. This lesson uses pricing functions over integer cents so rounding and external services do not obscure the design.''',
'''An interface declares a method; implementing classes or lambdas supply its body. A variable of interface type can hold different implementations. The receiver object selects the overridden method at runtime. A composed wrapper validates its own policy, delegates to the inner implementation and checks arithmetic withMath.addExact. Keep domain validation consistent across all implementations so callers do not need class-specific exceptions.''',
[('Interface','A named behavioral contract implemented by different objects.'),('Dynamic dispatch','Selecting an implementation from the runtime receiver object.'),('Composition','Building behavior by delegating to contained collaborators.')],[
ex('Call through an interface','UsePricing references to identity andhalf-price implementations on100 cents.','100 and50.', '''Pricing regular = amount -> { requireNonnegative(amount); return amount; };
Pricing half = amount -> { requireNonnegative(amount); return amount / 2; };
assert regular.price(100) == 100 && half.price(100) == 50;''','The caller invokes the same method name while the concrete behavior differs. The shared nonnegative-input contract keeps both implementations substitutable.'),
ex('Compose a fee policy','Wrap the half-price policy with a10-cent fee.','price100 becomes60.', '''Pricing withFee = new Fee(half, 10);
assert withFee.price(100) == 60;''','The wrapper delegates first and then adds its policy. It does not duplicate the half-price calculation, so the two concerns can change independently.'),
ex('Inspect rounding semantics','Apply integer half-price to101 cents under truncation-toward-zero.','50 cents beforefee.', '''assert half.price(101) == 50;''','Rounding is part of the pricing contract. A different business rule could require rounding up or preserving fractional units, but should not be hidden behind the same informal name.'),
ex('Validate every implementation','Call regular,half andfee policy with-1.','all throwIllegalArgumentException.', '''for (Pricing policy : List.of(regular, half, withFee)) {
    boolean rejected = false;
    try { policy.price(-1); } catch (IllegalArgumentException expected) { rejected = true; }
    assert rejected;
}''','A caller should not need to know the concrete type to predict whether a domain input is accepted. Consistent validation supports substitution.'),
ex('Change a collaborator without changing caller code','Iterate over the three policies and collect prices for100.','results100,50,60.', '''List<Integer> prices = new ArrayList<>();
for (Pricing policy : List.of(regular, half, withFee)) prices.add(policy.price(100));
assert prices.equals(List.of(100, 50, 60));''','The loop depends only onPricing. Adding another valid implementation does not require a class-name conditional in the caller.'),
ex('Reject an invalid wrapper','Construct a fee wrapper with a negative fee ornull delegate.','negative feeIllegalArgumentException;null delegateNullPointerException.', '''boolean feeRejected=false, delegateRejected=false;
try { new Fee(regular,-1); } catch(IllegalArgumentException expected) { feeRejected=true; }
try { new Fee(null,1); } catch(NullPointerException expected) { delegateRejected=true; }
assert feeRejected && delegateRejected;''','A composed object must establish its own valid state at construction. Deferring a null failure until the first pricing call makes the error harder to locate.')],helper='''interface Pricing { int price(int amount); }
static void requireNonnegative(int amount) { if(amount<0) throw new IllegalArgumentException("negative amount"); }
record Fee(Pricing delegate,int cents) implements Pricing {
    Fee { Objects.requireNonNull(delegate); requireNonnegative(cents); }
    public int price(int amount) { return Math.addExact(delegate.price(amount),cents); }
}
''')
add(11,
'''Equality, hashing and ordering are related contracts with different roles. equals determines logical sameness; equal objects must have equalhashCode values so hash collections can find them. Unequal objects may share a hash, and the collection resolves collisions through equality. A comparator defines order and can consider two unequal objects tied. Tree-based sets use comparison equality for uniqueness, so a comparator that ignores an identity field can collapse distinct records. Mutable map keys are dangerous because changing a field used in hashing can make the entry unreachable through normal lookup. Prefer immutable value keys and deterministic tie-breakers.''',
'''Records generate component-basedequals andhashCode. Comparator.comparing selects a primary sort key;thenComparing supplies a tie-breaker. HashMap lookup uses hashing and equality, nottoString. A key should remain stable while stored. For numeric ordering useInteger.compare rather than subtraction, because subtracting extreme values can overflow and reverse the intended sign.''',
[('Equality contract','Rules defining when two values represent the same logical identity.'),('Hash code','A bucket-selection value consistent with equality.'),('Comparator','A rule ordering two values and identifying ties.')],[
ex('Use immutable value keys','Create two equalPoint records and insert one into a map.','lookup with the other returnsorigin;hashes equal.', '''Point a=new Point(0,0), b=new Point(0,0); Map<Point,String> map=new HashMap<>(); map.put(a,"origin");
assert a.equals(b) && a.hashCode()==b.hashCode() && map.get(b).equals("origin");''','The lookup uses logical equality rather than reference identity. A record supplies a useful default for immutable coordinate values.'),
ex('Sort with a tie-breaker','Sort people(age20,idb),(age20,ida),(age18,idc) byage thenid.','IDs c,a,b.', '''List<Person> people=new ArrayList<>(List.of(new Person("b",20),new Person("a",20),new Person("c",18)));
people.sort(Comparator.comparingInt(Person::age).thenComparing(Person::id));
assert people.stream().map(Person::id).toList().equals(List.of("c","a","b"));''','The secondary key makes equal-age ordering explicit. Without it, a presentation may depend on input order rather than the intended identity ordering.'),
ex('Expose comparator uniqueness','Insert two different people ofage20 into aTreeSet comparingage only.','setsize1 despite unequal records.', '''Set<Person> byAge=new TreeSet<>(Comparator.comparingInt(Person::age)); byAge.add(new Person("a",20)); byAge.add(new Person("b",20));
assert byAge.size()==1 && !new Person("a",20).equals(new Person("b",20));''','TreeSet treats comparator result0 as equivalent for its membership rule. The comparator must reflect the uniqueness contract the caller actually wants.'),
ex('Demonstrate mutable-key failure','Insert a key withhash1,mutate its hash field to2,and attempt lookup with the same object.','lookup fails in this fixture while mapsize remains1.', '''MutableKey key=new MutableKey(1); Map<MutableKey,String> mutable=new HashMap<>(); mutable.put(key,"value"); key.value=2;
assert mutable.get(key)==null && mutable.size()==1;''','The entry remains in a bucket selected by the original hash. Mutation does not notifyHashMap to relocate it, so stable key state is essential.'),
ex('Avoid comparator subtraction','CompareInteger.MIN_VALUE and1 usingInteger.compare.','negative result;subtraction overflows positive.', '''assert Integer.compare(Integer.MIN_VALUE,1)<0;
assert Integer.MIN_VALUE-1>0;''','A comparator must preserve ordering for the whole accepted range. Arithmetic subtraction can wrap and violate that contract.'),
ex('Keep identity and display separate','Give twoPoints the same formatted label but different coordinates;compare values.','display labels equal;points unequal.', '''Point left=new Point(1,2), right=new Point(2,1); String labelLeft="point",labelRight="point";
assert labelLeft.equals(labelRight) && !left.equals(right);''','A human-friendly label is not automatically a unique identifier. Using display text as a map key can merge distinct domain values.')],helper='''record Point(int x,int y) { }
record Person(String id,int age) { }
static final class MutableKey {
    int value; MutableKey(int value){this.value=value;}
    public int hashCode(){return value;}
    public boolean equals(Object other){return other instanceof MutableKey key && key.value==value;}
}
''')
add(12,
'''Generics express type relationships so many errors can be detected before execution. List<Integer> is not a subtype ofList<Number>, because a caller holdingList<Number> could insert aDouble and violate the original integer list. A producer wildcard?extendsNumber permits reading numbers but generally forbids adding a specific numeric subtype. A consumer wildcard?superInteger permits adding integers, while reads are only known asObject. A generic method can connect input and output types through a type parameter. Java implements most generics through erasure, so runtime class identity does not distinguishArrayList<String> fromArrayList<Integer>. Avoid raw types that bypass these checks.''',
'''The<T> before a method return type declares a method type parameter. List<?extendsNumber> can be iterated asNumber for summation. List<?superInteger> can acceptInteger values. Use<T>voidcopy(List<?extendsT>source,List<?superT>target) to connect a producer and consumer. Wildcards describe allowed operations through a reference; they do not freeze the underlying object or create a runtime conversion.''',
[('Type parameter','A named placeholder relating types in a declaration.'),('Invariance','Different generic arguments do not imply a subtype relationship.'),('Wildcard bound','A restriction describing safe reads or writes through a generic reference.')],[
ex('Read from a producer','SumList.of(1,2,3) andList.of(1.5,2.5) throughList<?extendsNumber>.','sums6.0 and4.0.', '''assert sum(List.of(1,2,3))==6.0;
assert sum(List.of(1.5,2.5))==4.0;''','The method needs only to readNumber values, so anextends bound accepts both integer and double lists without permitting unsafe insertion.'),
ex('Write to a consumer','Append integers1,2 to aList<Number> throughList<?superInteger>.','listcontains1,2.', '''List<Number> numbers=new ArrayList<>(); addTwo(numbers);
assert numbers.equals(List.of(1,2));''','ANumber list can safely receiveInteger values. Reading through thesuper-bounded reference offers less precise type information because the actual list may contain other supertypes.'),
ex('Connect source and destination types','CopyList<Integer> intoList<Number> with a bounded generic method.','destinationcontains3,4.', '''List<Number> destination=new ArrayList<>(); copy(List.of(3,4),destination);
assert destination.equals(List.of(3,4));''','The same type parameter links the producer and consumer. It permits safe widening without an unchecked cast.'),
ex('Preserve generic return type','Callfirst on aString list and assign directly toString.','resultalpha.', '''String value=first(List.of("alpha","beta")); assert value.equals("alpha");''','The generic signature carries the element type to the return value. A rawObject return would force callers to cast and shift failures to runtime.'),
ex('Handle an empty input contract','Callfirst on an empty list and require a named failure.','NoSuchElementException.', '''boolean empty=false;
try { first(List.of()); } catch(NoSuchElementException expected){empty=true;}
assert empty;''','Type safety does not establish nonemptiness. A separate value-level precondition is still needed for an operation that requires an element.'),
ex('Observe erasure carefully','Compare runtime classes ofArrayList<String> andArrayList<Integer>;explain why this does not permit unsafe assignments.','runtime classes equal;compile-time contracts remain distinct.', '''var strings=new ArrayList<String>(); var integers=new ArrayList<Integer>();
assert strings.getClass().equals(integers.getClass());
assert strings.isEmpty() && integers.isEmpty();''','Erasure describes runtime representation. It does not repeal the compiler rule thatList<Integer> cannot be assigned toList<Number>. Do not use raw casts to bypass that rule.')],helper='''static double sum(List<? extends Number> values){double total=0;for(Number value:values)total+=value.doubleValue();return total;}
static void addTwo(List<? super Integer> values){values.add(1);values.add(2);}
static <T> void copy(List<? extends T> source,List<? super T> target){target.addAll(source);}
static <T> T first(List<T> values){if(values.isEmpty())throw new NoSuchElementException("empty list");return values.get(0);}
''')
add(13,
'''A lambda supplies the behavior of a functional interface, an interface with one abstract method. It can make a small transformation or predicate easier to pass around, but it does not remove the need for a contract. Captured local variables must be final or effectively final, meaning their binding is not reassigned after initialization. Capturing a reference does not make the referenced object immutable. A lambda that appends to a shared list still has a side effect and may be unsafe in a parallel stream. Separate pure transformations from actions when possible, and use named methods when a lambda becomes difficult to explain.''',
'''Predicate<T> returns boolean, Function<T,R> maps a value to another value, and Consumer<T> performs an action without returning a result. Method references such asString::strip are compact forms of compatible lambdas. Function.andThen applies the first function before the second;compose reverses that composition order. A captured primitive value is read from its stable local binding, while a captured mutable object can still change internally.''',
[('Functional interface','An interface with one abstract method that a lambda can implement.'),('Capture','Using a surrounding local value from inside a lambda.'),('Pure transformation','A computation that returns a value without changing external state.')],[
ex('Use a predicate','Create a Predicate<Integer> accepting positive values and test3,0,-1.','true,false,false.', '''java.util.function.Predicate<Integer> positive = value -> value > 0;
assert positive.test(3) && !positive.test(0) && !positive.test(-1);''','The predicate has a single purpose and no side effects. Boundary zero is checked explicitly rather than inferred from a positive example.'),
ex('Compose transformations','Strip a string,then uppercase it withLocale.ROOT.','inputspace red space becomesRED.', '''java.util.function.Function<String,String> strip = String::strip;
java.util.function.Function<String,String> upper = value -> value.toUpperCase(Locale.ROOT);
assert strip.andThen(upper).apply(" red ").equals("RED");''','The composition order is explicit. For transformations that do not commute, reversing the order changes the result.'),
ex('Distinguish composition order','Compose add1 andmultiply2 usingandThen andcompose on3.','andThen8;compose7.', '''java.util.function.Function<Integer,Integer> addOne = value -> value + 1;
java.util.function.Function<Integer,Integer> twice = value -> value * 2;
assert addOne.andThen(twice).apply(3) == 8;
assert addOne.compose(twice).apply(3) == 7;''','A small noncommuting example makes the API semantics visible. Readingcompose as if it wereandThen is a common source of subtle pipeline errors.'),
ex('Capture a stable threshold','Capture local threshold10 in a predicate and test9,10,11.','false,true,true under>=.', '''int threshold = 10;
java.util.function.Predicate<Integer> enough = value -> value >= threshold;
assert !enough.test(9) && enough.test(10) && enough.test(11);''','The local binding is effectively final because it is not reassigned. Changing the threshold later requires a different state design rather than silently mutating a captured primitive.'),
ex('Expose mutable captured state','Capture a list in aConsumer and append two values.','captured list becomesa,b.', '''List<String> captured = new ArrayList<>();
java.util.function.Consumer<String> append = captured::add;
append.accept("a"); append.accept("b");
assert captured.equals(List.of("a","b"));''','The reference binding is stable, but the list remains mutable. This action should not be treated as a pure mapper or assumed safe under concurrent execution.'),
ex('Use a named function for a contract','Pass a method reference to a parser that rejects blank input and parses a positive integer.','7 accepted;blank rejected.', '''java.util.function.Function<String,Integer> parser = Main::parsePositive;
assert parser.apply("7") == 7;
boolean blank = false;
try { parser.apply(" "); } catch(IllegalArgumentException expected) { blank = true; }
assert blank;''','A named helper makes validation and failure behavior easier to document than a long inline lambda. Function syntax does not imply that exceptions disappear.')],helper='''static int parsePositive(String text) {
    if(text==null || text.isBlank()) throw new IllegalArgumentException("positive integer text required");
    int value=Integer.parseInt(text); if(value<=0) throw new IllegalArgumentException("positive value required"); return value;
}
''',source='https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/function/package-summary.html')
add(14,
'''A stream is a single-use computation pipeline over a source. Intermediate operations such asfilter andmap are lazy: defining them does not necessarily process elements. A terminal operation such ascollect orsum triggers the computation. The pipeline describes transformations, not a mutable container. Reduction requires an identity and an associative combination rule if it is to behave predictably under partitioning. Side effects in stream operations can make execution order and parallel behavior difficult to reason about. Prefer collectors and pure mappings over appending to a shared list from a parallelforEach.''',
'''stream() creates a pipeline,filter keeps matching elements,andmapToInt selects a primitive numeric stream. sum is a terminal reduction with identity0. groupingBy collects rows into groups;counting or summingInt defines the group aggregate. A stream cannot be reused after a terminal operation. In a parallel reduction, the identity must be neutral for every partition, and subtraction is not associative.''',
[('Lazy pipeline','A computation whose intermediate stages wait for a terminal operation.'),('Terminal operation','An operation that consumes a stream and produces a result or action.'),('Associative reduction','A combination rule unaffected by regrouping operands.')],[
ex('Filter and sum','Keep even values from1,2,3,4 and sum their squares.','20.', '''int total = List.of(1,2,3,4).stream().filter(value -> value % 2 == 0).mapToInt(value -> value * value).sum();
assert total == 20;''','The pipeline preserves the order of conceptual operations: selection happens before squaring and reduction. The result is a scalar rather than a modified source list.'),
ex('Observe laziness with an explicit terminal','Create a mapped stream that increments a counter,then consumetoList.','counter0 before terminal and3 after.', '''var calls = new java.util.concurrent.atomic.AtomicInteger();
var pipeline = List.of(1,2,3).stream().map(value -> { calls.incrementAndGet(); return value * 2; });
assert calls.get() == 0;
assert pipeline.toList().equals(List.of(2,4,6)) && calls.get() == 3;''','The counter is a teaching probe, not a recommended business side effect. toList requires mapped values, while some terminals may optimize away unnecessary stages.'),
ex('Group with a collector','Count red,blue,red withgroupingBy andcounting.','red2L,blue1L.', '''Map<String,Long> counts = List.of("red","blue","red").stream().collect(java.util.stream.Collectors.groupingBy(value -> value, java.util.stream.Collectors.counting()));
assert counts.equals(Map.of("red",2L,"blue",1L));''','The collector owns accumulation rather than relying on shared external mutation. The map ordering is unspecified unless a specific ordered map supplier is chosen.'),
ex('Reject stream reuse','Consume a stream once,then attempt another terminal operation.','IllegalStateException.', '''var once = List.of(1,2).stream(); assert once.count() == 2;
boolean reused = false;
try { once.toList(); } catch(IllegalStateException expected) { reused = true; }
assert reused;''','A stream represents one traversal. Create a new stream from the source when another computation is required.'),
ex('Check the reduction identity','Compare sum reduction with identity0 against a deliberately wrong identity10.','correct6;wrong16 in the sequential fixture.', '''int correct = List.of(1,2,3).stream().reduce(0,Integer::sum);
int wrong = List.of(1,2,3).stream().reduce(10,Integer::sum);
assert correct == 6 && wrong == 16;''','An identity is not an arbitrary initial offset when parallel partitions may each receive it. The neutral value for addition is0.'),
ex('Expose nonassociative subtraction','Compare(10-3)-2 with10-(3-2),then use an associative sum for a parallel fixture.','5 versus9;parallel sum5050.', '''assert (10-3)-2 == 5 && 10-(3-2) == 9;
assert java.util.stream.IntStream.rangeClosed(1,100).parallel().sum() == 5050;''','Subtraction changes under regrouping, so it is unsuitable as a general parallel reduction operator. Correctness must come before any performance experiment.')],source='https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/Stream.html')
add(15,
'''Time has several meanings. Instant identifies a point on theUTCtimeline. LocalDate describes a calendar date without a time zone. LocalDateTime is a wall-clock reading that may be ambiguous or nonexistent in a region because of daylight-saving transitions. ZonedDateTime combines local fields with a zone and resolved offset. A calendar day is not always24 elapsed hours. Store the meaning required by the domain rather than treating every timestamp as interchangeable text. Parse explicit offsets for event instants, and use a region zone when calendar rules matter.''',
'''Instant.parse acceptsISO8601UTCtext. atZone converts an instant to a regional representation without changing the instant. plusDays follows local calendar arithmetic,while plusHours follows elapsed time forZonedDateTime. ZoneRules.getValidOffsets reveals zero,one or two valid offsets for a local date-time. Use explicit formatters andLocale rather than relying on machine defaults.''',
[('Instant','A point on theUTCtimeline.'),('Local date-time','Calendar and clock fields without a resolved zone offset.'),('Zone rule','A region-specific mapping between local time and offsets.')],[
ex('Preserve an instant across zones','Parse2024-01-01T00:00:00Z and view it inUTC andAmerica/New_York.','same instant;New York local date2023-12-31.', '''var instant = java.time.Instant.parse("2024-01-01T00:00:00Z");
var utc = instant.atZone(java.time.ZoneId.of("UTC"));
var ny = instant.atZone(java.time.ZoneId.of("America/New_York"));
assert utc.toInstant().equals(ny.toInstant()) && ny.toLocalDate().equals(java.time.LocalDate.of(2023,12,31));''','Changing the display zone does not move the event. A date-only grouping can nevertheless change because calendar boundaries differ by zone.'),
ex('Compare calendar and elapsed days','Start at noon before the2024New York spring transition and compareplusDays1 withplusHours24.','calendar next noon is23 elapsed hours later;24hours reaches13:00.', '''var start = java.time.ZonedDateTime.of(2024,3,9,12,0,0,0,java.time.ZoneId.of("America/New_York"));
var nextDay = start.plusDays(1); var next24 = start.plusHours(24);
assert java.time.Duration.between(start,nextDay).toHours() == 23;
assert nextDay.getHour() == 12 && next24.getHour() == 13;''','A day in the local calendar crosses a daylight-saving gap here. Duration and calendar arithmetic answer different questions.'),
ex('Detect a nonexistent local time','Ask for valid offsets at2024-03-10 02:30 inNew York.','zero valid offsets.', '''var zone = java.time.ZoneId.of("America/New_York");
var gap = java.time.LocalDateTime.of(2024,3,10,2,30);
assert zone.getRules().getValidOffsets(gap).isEmpty();''','A parser may resolve a gap according to an API policy, but the original local reading did not occur. Validate explicitly when silent adjustment is unacceptable.'),
ex('Detect an ambiguous local time','Ask for offsets at2024-11-03 01:30 inNew York.','two valid offsets.', '''var overlap = java.time.LocalDateTime.of(2024,11,3,1,30);
assert zone.getRules().getValidOffsets(overlap).size() == 2;''','The clock reading occurs twice during the fall transition. A domain record needs an offset or a declared ambiguity-resolution policy to identify one instant.'),
ex('Parse a strict calendar date','Parse2024-02-29 and reject2023-02-29 withISO_LOCAL_DATE.','leap-day accepted only for2024.', '''assert java.time.LocalDate.parse("2024-02-29").getDayOfMonth() == 29;
boolean invalid = false;
try { java.time.LocalDate.parse("2023-02-29"); } catch(java.time.format.DateTimeParseException expected) { invalid = true; }
assert invalid;''','Validation follows calendar rules rather than accepting any numeric month/day combination. Keep parsing failures distinct from a missing date.'),
ex('Use a half-open time window','Include an instant at the start and exclude an instant exactly at the end of a one-hour window.','start included;end excluded.', '''var end = instant.plusSeconds(3600);
assert !instant.isBefore(instant) && instant.isBefore(end);
assert !( !end.isBefore(instant) && end.isBefore(end) );''','Half-open intervals avoid double-counting an event on adjacent boundaries. The policy should be consistent across storage,queries and reports.')],source='https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/ZonedDateTime.html')
add(16,
'''A path names a location; it is not the file contents or a guarantee that the location exists. Filesystem operations can fail because of permissions,missing parents,encoding errors or concurrent changes. Choose an explicit character encoding so text has the same meaning across machines. Temporary directories provide owned scratch space,while try-with-resources closes streams that otherwise retain file handles. Replacing a file atomically is a filesystem capability,not a universal property of every move. If atomic replacement is required,fail clearly when unsupported instead of silently claiming the same guarantee from a non-atomic fallback.''',
'''Path.resolve appends a child path,normalize removes lexicaldot segments,andtoRealPath consults the filesystem. Files.writeString/readString acceptStandardCharsets.UTF_8. Files.list andFiles.walk return streams that must close. Files.move withATOMIC_MOVE requests atomicity and may throwAtomicMoveNotSupportedException. The helper creates one owned temporary directory and deletes only its contents in a finally block.''',
[('Path','A typed representation of a filesystem location.'),('Encoding','A rule translating text characters to bytes and back.'),('Atomic move','A replacement operation observed as one filesystem action when supported.')],[
ex('Round-trip explicit UTF-8','WriteCafé and an emoji to an owned temporary file,then read it withUTF-8.','exact text equality.', '''withTemp(root -> {
    var path = root.resolve("text.txt"); String text = "Café 🙂";
    java.nio.file.Files.writeString(path,text,java.nio.charset.StandardCharsets.UTF_8);
    assert java.nio.file.Files.readString(path,java.nio.charset.StandardCharsets.UTF_8).equals(text);
});''','Explicit encoding avoids dependence on platform defaults. The round trip tests both byte writing and reading,not just aString kept in memory.'),
ex('Distinguish a path from existence','Resolve a missing child inside the temporary directory and inspect existence before creating it.','path object exists;filesystem entry absent.', '''withTemp(root -> {
    var missing = root.resolve("missing.txt");
    assert missing.getFileName().toString().equals("missing.txt") && !java.nio.file.Files.exists(missing);
});''','Constructing aPath does not create a file. Keeping those actions separate prevents accidental assumptions about setup state.'),
ex('Close a directory stream','Create two files and count them through atry-with-resourcesFiles.list stream.','count2.', '''withTemp(root -> {
    java.nio.file.Files.writeString(root.resolve("a.txt"),"a"); java.nio.file.Files.writeString(root.resolve("b.txt"),"b");
    try(var entries = java.nio.file.Files.list(root)) { assert entries.count() == 2; }
});''','The stream can hold a directory resource until closed. A terminal operation alone is not the ownership policy for anI/O-backed stream.'),
ex('Request atomic replacement honestly','Write old and staged files,requestATOMIC_MOVE,then verify the selected outcome without claiming a fallback is atomic.','either targetnew withstagedabsent,or explicit unsupported result retainingold.', '''withTemp(root -> {
    var target=root.resolve("target.txt"); var staged=root.resolve("staged.txt");
    java.nio.file.Files.writeString(target,"old"); java.nio.file.Files.writeString(staged,"new");
    try {
        java.nio.file.Files.move(staged,target,java.nio.file.StandardCopyOption.ATOMIC_MOVE,java.nio.file.StandardCopyOption.REPLACE_EXISTING);
        assert java.nio.file.Files.readString(target).equals("new") && !java.nio.file.Files.exists(staged);
    } catch(java.nio.file.AtomicMoveNotSupportedException expected) {
        assert java.nio.file.Files.readString(target).equals("old");
    }
});''','The branch reports a capability limit rather than silently weakening the contract. Atomic replacement also does not by itself prove durable persistence after a power loss.'),
ex('Expose a lexical path escape','Resolve../outside under an owned root and normalize it before checking containment.','normalized path is outside the root.', '''withTemp(root -> {
    var candidate=root.resolve("../outside").normalize();
    assert !candidate.startsWith(root.normalize());
});''','Lexical containment is useful but does not resolve symlinks. A security-sensitive file boundary needs real-path and ownership checks as discussed later.'),
ex('Verify cleanup after failure','Throw inside the owned temporary scope and confirm the directory is removed by the helper.','original exception propagated;owned directory absent.', '''final java.nio.file.Path[] created={null}; boolean propagated=false;
try { withTemp(root -> { created[0]=root; throw new java.io.IOException("fixture failure"); }); }
catch(java.io.IOException expected) { propagated=expected.getMessage().equals("fixture failure"); }
assert propagated && created[0]!=null && !java.nio.file.Files.exists(created[0]);''','Cleanup should run on both paths while preserving the primary failure. It must remain confined to the directory this exercise created.')],helper='''@FunctionalInterface interface FileWork { void run(java.nio.file.Path root) throws Exception; }
static void withTemp(FileWork work) throws Exception {
    var root=java.nio.file.Files.createTempDirectory("ds60-java-");
    try { work.run(root); }
    finally {
        try(var paths=java.nio.file.Files.walk(root)) {
            for(var path:paths.sorted(Comparator.reverseOrder()).toList()) java.nio.file.Files.deleteIfExists(path);
        }
    }
}
''',source='https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/Files.html')
add(17,
'''Optional represents the presence or absence of a value in a return contract. It can make a missing lookup explicit,but it does not replace every null or every domain error. An absent record is different from a malformed identifier,an unavailable service or a zero numeric value. UseOptional for an expected missing result and exceptions or a richer result type for invalid inputs and operational failures. A method returningOptional should not returnnull. Optional itself is a value container; callingget without checking simply moves an unchecked absence failure to a later line.''',
'''Optional.of rejectsnull,ofNullable mapsnull toempty,andmap transforms only a present value. orElse evaluates its fallback argument eagerly,whileorElseGet invokes a supplier only when needed. flatMap avoids nestedOptional when the mapper already returns one. A boundary parser can validate text before performing a lookup so malformed input does not masquerade as an ordinary miss.''',
[('Optional','A container explicitly representing presence or absence.'),('Domain error','An input or operation violating the accepted business contract.'),('Lazy fallback','A fallback computation invoked only when the value is absent.')],[
ex('Represent a missing lookup','Look up knowna andunknownb in a fixed map throughOptional.','a present with7;b empty.', '''Map<String,Integer> data=Map.of("a",7);
Optional<Integer> known=Optional.ofNullable(data.get("a")); Optional<Integer> missing=Optional.ofNullable(data.get("b"));
assert known.orElseThrow()==7 && missing.isEmpty();''','The absence ofb is an expected lookup outcome. It is not represented as zero because zero could be a valid stored value.'),
ex('Transform only present values','Map the known value todouble and apply the same mapping toempty.','14 andempty.', '''assert known.map(value -> value*2).orElseThrow()==14;
assert missing.map(value -> value*2).isEmpty();''','The mapping function is not called for an emptyOptional. This keeps the absence policy visible without repeatednull conditionals.'),
ex('Compare eager and lazy fallback','Use a counter-producing fallback withorElse andorElseGet on a present value.','orElse increments;orElseGet does not.', '''var calls=new java.util.concurrent.atomic.AtomicInteger();
assert known.orElse(calls.incrementAndGet())==7 && calls.get()==1;
assert known.orElseGet(calls::incrementAndGet)==7 && calls.get()==1;''','Method arguments are evaluated beforeorElse is invoked. A supplier delays the computation and avoids unnecessary expensive or side-effecting work.'),
ex('Reject malformed lookup input','Validate an empty identifier before consulting the map.','IllegalArgumentException rather thanempty.', '''boolean invalid=false;
try { lookup(data," "); } catch(IllegalArgumentException expected){invalid=true;}
assert invalid && lookup(data,"b").isEmpty();''','An invalid request and a valid request with no result are different outcomes. Conflating them makes error diagnosis and user feedback less precise.'),
ex('Flatten a nullable transformation','Parse an optional numeric string through a helper returningOptional<Integer>.','valid12 present;badtext empty under this declared parser policy.', '''assert Optional.of("12").flatMap(Main::tryParse).orElseThrow()==12;
assert Optional.of("bad").flatMap(Main::tryParse).isEmpty();''','The helper deliberately treats parse failure as absence for this small API. A richer application may need to retain the error reason instead of discarding it.'),
ex('Expose unsafeget','Callget onempty and catchNoSuchElementException.','specific absence failure.', '''boolean absent=false;
try { Optional.empty().get(); } catch(NoSuchElementException expected){absent=true;}
assert absent;''','Optional does not make unchecked access safe. Prefer an explicit fallback,orElseThrow with context,or a branching operation that matches the caller contract.')],helper='''static Optional<Integer> lookup(Map<String,Integer> data,String id){if(id==null||id.isBlank())throw new IllegalArgumentException("nonblank id required");return Optional.ofNullable(data.get(id));}
static Optional<Integer> tryParse(String text){try{return Optional.of(Integer.parseInt(text));}catch(NumberFormatException error){return Optional.empty();}}
''',source='https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Optional.html')
add(18,
'''A useful test distinguishes correct behavior from a plausible mistake. Repeating the implementation formula in the expected value can reproduce the same bug on both sides. Use independent examples,boundary cases and properties that follow from the contract. A mutation test deliberately changes one behavior and checks that the tests detect it. Assertions are convenient in this course because the launcher enables-ea,but production test suites often use a dedicated framework so checks cannot be disabled accidentally. Tests should expose failures rather than catch every exception and print success.''',
'''A table-driven test stores inputs and expected outputs together,then runs the same checker over all cases. A property test checks a relation over several inputs,such asreversing twice restoring an array. An exception helper should verify the expected type and fail when no exception occurs. Keep test fixtures deterministic and avoid timing assumptions for concurrency. A test passing on one input says nothing about untested boundaries unless a valid general argument supports the claim.''',
[('Test oracle','An independent basis for deciding the expected result.'),('Property','A relation that should hold across a family of inputs.'),('Mutation test','A check that an intentionally broken variant is detected.')],[
ex('Use independent table cases','Testclamp for values-2,0,3,9 underbounds0..5.','outputs0,0,3,5.', '''int[][] cases={{-2,0},{0,0},{3,3},{9,5}};
for(int[] row:cases) assert clamp(row[0],0,5)==row[1];''','The expected outputs are literal contract examples. They do not callclamp or duplicate its full branching logic to generate answers.'),
ex('Check a boundary failure','Callclamp withlower5,upper2 and requireIllegalArgumentException.','exception observed.', '''expect(IllegalArgumentException.class,() -> clamp(3,5,2));''','An invalid interval is different from a value outside a valid interval. The test ensures the implementation rejects the contract violation.'),
ex('Test an idempotence property','For values-10 through10,clamping an already clamped value leaves it unchanged.','all21 cases satisfyidempotence.', '''for(int value=-10;value<=10;value++) {
    int once=clamp(value,0,5); assert clamp(once,0,5)==once;
}''','The property follows from the output range contract. It adds coverage,but a constant-returning mutant could also be idempotent,so examples remain necessary.'),
ex('Detect a broken implementation','Use a mutant that returnsupper for values belowlower and show the table rejects it.','at least one mismatch.', '''boolean caught=false;
for(int[] row:cases) if(brokenClamp(row[0],0,5)!=row[1]) caught=true;
assert caught;''','A test suite should fail on a meaningful defect. This control demonstrates that the lower-bound example is not merely decorative.'),
ex('Verify the exception checker itself','Ask the helper to expect an exception from a successful action and catch itsAssertionError.','checker fails when no exception is thrown.', '''boolean checkerFailed=false;
try { expect(IllegalArgumentException.class,() -> { }); }
catch(AssertionError expected){checkerFailed=true;}
assert checkerFailed;''','A broken helper that silently accepts success would make every negative test pass. Testing the test utility is justified because it is a shared correctness boundary.'),
ex('Test a fresh transfer property','Reverse arrays oflength0,1,3 twice using a separate copy and compare with originals.','all originals restored;input arrays unchanged.', '''for(int[] original:List.of(new int[0],new int[]{4},new int[]{1,2,3})) {
    int[] first=reverse(original); int[] second=reverse(first);
    assert Arrays.equals(second,original);
    if(original.length>1) assert first[0]==original[original.length-1];
}''','The round-trip property and a directional example complement each other. A function returning its input unchanged would pass only the round trip,so the second assertion matters.')],helper='''static int clamp(int value,int lower,int upper){if(lower>upper)throw new IllegalArgumentException("invalid bounds");return Math.max(lower,Math.min(value,upper));}
static int brokenClamp(int value,int lower,int upper){return value<lower?upper:Math.min(value,upper);}
@FunctionalInterface interface Action{void run() throws Exception;}
static void expect(Class<? extends Throwable> type,Action action){
    try{action.run();}catch(Throwable error){if(type.isInstance(error))return;throw new AssertionError("wrong exception",error);}
    throw new AssertionError("expected "+type.getSimpleName());
}
static int[] reverse(int[] values){int[] result=values.clone();for(int i=0,j=result.length-1;i<j;i++,j--){int temporary=result[i];result[i]=result[j];result[j]=temporary;}return result;}
''')
add(19,
'''A data structure is a set of operations with representation and cost tradeoffs. AnArrayList supports constant-time indexed access but shifting elements after a front insertion costs linear work. AHashMap offers expected constant-time lookup under appropriate hashing assumptions,not a promise that every operation always costs one step. ADeque supports queue and stack operations without shifting an array prefix. APriorityQueue keeps the smallest element available but does not expose a fully sorted iteration order. BigO describes how work grows with input size,not a measured wall-clock time or a guarantee about constants.''',
'''ArrayDeque.addLast/removeFirst implements a queue;push/pop implements a stack. PriorityQueue.add andpoll maintain a heap ordering,and repeatedpoll produces sorted removal order. Iterating the heap is not a sorted traversal. Count comparisons in a simple linear search to connect an algorithmic model to observations. A hash-based membership result must use stable equality and hashing contracts.''',
[('BigO','An asymptotic upper-bound description of growth in work or space.'),('Deque','A double-ended queue supporting insertion and removal at both ends.'),('Heap','A partial ordering that keeps a minimum or maximum at the root.')],[
ex('Use a FIFO queue','Adda,b,c to anArrayDeque and remove from the front.','a,b,c order.', '''Deque<String> queue=new ArrayDeque<>(); queue.addLast("a");queue.addLast("b");queue.addLast("c");
assert List.of(queue.removeFirst(),queue.removeFirst(),queue.removeFirst()).equals(List.of("a","b","c"));''','The queue preserves arrival order. ChoosingremoveLast instead would create a stack-like policy.'),
ex('Use a LIFO stack','Push1,2,3 onto aDeque andpop all values.','3,2,1.', '''Deque<Integer> stack=new ArrayDeque<>();stack.push(1);stack.push(2);stack.push(3);
assert List.of(stack.pop(),stack.pop(),stack.pop()).equals(List.of(3,2,1));''','The most recently pushed value is removed first. Stack behavior is useful for nested traversal or undo histories but differs from fair arrival-order processing.'),
ex('Poll a priority queue','Insert5,1,4,2 and repeatedlypoll.','1,2,4,5.', '''PriorityQueue<Integer> heap=new PriorityQueue<>(List.of(5,1,4,2));List<Integer> removed=new ArrayList<>();
while(!heap.isEmpty())removed.add(heap.remove());
assert removed.equals(List.of(1,2,4,5));''','The heap guarantees the next minimum,not that its backing iteration is sorted. Repeated removal establishes the sorted sequence.'),
ex('Count linear-search work','Search for the final item in arrays oflength4 and8 using a comparison counter.','4 and8 comparisons.', '''assert comparisons(new int[]{1,2,3,4},4)==4;
assert comparisons(new int[]{1,2,3,4,5,6,7,8},8)==8;''','Doubling this worst-case input doubles observed comparisons. This supports the linear growth model for this algorithm without making a hardware timing claim.'),
ex('Preserve duplicate priorities','Insert tasks with equal priority and a stable sequence tie-breaker.','earlier sequence removed first.', '''PriorityQueue<Task> tasks=new PriorityQueue<>(Comparator.comparingInt(Task::priority).thenComparingInt(Task::sequence));
tasks.add(new Task(1,2,"later"));tasks.add(new Task(1,1,"earlier"));
assert tasks.remove().name().equals("earlier");''','A priority alone may not define a deterministic order among ties. The explicit sequence field preserves a declared policy.'),
ex('Handle empty removal explicitly','CompareDeque.pollFirst withremoveFirst on an empty queue.','poll returnsnull;remove throwsNoSuchElementException.', '''Deque<Integer> empty=new ArrayDeque<>();assert empty.pollFirst()==null;boolean failed=false;
try{empty.removeFirst();}catch(NoSuchElementException expected){failed=true;}
assert failed;''','The two APIs express different absence contracts. Choosing one deliberately is clearer than catching an exception that the caller expected as normal control flow.')],helper='''record Task(int priority,int sequence,String name){}
static int comparisons(int[] values,int target){int count=0;for(int value:values){count++;if(value==target)break;}return count;}
''',source='https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/PriorityQueue.html')
add(20,
'''Algorithms connect a problem contract to a sequence of operations and invariants. Binary search relies on sorted input and repeatedly narrows a half-open interval containing the possible answer. Stable sorting preserves relative order among equal keys,which matters when records already have a meaningful prior order. Recursion solves a problem through smaller instances and needs a base case;memoization avoids recomputing repeated subproblems. Dynamic programming makes those dependencies explicit in a table. The coin-change fixture shows why a locally greedy choice can fail even when a valid combination exists.''',
'''A lower-bound search returns the first index whose value is at least the target,orlength if none qualifies. The invariant keeps all earlier discarded positions below the target and all later discarded positions at least the target. A dynamic-programming tabledp[amount] stores the minimum coin count for that exact amount,withdp[0]=0 and an unreachable sentinel. Each transition considers a smaller amount and one added coin.''',
[('Binary-search invariant','The relationship preserved while narrowing a sorted search interval.'),('Stable sort','A sort preserving input order among equal sort keys.'),('Dynamic programming','Reusing solved subproblems according to explicit dependencies.')],[
ex('Find the first duplicate boundary','RunlowerBound on1,2,2,5 withtarget2 andtarget6.','indices1 and4.', '''int[] sorted={1,2,2,5};assert lowerBound(sorted,2)==1 && lowerBound(sorted,6)==4;''','Returning the first qualifying position gives a precise duplicate policy. An arbitrary matching index would satisfy a different search contract.'),
ex('Handle empty and outside searches','Search an empty array and a target below the first element.','both return0.', '''assert lowerBound(new int[0],7)==0;
assert lowerBound(sorted,0)==0;''','The half-open interval starts empty for an empty input. The result is an insertion position,not necessarily the index of an existing match.'),
ex('Preserve stable ties','Sort recordsa2,b1,c2 by key only and inspect the equal-key order.','IDs b,a,c.', '''List<Item> items=new ArrayList<>(List.of(new Item("a",2),new Item("b",1),new Item("c",2)));
items.sort(Comparator.comparingInt(Item::key));
assert items.stream().map(Item::id).toList().equals(List.of("b","a","c"));''','The two key2 records retain their originala-before-c order. Adding an explicit secondary comparator would intentionally define a different tie rule.'),
ex('Solve a greedy counterexample','Find minimum coins foramount6 usingcoins1,3,4.','2 coins,using3+3 rather than4+1+1.', '''assert minimumCoins(6,new int[]{1,3,4})==2;''','The best first coin does not necessarily belong to the globally best solution. The table compares all valid smaller-amount transitions.'),
ex('Represent an unreachable amount','Solveamount3 withonlycoin2 andamount0 withanypositivecoins.','-1 forunreachable3;0 foramount0.', '''assert minimumCoins(3,new int[]{2})==-1;
assert minimumCoins(0,new int[]{2,5})==0;''','Zero is the base case,while-1 is an explicit unreachable result. Confusing them would make an impossible amount look solvable with no coins.'),
ex('Reject invalid recurrence inputs','Pass a negative amount or a zero-valued coin.','IllegalArgumentException forboth.', '''boolean negative=false,zeroCoin=false;
try{minimumCoins(-1,new int[]{1});}catch(IllegalArgumentException expected){negative=true;}
try{minimumCoins(3,new int[]{0,1});}catch(IllegalArgumentException expected){zeroCoin=true;}
assert negative&&zeroCoin;''','A zero coin would not reduce the subproblem and violates the intended recurrence. Validation prevents an ill-defined algorithm rather than relying on an accidental loop bound.')],helper='''record Item(String id,int key){}
static int lowerBound(int[] values,int target){int low=0,high=values.length;while(low<high){int mid=low+(high-low)/2;if(values[mid]<target)low=mid+1;else high=mid;}return low;}
static int minimumCoins(int amount,int[] coins){
    if(amount<0||amount>1000)throw new IllegalArgumentException("amount0..1000 required");
    for(int coin:coins)if(coin<=0)throw new IllegalArgumentException("positive coins required");
    int[] dp=new int[amount+1];Arrays.fill(dp,amount+1);dp[0]=0;
    for(int current=1;current<=amount;current++)for(int coin:coins)if(coin<=current)dp[current]=Math.min(dp[current],dp[current-coin]+1);
    return dp[amount]>amount?-1:dp[amount];
}
''')
add(21,
'''Threads can execute concurrently while sharing memory. Correct communication requires a happens-before relationship,not an assumption that another thread has probably finished. Starting a thread publishes prior actions to it,and a successful join makes its completed actions visible to the joining thread. Volatile writes and reads establish a publication relationship for associated state,but volatile does not make a compound read-modify-write atomic. A counter increment reads,adds andwrites,so two threads can lose an update even if each individual access is visible.

This lesson uses bounded joins,latches and a barrier to make ordering deliberate. A controlled lost-update fixture forces both workers to read the same starting value before either writes. That demonstrates the mechanism without hoping a random stress run happens to fail. Interruption is a cooperative request,not forcible termination;blocking code should respond or preserve the interrupt status when it cannot complete its work.''',
'''Thread.start begins a new execution;calling run directly is an ordinary method call. join(timeout) waits only up to a bound,so check isAlive afterward. CountDownLatch coordinates a one-time event,and CyclicBarrier can align two reads before their writes. A volatile ready flag can publish a preceding data assignment. InterruptedException clears the interrupted status,so a handler that propagates cancellation through state should restore it with interrupt().''',
[('Happens-before','A memory-ordering relationship guaranteeing visibility of earlier actions.'),('Atomic operation','An operation that cannot be observed as separate interleaved steps.'),('Interruption','A cooperative signal requesting that a thread stop or change its work.')],[
ex('Publish a result through join','Start a worker that writes42 into a shared holder,join it with a bound,and inspect the result.','worker terminated;result42.', '''int[] result={0}; Thread worker=Thread.ofPlatform().start(() -> result[0]=42);
joinBounded(worker); assert result[0]==42;''','The join establishes the required visibility after completion. A timed sleep would not provide the same guarantee.'),
ex('Publish initial state through start','Assign7 before starting a worker that reads the holder.','worker observes7.', '''int[] input={7}; var observed=new java.util.concurrent.atomic.AtomicInteger();
Thread reader=Thread.ofPlatform().start(() -> observed.set(input[0])); joinBounded(reader);
assert observed.get()==7;''','Actions before start happen-before actions in the started thread. The fixture does not rely on the worker noticing an unsynchronized later mutation.'),
ex('Force a lost update','Make two workers read counter0,wait at a barrier,then each write its saved value plus1.','final counter1 despite two increments.', '''int[] counter={0}; var barrier=new java.util.concurrent.CyclicBarrier(2); var failure=new java.util.concurrent.atomic.AtomicReference<Throwable>();
Runnable increment=() -> { try { int saved=counter[0]; barrier.await(2,java.util.concurrent.TimeUnit.SECONDS); counter[0]=saved+1; } catch(Throwable error){failure.set(error);} };
Thread a=Thread.ofPlatform().start(increment),b=Thread.ofPlatform().start(increment);joinBounded(a);joinBounded(b);
assert failure.get()==null && counter[0]==1;''','Both reads occur before either write,so both workers write1. Visibility alone cannot make the compound operation atomic.'),
ex('Use a volatile publication flag','Write data99 before setting a volatile ready flag;read after observing that flag.','reader sees99 and finishes within the bound.', '''Publication publication=new Publication(); var seen=new java.util.concurrent.atomic.AtomicInteger(-1);
Thread consumer=Thread.ofPlatform().start(() -> { long deadline=System.nanoTime()+2_000_000_000L; while(!publication.ready && System.nanoTime()<deadline)Thread.onSpinWait(); if(publication.ready)seen.set(publication.data); });
Thread producer=Thread.ofPlatform().start(() -> { publication.data=99;publication.ready=true; });
joinBounded(producer);joinBounded(consumer);assert seen.get()==99;''','The volatile flag publishes the preceding data write. The deadline makes a failed communication contract visible rather than leaving an infinite spin loop.'),
ex('Distinguish run from start','Invoke a Runnable directly and compare its thread identity with the caller.','same thread identity for directrun.', '''Thread caller=Thread.currentThread();var identity=new java.util.concurrent.atomic.AtomicReference<Thread>();
Runnable action=() -> identity.set(Thread.currentThread()); action.run();
assert identity.get()==caller;''','A Runnable describes work. It does not create concurrency until an executor or started Thread schedules it.'),
ex('Respond to interruption','Interrupt a worker waiting on a latch,restore its flag in the catch,and verify termination.','interruption observed and worker terminated.', '''var started=new java.util.concurrent.CountDownLatch(1);var waiting=new java.util.concurrent.CountDownLatch(1);var interrupted=new java.util.concurrent.atomic.AtomicBoolean();
Thread blocked=Thread.ofPlatform().start(() -> {started.countDown();try{waiting.await();}catch(InterruptedException expected){Thread.currentThread().interrupt();interrupted.set(Thread.currentThread().isInterrupted());}});
assert started.await(2,java.util.concurrent.TimeUnit.SECONDS);blocked.interrupt();joinBounded(blocked);assert interrupted.get();''','The worker cooperates with cancellation at a blocking point. Ignoring the exception would discard the request and could leave a larger task running unexpectedly.')],helper='''static final class Publication { int data; volatile boolean ready; }
static void joinBounded(Thread thread) throws InterruptedException {thread.join(2500);if(thread.isAlive()){thread.interrupt();throw new AssertionError("thread did not terminate");}}
''',source='https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Thread.html')
add(22,
'''An ExecutorService owns task scheduling and worker lifetime. A Future represents an eventual result or failure,not proof that the task has already completed. get can block,so a bounded caller should use a timeout and decide what to do when the result is still unknown. Cancellation requests interruption when allowed,but the task must cooperate. A cancelled Future and a terminated task are related but distinct observations.

A fixed thread pool normally has an unbounded queue,which can retain more work than the application can process. A bounded ThreadPoolExecutor makes overload policy explicit through a finite queue and a rejection handler. This lesson uses latches to hold work at known points,then checks timeout,cancellation,failure propagation and shutdown without external services or arbitrary sleeps.''',
'''submit returns a Future;get(timeout,unit) returns a value or throws a named completion/timeout exception. ExecutionException wraps the task failure in getCause. cancel(true) requests interruption. try-with-resources closes the executor in Java21,but tasks still need bounded cooperative behavior. A ThreadPoolExecutor with an ArrayBlockingQueue and AbortPolicy rejects excess submissions rather than silently growing memory.''',
[('Future','A handle for an asynchronous result,failure or cancellation state.'),('Timeout','A bound on waiting,not proof that the underlying work stopped.'),('Backpressure','A policy limiting admitted work when capacity is exhausted.')],[
ex('Retrieve a bounded result','Submit a callable returning42 and get it within2seconds.','result42.', '''try(var executor=java.util.concurrent.Executors.newFixedThreadPool(2)) {
    var future=executor.submit(() -> 42);
    assert future.get(2,java.util.concurrent.TimeUnit.SECONDS)==42;
}''','The executor owns worker lifetime. The timeout makes the caller waiting policy explicit even though this fixture should finish immediately.'),
ex('Preserve task failure identity','Submit a callable throwingIllegalArgumentException and inspectFuture.get.','ExecutionException cause isIllegalArgumentException.', '''try(var executor=java.util.concurrent.Executors.newSingleThreadExecutor()) {
    var failed=executor.submit(() -> {throw new IllegalArgumentException("bad fixture");});boolean observed=false;
    try{failed.get(2,java.util.concurrent.TimeUnit.SECONDS);}catch(java.util.concurrent.ExecutionException expected){observed=expected.getCause() instanceof IllegalArgumentException;}
    assert observed;
}''','The asynchronous boundary wraps the failure but retains its cause. Replacing it with a generic successful default would hide the task outcome.'),
ex('Separate wait timeout from task completion','Hold a task on a latch,wait with a short timeout,then release and obtain the result.','TimeoutException first;later result7.', '''var gate=new java.util.concurrent.CountDownLatch(1);
try(var executor=java.util.concurrent.Executors.newSingleThreadExecutor()) {
    var future=executor.submit(() -> {gate.await();return 7;});boolean timedOut=false;
    try{future.get(20,java.util.concurrent.TimeUnit.MILLISECONDS);}catch(java.util.concurrent.TimeoutException expected){timedOut=true;}finally{gate.countDown();}
    assert timedOut && future.get(2,java.util.concurrent.TimeUnit.SECONDS)==7;
}''','The timeout stops waiting,not the task. The explicit release demonstrates that the same Future can later complete successfully.'),
ex('Cancel cooperatively','Cancel a running latch-waiting task with interruption and observe its exit signal.','Future cancelled and task catches interruption.', '''var started=new java.util.concurrent.CountDownLatch(1);var exited=new java.util.concurrent.CountDownLatch(1);
try(var executor=java.util.concurrent.Executors.newSingleThreadExecutor()) {
    var future=executor.submit(() -> {started.countDown();try{new java.util.concurrent.CountDownLatch(1).await();}catch(InterruptedException expected){Thread.currentThread().interrupt();}finally{exited.countDown();}});
    assert started.await(2,java.util.concurrent.TimeUnit.SECONDS);assert future.cancel(true);
    assert exited.await(2,java.util.concurrent.TimeUnit.SECONDS) && future.isCancelled();
}''','The exit latch is separate evidence that the task responded. Future cancellation alone does not prove arbitrary user code has stopped.'),
ex('Reject work after shutdown','Shut down an idle executor and submit another task.','RejectedExecutionException.', '''var closed=java.util.concurrent.Executors.newSingleThreadExecutor();closed.shutdown();boolean rejected=false;
try{closed.submit(() -> 1);}catch(java.util.concurrent.RejectedExecutionException expected){rejected=true;}
assert rejected && closed.awaitTermination(2,java.util.concurrent.TimeUnit.SECONDS);''','Shutdown closes admission. It is not a signal to silently create a replacement executor behind the caller\'s back.'),
ex('Enforce a bounded queue','Use one worker and one queue slot,hold the worker,fill the queue,then submit a third task.','third submission rejected;admitted tasks finish after release.', '''var hold=new java.util.concurrent.CountDownLatch(1);var running=new java.util.concurrent.CountDownLatch(1);
try(var bounded=new java.util.concurrent.ThreadPoolExecutor(1,1,0,java.util.concurrent.TimeUnit.SECONDS,new java.util.concurrent.ArrayBlockingQueue<Runnable>(1),new java.util.concurrent.ThreadPoolExecutor.AbortPolicy())) {
    var first=bounded.submit(() -> {running.countDown();hold.await();return 1;});assert running.await(2,java.util.concurrent.TimeUnit.SECONDS);
    var second=bounded.submit(() -> 2);boolean overloaded=false;
    try{bounded.submit(() -> 3);}catch(java.util.concurrent.RejectedExecutionException expected){overloaded=true;}finally{hold.countDown();}
    assert overloaded && first.get(2,java.util.concurrent.TimeUnit.SECONDS)==1 && second.get(2,java.util.concurrent.TimeUnit.SECONDS)==2;
}''','The queue bound makes overload observable. A real application can reject,block or shed work under a documented policy,but should not pretend resources are unlimited.')],source='https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ExecutorService.html')
add(23,
'''Synchronization protects a state transition,not merely a variable name. A synchronized block uses a monitor and provides mutual exclusion plus visibility when all participants follow the same locking policy. AtomicInteger supports individual atomic operations such as increment and compare-and-set. ConcurrentHashMap provides thread-safe operations,but a separate get followed by put is still a compound sequence unless a method such ascompute ormerge makes it atomic for a key.

Locks also create lifetime and ordering obligations. Always release an explicit lock in finally. Acquiring multiple locks in inconsistent order can deadlock;using one global order removes that cycle for the declared lock set. A timed tryLock can make contention a bounded outcome rather than an indefinite wait. This lesson tests exact counts and controlled contention,not a universal concurrency performance claim.''',
'''Use synchronized around the entire read-modify-write. AtomicInteger.incrementAndGet performs one atomic increment. compareAndSet succeeds only when the current value matches the expected value. ConcurrentHashMap.merge combines updates atomically for a key. ReentrantLock.tryLock(timeout,unit) returns false on bounded contention;unlock belongs in finally after a successful acquisition.''',
[('Critical section','The state transition protected by one mutual-exclusion policy.'),('Compare-and-set','An atomic conditional update based on an expected current value.'),('Lock ordering','A consistent acquisition order preventing a declared class of cycles.')],[
ex('Protect a compound counter','Run two workers making1000 synchronized increments each.','counter2000.', '''Counter counter=new Counter();runTwo(() -> {for(int i=0;i<1000;i++)counter.increment();});
assert counter.value()==2000;''','The lock covers the complete increment. Synchronizing only a read or only a write would still permit lost updates.'),
ex('Use an atomic increment','Repeat the workload withAtomicInteger.incrementAndGet.','value2000.', '''var atomic=new java.util.concurrent.atomic.AtomicInteger();runTwo(() -> {for(int i=0;i<1000;i++)atomic.incrementAndGet();});
assert atomic.get()==2000;''','The atomic operation matches this simple counter contract. More complex multi-field invariants may still require a larger critical section.'),
ex('Inspect compare-and-set','Change0to1 withCAS,then retry expecting0.','firsttrue;secondfalse;value1.', '''var state=new java.util.concurrent.atomic.AtomicInteger();assert state.compareAndSet(0,1);assert !state.compareAndSet(0,2);assert state.get()==1;''','CAS reports whether its expected-state condition held. A failed attempt must be handled according to the algorithm rather than assumed to have updated.'),
ex('Combine map updates atomically','UseConcurrentHashMap.merge for2000 total increments ofkeyx.','stored count2000.', '''var counts=new java.util.concurrent.ConcurrentHashMap<String,Integer>();runTwo(() -> {for(int i=0;i<1000;i++)counts.merge("x",1,Integer::sum);});
assert counts.get("x")==2000;''','The map operation covers the per-key combination. Thread safety of the container would not make an arbitrary get-plus-put sequence atomic.'),
ex('Bound lock contention','Hold aReentrantLock in the caller while a worker tries to acquire it with a short timeout.','worker returnsfalse;lock released in finally.', '''var lock=new java.util.concurrent.locks.ReentrantLock();var acquired=new java.util.concurrent.atomic.AtomicBoolean(true);lock.lock();
try{Thread contender=Thread.ofPlatform().start(() -> {try{boolean ok=lock.tryLock(50,java.util.concurrent.TimeUnit.MILLISECONDS);acquired.set(ok);if(ok)lock.unlock();}catch(InterruptedException error){Thread.currentThread().interrupt();}});join(contender);assert !acquired.get();}
finally{lock.unlock();}
assert !lock.isLocked();''','The owner deliberately retains the lock until the timed attempt ends. The result is a controlled contention outcome,not a race-dependent timing guess.'),
ex('Use one global order for two locks','Have both workers acquirefirst then second before incrementing shared state.','2000 increments and no blocked worker after bounded joins.', '''Object first=new Object(),second=new Object();int[] total={0};
runTwo(() -> {for(int i=0;i<1000;i++){synchronized(first){synchronized(second){total[0]++;}}}});
assert total[0]==2000;''','The same acquisition order removes the opposite-order cycle for these two locks. It does not prove that a larger program has no other lock or resource cycles.')],helper='''static final class Counter {private int value; synchronized void increment(){value++;} synchronized int value(){return value;}}
static void join(Thread thread) throws InterruptedException {thread.join(2500);if(thread.isAlive()){thread.interrupt();throw new AssertionError("worker did not stop");}}
static void runTwo(Runnable action) throws Exception {var failure=new java.util.concurrent.atomic.AtomicReference<Throwable>();Runnable checked=() -> {try{action.run();}catch(Throwable error){failure.set(error);}};Thread a=Thread.ofPlatform().start(checked),b=Thread.ofPlatform().start(checked);join(a);join(b);if(failure.get()!=null)throw new AssertionError("worker failed",failure.get());}
''',source='https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/AtomicInteger.html')
add(24,
'''Virtual threads are lightweight Java threads intended to make large numbers of blocking tasks easier to express. They still run on carrier operating-system threads and do not create additional CPU cores. A CPU-bound calculation does not become faster merely because it is placed in a virtual thread. Resource limits such as database connections,remote quotas andmemory still need backpressure. A virtual-thread-per-task executor is therefore not permission to admit unlimited work.

Java21 has pinning cases where a virtual thread blocks while holding a synchronized monitor or during certain native operations,preventing its carrier from being reused for other virtual threads. Later JDK behavior can differ,so version the explanation. Keep blocking work outside a monitor when the state contract permits it,or redesign the synchronization carefully. This lesson checks thread identity,lifetime,cancellation and a semaphore admission limit without making throughput claims.''',
'''Thread.ofVirtual starts a virtual thread;isVirtual identifies it. Executors.newVirtualThreadPerTaskExecutor creates a new virtual thread for each admitted task. A Semaphore can bound simultaneous access to a scarce resource independently of thread count. Future.get andlatches provide bounded completion evidence. Cooperative interruption remains necessary,just as with platform threads.''',
[('Virtual thread','A lightweight Java thread scheduled over carrier threads.'),('Carrier','An operating-system thread executing virtual-thread work.'),('Backpressure','A limit on admitted resource-consuming operations.'),('Pinning in Java21','A condition preventing a blocked virtual thread from releasing its carrier.')],[
ex('Observe virtual identity','Start a virtual thread that recordsisVirtual andjoin it.','true and terminated.', '''var virtual=new java.util.concurrent.atomic.AtomicBoolean();Thread task=Thread.ofVirtual().start(() -> virtual.set(Thread.currentThread().isVirtual()));task.join(2000);
assert !task.isAlive() && virtual.get();''','The identity check establishes the actual thread type. It does not measure performance or the number of carrier threads used.'),
ex('Use a scoped virtual executor','Submit four square calculations and retrieve their results with timeouts.','1,4,9,16.', '''try(var executor=java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
    List<java.util.concurrent.Future<Integer>> futures=new ArrayList<>();for(int value=1;value<=4;value++){int input=value;futures.add(executor.submit(() -> input*input));}
    List<Integer> results=new ArrayList<>();for(var future:futures)results.add(future.get(2,java.util.concurrent.TimeUnit.SECONDS));
    assert results.equals(List.of(1,4,9,16));
}''','The executor lifetime encloses its tasks. Capturing a separate effectively-final input per submission avoids confusing loop-state ownership.'),
ex('Limit a scarce resource with a semaphore','Run six tasks but allow only two inside a gated resource section.','maximum active count2;all six complete.', '''var permits=new java.util.concurrent.Semaphore(2);var active=new java.util.concurrent.atomic.AtomicInteger();var maximum=new java.util.concurrent.atomic.AtomicInteger();var entered=new java.util.concurrent.CountDownLatch(2);var release=new java.util.concurrent.CountDownLatch(1);
try(var executor=java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
    List<java.util.concurrent.Future<Integer>> futures=new ArrayList<>();
    for(int i=0;i<6;i++)futures.add(executor.submit(() -> {if(!permits.tryAcquire(2,java.util.concurrent.TimeUnit.SECONDS))throw new IllegalStateException("admission timeout");try{int now=active.incrementAndGet();maximum.accumulateAndGet(now,Math::max);entered.countDown();if(!release.await(2,java.util.concurrent.TimeUnit.SECONDS))throw new IllegalStateException("gate timeout");return 1;}finally{active.decrementAndGet();permits.release();}}));
    try{assert entered.await(2,java.util.concurrent.TimeUnit.SECONDS);}finally{release.countDown();}
    int completed=0;for(var future:futures)completed+=future.get(3,java.util.concurrent.TimeUnit.SECONDS);assert completed==6 && maximum.get()==2;
}''','Thread creation is separate from resource admission. The semaphore protects the scarce section even when many virtual threads exist.'),
ex('Preserve a CPU calculation contract','Compare a sequential sum1..1000 with four partitioned virtual tasks.','both500500;no speed claim.', '''int sequential=java.util.stream.IntStream.rangeClosed(1,1000).sum();
try(var executor=java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
    List<java.util.concurrent.Future<Integer>> parts=new ArrayList<>();for(int p=0;p<4;p++){int start=p*250+1,end=(p+1)*250;parts.add(executor.submit(() -> java.util.stream.IntStream.rangeClosed(start,end).sum()));}
    int total=0;for(var future:parts)total+=future.get(2,java.util.concurrent.TimeUnit.SECONDS);assert total==sequential && total==500500;
}''','Correct partitioning is checked independently of timing. Virtual threads do not promise to accelerate CPU-bound arithmetic.'),
ex('Cancel a blocked virtual task','Interrupt a virtual task waiting on a latch and observe its cleanup signal.','Future cancelled;task exits cooperatively.', '''var started=new java.util.concurrent.CountDownLatch(1);var exited=new java.util.concurrent.CountDownLatch(1);
try(var executor=java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
    var future=executor.submit(() -> {started.countDown();try{new java.util.concurrent.CountDownLatch(1).await();}catch(InterruptedException expected){Thread.currentThread().interrupt();}finally{exited.countDown();}});
    assert started.await(2,java.util.concurrent.TimeUnit.SECONDS);assert future.cancel(true);assert exited.await(2,java.util.concurrent.TimeUnit.SECONDS);
}''','Lightweight scheduling does not change cancellation into forcible termination. Task code still owns resource cleanup and interruption response.'),
ex('Keep a blocking wait outside a monitor','Read a state snapshot inside a synchronized block,then wait on a latch after leaving it.','caller can acquire the monitor while the worker is waiting.', '''Object monitor=new Object();var waiting=new java.util.concurrent.CountDownLatch(1);var finish=new java.util.concurrent.CountDownLatch(1);int[] state={7};var snapshot=new java.util.concurrent.atomic.AtomicInteger();
Thread worker=Thread.ofVirtual().start(() -> {synchronized(monitor){snapshot.set(state[0]);}waiting.countDown();try{finish.await(2,java.util.concurrent.TimeUnit.SECONDS);}catch(InterruptedException error){Thread.currentThread().interrupt();}});
assert waiting.await(2,java.util.concurrent.TimeUnit.SECONDS);synchronized(monitor){state[0]=8;}finish.countDown();worker.join(2000);
assert !worker.isAlive() && snapshot.get()==7 && state[0]==8;''','This design releases the monitor before blocking. It avoids the illustrated Java21 monitor-held blocking pattern,but it does not measure carrier pinning or prove a general performance improvement.')],source='https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html')
add(25,
'''The JVM manages heap memory through reachability,not by immediately freeing an object when a local variable changes. References in collections,static fields,thread locals orlisteners can keep objects alive after a caller no longer needs them. Stack frames hold local execution state and references,while objects and arrays generally live in managed heap storage. An unreachable object becomes eligible for collection,but collection timing is not a deterministic application contract.

System.gc is a request rather than proof that a particular object was reclaimed. Memory counters are observations affected by allocation,collection andimplementation details. This lesson uses bounded arrays and explicit ownership changes to explain retention without allocating until failure or relying on a forced collection. Weak references can observe optional reachability,but application correctness should not depend on when a weakly reachable object disappears.''',
'''A collection holding an array retains a strong reference. Clearing the collection removes that particular ownership path,but other references may remain. WeakReference.get may return the referent ornull depending on reachability andcollection. Runtime memory values describe the current process andshould not be treated as exact per-object size measurements. Avoid finalizers as a resource-lifetime mechanism;use explicitclose forfiles,sockets andexecutors.''',
[('Reachability','Whether an object can be reached through active reference paths.'),('Retention','Keeping an object alive through a reference that still exists.'),('Garbage collection','Reclaiming managed memory according to runtime policy.'),('Allocation rate','The amount of new storage created over a period of work.')],[
ex('Expose a strong retention path','Store a small byte array in a list anddrop the local variable reference.','list still exposes the same array contents.', '''List<byte[]> retained=new ArrayList<>();byte[] payload=new byte[1024];payload[0]=7;retained.add(payload);payload=null;
assert retained.get(0)[0]==7 && retained.get(0).length==1024;''','The local reference disappearing does not remove the list\'s ownership path. This is a common source of unbounded cache orlistener retention.'),
ex('Remove one ownership path deliberately','Keep a separate reference,clear the list,andinspect the separate reference.','list empty;separate array stillvalid.', '''byte[] separate=retained.get(0);retained.clear();
assert retained.isEmpty() && separate[0]==7;''','Clearing a container removes its references,but another strong reference can keep the object reachable. Reachability is a graph property.'),
ex('Inspect a weak reference without timing assumptions','Create aWeakReference to the still-strongly-referenced array.','weakget returns the same object while strong reference exists.', '''var weak=new java.lang.ref.WeakReference<>(separate);
assert weak.get()==separate;java.lang.ref.Reference.reachabilityFence(separate);''','The reachability fence makes the intended lifetime explicit for this observation. The exercise does not assert when collection occurs after strong references disappear.'),
ex('Separate value size from allocation count','Create ten arrays of128bytes andcount logical payload bytes.','1280 logical bytes;no exact heap-overhead claim.', '''List<byte[]> blocks=new ArrayList<>();for(int i=0;i<10;i++)blocks.add(new byte[128]);
int logical=blocks.stream().mapToInt(block -> block.length).sum();assert logical==1280;''','Array headers,alignment,references andcontainer overhead are additional. Logical payload arithmetic is not a measured object-layout receipt.'),
ex('Reuse a bounded working buffer','Fill one array repeatedly rather than retaining every intermediate array.','same buffer identity;final value9.', '''byte[] buffer=new byte[16];int identity=System.identityHashCode(buffer);
for(int i=0;i<10;i++)Arrays.fill(buffer,(byte)i);
assert System.identityHashCode(buffer)==identity && buffer[0]==9;''','Reuse can reduce allocations when ownership permits mutation. It can also create aliasing bugs if callers expect historical snapshots,so the contract matters.'),
ex('Record process memory cautiously','ReadRuntime total/free/max memory andcheck only valid ordering relationships.','nonnegative counters;max at leasttotal;no claim of exact object size.', '''Runtime runtime=Runtime.getRuntime();long total=runtime.totalMemory(),free=runtime.freeMemory(),maximum=runtime.maxMemory();
assert total>=0 && free>=0 && maximum>=total;''','Counters can change between reads andinclude runtime behavior outside this fixture. Profiling andcontrolled measurement are needed for a memory diagnosis.')],source='https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/ref/Reference.html')
add(26,
'''Packages organize class names andaccess boundaries. Aclasspath tells the runtime where unnamed-module classes canbe found;it doesnot change the package declared in source. Java\'s module system adds explicitrequires andexports relationships. Apublic class in a package is not automatically accessible from another named module unless the package is exported. Module boundaries therefore add a level beyond public/private declarations.

This lesson includes a real two-module source fixture:a greeting library exports its package,and an application requires that module. The defaultMain.java diagnostic writes the same tiny fixture into an owned temporary directory,invokes the prepared JDK compiler,inspects module descriptors andruns the application in a bounded child JVM. No external dependency is downloaded. The separate checked-in fixture and manual commands let a learner inspect the file layout directly.''',
'''The source root contains one directory per module,each withmodule-info.java and package directories. javac --module-source-path selects that layout and-m names the modules tocompile. java --module-path selects compiled modules and-mmodule/class starts the application. ModuleFinder reads descriptors without treating filenames as module identities. The child process uses a fixed local Java executable andbounded wait.''',
[('Package','A namespace andaccess grouping declared by aJava source file.'),('Classpath','Locations used tofind classes in the unnamed-module model.'),('Named module','A unit declaring dependencies andexported packages.'),('Export','Permission for other modules toaccess a package\'s publicAPI.')],[
ex('Inspect a platform module','ReadString.class module andpackage names.','modulejava.base;packagejava.lang.', '''assert String.class.getModule().getName().equals("java.base");assert String.class.getPackageName().equals("java.lang");''','The fully qualified class name,package andmodule are distinct identities. Apackage name alone doesnot establish module membership.'),
ex('Inspect the classroom classpath context','ReadMain.class module metadata.','Main belongs to the unnamed module in the standardclasspath launch.', '''assert !Main.class.getModule().isNamed();''','The classroom compiles a singleMain.java andlaunches it byclasspath. The separate fixture demonstrates named-module execution rather than pretending the pad itself is modular.'),
ex('Compile two real modules','Create the owned greeting/application fixture andcompile both with--module-source-path.','compiler exit0 andmodule-info.class files present.', '''try(ModuleFixture fixture=new ModuleFixture()) {
    assert fixture.compile()==0;
    assert java.nio.file.Files.isRegularFile(fixture.output.resolve("course.greeting/module-info.class"));
    assert java.nio.file.Files.isRegularFile(fixture.output.resolve("course.app/module-info.class"));
}''','The compiler verifies actualrequires/exports syntax andpackage layout. Merely reading a module-info string would not establish a valid build.'),
ex('Inspect declared dependencies andexports','Read the compiled descriptors withModuleFinder.','app requirescourse.greeting;library exportsedu.example.greeting.', '''try(ModuleFixture fixture=new ModuleFixture()) {
    assert fixture.compile()==0;var finder=java.lang.module.ModuleFinder.of(fixture.output);
    var app=finder.find("course.app").orElseThrow().descriptor();var library=finder.find("course.greeting").orElseThrow().descriptor();
    assert app.requires().stream().anyMatch(item -> item.name().equals("course.greeting"));
    assert library.exports().stream().anyMatch(item -> item.source().equals("edu.example.greeting"));
}''','Descriptors provide structured evidence of the boundary. Apublic class without an export would not supply the same named-moduleAPI.'),
ex('Run the modular application','Launch the compiled app in a fresh childJVM with the fixed module path.','stdoutHello, modules! andexit0.', '''try(ModuleFixture fixture=new ModuleFixture()) {
    assert fixture.compile()==0;assert fixture.run().strip().equals("Hello, modules!");
}''','The fresh process tests runtime module resolution in addition to compilation. It cannot rely on classes accidentally loaded in the parent process.'),
ex('Reject a missing module dependency','Compile an app requiringcourse.missing instead ofcourse.greeting.','nonzero compiler exit andcaptured diagnostic.', '''try(ModuleFixture fixture=new ModuleFixture()) {
    java.nio.file.Files.writeString(fixture.source.resolve("course.app/module-info.java"),"module course.app { requires course.missing; }");
    assert fixture.compile()!=0 && !fixture.diagnostics.isBlank();
}''','The negative control proves dependency resolution is being checked. The failure is expected anddoesnot get converted into a passing runtime result.')],helper='''static final class ModuleFixture implements AutoCloseable {
    final java.nio.file.Path root,source,output;String diagnostics="";
    ModuleFixture() throws Exception {
        root=java.nio.file.Files.createTempDirectory("ds60-modules-");source=root.resolve("src");output=root.resolve("out");
        write("course.greeting/module-info.java","module course.greeting { exports edu.example.greeting; }");
        write("course.greeting/edu/example/greeting/Greeter.java","package edu.example.greeting; public final class Greeter { public static String message(){return \\"Hello, modules!\\";} }");
        write("course.app/module-info.java","module course.app { requires course.greeting; }");
        write("course.app/edu/example/app/Main.java","package edu.example.app; public class Main { public static void main(String[] args){System.out.println(edu.example.greeting.Greeter.message());} }");
    }
    void write(String relative,String text) throws Exception {var path=source.resolve(relative);java.nio.file.Files.createDirectories(path.getParent());java.nio.file.Files.writeString(path,text);}
    int compile(){var compiler=javax.tools.ToolProvider.getSystemJavaCompiler();if(compiler==null)throw new IllegalStateException("JDK compiler required");var errors=new java.io.ByteArrayOutputStream();int code=compiler.run(null,errors,errors,"--release","21","--module-source-path",source.toString(),"-d",output.toString(),"-m","course.greeting,course.app");diagnostics=errors.toString(java.nio.charset.StandardCharsets.UTF_8);return code;}
    String run() throws Exception {String executable=java.nio.file.Path.of(System.getProperty("java.home"),"bin","java").toString();var process=new ProcessBuilder(executable,"-ea","--module-path",output.toString(),"-m","course.app/edu.example.app.Main").redirectErrorStream(true).start();if(!process.waitFor(5,java.util.concurrent.TimeUnit.SECONDS)){process.destroyForcibly();throw new AssertionError("child JVM timeout");}String text=new String(process.getInputStream().readAllBytes(),java.nio.charset.StandardCharsets.UTF_8);if(process.exitValue()!=0)throw new AssertionError(text);return text;}
    public void close() throws Exception {try(var paths=java.nio.file.Files.walk(root)){for(var path:paths.sorted(Comparator.reverseOrder()).toList())java.nio.file.Files.deleteIfExists(path);}}
}
''',source='https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/module/ModuleFinder.html')
add(27,
'''A build turns source anddeclared dependencies into an artifact. Reproducibility requires identifying the compiler,target level,inputs,dependency versions andpackaging metadata. A source repository alone isnot enough if a build fetches moving dependency versions or embeds timestamps that change everyrun. Maven andGradle can manage larger builds,but their configuration still needs explicit versions,verification andoffline preparation. This default lesson uses only the JDK\'sjavac andjar tools on a literal source fixture.

The example compiles one small application,packages it twice with a fixed archive timestamp,andcompares the resulting bytes in the same prepared JDK environment. It then executes theJAR. This establishes a bounded local reproducibility property,not byte-identical builds across everyJDK orOS. A dependency lock orchecksum is an identity control,not proof that a dependency is safe orappropriate.''',
'''The JavaCompiler API invokes the prepared compiler with--release21. The JDKjar tool can be accessed throughjava.util.spi.ToolProvider andgiven a fixed--date plusmain-class. Package only the intended classes directory. SHA256 compares artifactbytes;use a fresh childJVM toprove theJAR entrypoint works. A changed source ordependency identity should change the recorded build manifest.''',
[('Build input','Source,toolchain anddependency state used toproduce an artifact.'),('Reproducible artifact','An output matching a declared byte-identity contract under fixed inputs.'),('Dependency pin','An exact version orhash identifying a required component.'),('JAR','AJava archive containing classes,resources andoptional launch metadata.')],[
ex('Compile a literal application','Build a Hello class whose main printsbuild-ok.','compiler exit0;Hello.class exists.', '''try(BuildFixture fixture=new BuildFixture()) {assert fixture.compile()==0;assert java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"));}''','The compiler target is explicit. A file named.class would not by itself prove that the source compiled successfully.'),
ex('Create a runnable archive','Package the compiled classes withmain-classHello andfixedtimestamp.','JAR exists andcontainsHello.class.', '''try(BuildFixture fixture=new BuildFixture()) {
    assert fixture.compile()==0;var jar=fixture.pack("one.jar");
    try(var archive=new java.util.jar.JarFile(jar.toFile())){assert archive.getJarEntry("Hello.class")!=null;assert archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello");}
}''','The archive contains both bytecode andentrypoint metadata. These are separate checks from its filename extension.'),
ex('Compare two builds with fixed metadata','Package the same classes twice withthe same timestamp.','archive byte hashes equal in this preparedJDK.', '''try(BuildFixture fixture=new BuildFixture()) {
    assert fixture.compile()==0;var a=fixture.pack("a.jar");var b=fixture.pack("b.jar");
    assert Arrays.equals(java.security.MessageDigest.getInstance("SHA-256").digest(java.nio.file.Files.readAllBytes(a)),java.security.MessageDigest.getInstance("SHA-256").digest(java.nio.file.Files.readAllBytes(b)));
}''','The test controls timestampandinputclassbytes. It doesnot claim thatdifferentcompilerreleases generate identicalbytecode.'),
ex('Execute the packaged entrypoint','Run theJAR in a bounded childJVM.','stdoutbuild-ok;exit0.', '''try(BuildFixture fixture=new BuildFixture()) {assert fixture.compile()==0;assert fixture.run(fixture.pack("run.jar")).strip().equals("build-ok");}''','Execution verifies thatpackaging andentrypointmetadataagree. Ahashmatch alonewouldnotshowthat theartifactcanstart.'),
ex('Detect a changed source identity','Hash two source strings differing in their printedmessage.','differentSHA256digests.', '''var digest=java.security.MessageDigest.getInstance("SHA-256");
byte[] first=digest.digest("class A { int x=1; }".getBytes(java.nio.charset.StandardCharsets.UTF_8));
byte[] second=digest.digest("class A { int x=2; }".getBytes(java.nio.charset.StandardCharsets.UTF_8));
assert !Arrays.equals(first,second);''','The manifest should bind the exact inputs,not only a repository name. A changed input needs a new artifact identity andvalidation.'),
ex('Record an explicit dependency contract','Represent H2 asversion2.5.252 witha requiredverifiedhash field andreject a movingLATEST label.','exactversionaccepted;LATESTnot treated as a pin.', '''Map<String,String> dependency=Map.of("coordinate","com.h2database:h2","version","2.5.252","hash_policy","verify prepared artifact SHA256");
assert dependency.get("version").equals("2.5.252") && !dependency.get("version").equals("LATEST");''','This record states the required identitypolicy ratherthan inventing a hash. The actual preparedJAR receipt must supply the verified bytes before a release claim.')],helper='''static final class BuildFixture implements AutoCloseable {
    final java.nio.file.Path root,source,classes;
    BuildFixture() throws Exception {root=java.nio.file.Files.createTempDirectory("ds60-build-");source=root.resolve("Hello.java");classes=root.resolve("classes");java.nio.file.Files.createDirectories(classes);java.nio.file.Files.writeString(source,"public class Hello { public static void main(String[] args){System.out.println(\\"build-ok\\");} }");}
    int compile(){var compiler=javax.tools.ToolProvider.getSystemJavaCompiler();if(compiler==null)throw new IllegalStateException("JDK required");return compiler.run(null,null,null,"--release","21","-d",classes.toString(),source.toString());}
    java.nio.file.Path pack(String name) throws Exception {var target=root.resolve(name);var jar=java.util.spi.ToolProvider.findFirst("jar").orElseThrow();var output=new java.io.StringWriter();int result=jar.run(new java.io.PrintWriter(output),new java.io.PrintWriter(output),"--create","--file",target.toString(),"--main-class","Hello","--date=2020-01-01T00:00:02Z","-C",classes.toString(),".");if(result!=0)throw new AssertionError(output.toString());return target;}
    String run(java.nio.file.Path jar) throws Exception {String executable=java.nio.file.Path.of(System.getProperty("java.home"),"bin","java").toString();var process=new ProcessBuilder(executable,"-ea","-jar",jar.toString()).redirectErrorStream(true).start();if(!process.waitFor(5,java.util.concurrent.TimeUnit.SECONDS)){process.destroyForcibly();throw new AssertionError("JAR timeout");}String output=new String(process.getInputStream().readAllBytes(),java.nio.charset.StandardCharsets.UTF_8);if(process.exitValue()!=0)throw new AssertionError(output);return output;}
    public void close() throws Exception {try(var paths=java.nio.file.Files.walk(root)){for(var path:paths.sorted(Comparator.reverseOrder()).toList())java.nio.file.Files.deleteIfExists(path);}}
}
''',source='https://docs.oracle.com/en/java/javase/21/docs/specs/man/jar.html')
add(28,
'''HTTP is a request/response protocol with method,path,status,headers andbody. A successful network exchange can still return an application error such as404 or400. Aclient must inspect status before interpreting thebody. Timeouts bound waiting but do not prove that a remote operation didnot happen. Response bodies andserver exchanges own resources that need closure.

This lesson starts one short-lived server bound only to127.0.0.1 on an operating-system-selected port,then uses theJDKHttpClient tocall it. It doesnot contact anexternal service orstart a persistent deployment. Thehandler accepts anexactpath andGETmethod,returns explicitUTF-8content,andcloses everyexchange. try-with-resources owns both client andserver wrapper inJava21. Thefixture exposes prefix-routing andmethod-validation mistakes without requiring a web framework.''',
'''HttpServer.create binds anInetSocketAddress withport0,thengetAddress reveals the actualport. createContext uses prefixmatching,so thehandler should validate anexactpath when that is thecontract. HttpRequest specifies a timeout andmethod. HttpResponse exposes statusCode,headers andbody separately. stop(0) releases the ownedlistener when thefixture closes.''',
[('HTTP status','The response code describing protocol/application outcome.'),('Loopback binding','A listener restricted to thelocal host network interface.'),('Request timeout','A bound on client waiting for a request.'),('Exchange lifetime','Ownership of request/response streams andconnection state.')],[
ex('Call an owned loopback endpoint','Start the fixture andGET/health.','status200 andbodyok.', '''try(LocalServer server=new LocalServer();var client=java.net.http.HttpClient.newBuilder().connectTimeout(java.time.Duration.ofSeconds(2)).build()) {
    var response=client.send(java.net.http.HttpRequest.newBuilder(server.uri("/health")).timeout(java.time.Duration.ofSeconds(2)).GET().build(),java.net.http.HttpResponse.BodyHandlers.ofString());
    assert response.statusCode()==200 && response.body().equals("ok");
}''','The request reaches a real localHTTPserver. A returnedStringalonewouldnotverify routing,status orresourceclosure.'),
ex('Inspect content metadata','ReadContent-Type on the successfulresponse.','text/plain withUTF-8 charset.', '''try(LocalServer server=new LocalServer();var client=java.net.http.HttpClient.newHttpClient()) {
    var response=client.send(java.net.http.HttpRequest.newBuilder(server.uri("/health")).timeout(java.time.Duration.ofSeconds(2)).GET().build(),java.net.http.HttpResponse.BodyHandlers.ofString());
    assert response.headers().firstValue("Content-Type").orElseThrow().equals("text/plain; charset=utf-8");
}''','Theencoding contract belongs in the response metadata as well as thebyte-writing code. Clients should not guess aplatform default.'),
ex('Reject an unsupported method','POSTto/health underaGET-onlycontract.','status405 andmethod not allowed body.', '''try(LocalServer server=new LocalServer();var client=java.net.http.HttpClient.newHttpClient()) {
    var request=java.net.http.HttpRequest.newBuilder(server.uri("/health")).timeout(java.time.Duration.ofSeconds(2)).POST(java.net.http.HttpRequest.BodyPublishers.noBody()).build();
    var response=client.send(request,java.net.http.HttpResponse.BodyHandlers.ofString());assert response.statusCode()==405 && response.body().equals("method not allowed");
}''','A routeexistingdoesnotmakeeverymethodvalid. Validation occursbeforeperformingdomainwork.'),
ex('Reject a prefix lookalike','GET/health-extra,whichmatchesthecontextprefixbutnot thedeclaredexactpath.','status404.', '''try(LocalServer server=new LocalServer();var client=java.net.http.HttpClient.newHttpClient()) {
    var response=client.send(java.net.http.HttpRequest.newBuilder(server.uri("/health-extra")).timeout(java.time.Duration.ofSeconds(2)).GET().build(),java.net.http.HttpResponse.BodyHandlers.ofString());assert response.statusCode()==404;
}''','HttpServercontextmatchingisprefix-based. Anexactapplicationroute needsitsownpathcheck toavoidaccidentallyacceptinglookalikes.'),
ex('Keep error status separate from transport success','GETanunknownpathandinspectthecompletedresponse.','HTTPexchangecompletes with404 ratherthan a fabricated200.', '''try(LocalServer server=new LocalServer();var client=java.net.http.HttpClient.newHttpClient()) {
    var response=client.send(java.net.http.HttpRequest.newBuilder(server.uri("/missing")).timeout(java.time.Duration.ofSeconds(2)).GET().build(),java.net.http.HttpResponse.BodyHandlers.ofString());assert response.statusCode()==404;
}''','Atransport-levelsuccessdoesnotmean thedomainoperation succeeded. Clientlogicshouldbranchonstatusbeforeparsingasuccessschema.'),
ex('Verify local-only target and closure','Inspecttheboundhostandpositiveephemeralport,thenclose thewrapper.','host127.0.0.1;portpositive;closedflagtrue.', '''LocalServer owned=new LocalServer();assert owned.uri("/health").getHost().equals("127.0.0.1") && owned.uri("/health").getPort()>0;owned.close();assert owned.closed;''','Thefixtureownsandstopsitslistener. Itdoesnotchangeasharedserver orleaveadeploymentrunningafterthelesson.')],helper='''static final class LocalServer implements AutoCloseable {
    final com.sun.net.httpserver.HttpServer server;boolean closed;
    LocalServer() throws java.io.IOException {
        server=com.sun.net.httpserver.HttpServer.create(new java.net.InetSocketAddress("127.0.0.1",0),0);
        server.createContext("/health",exchange -> {try(exchange){int status;String body;if(!exchange.getRequestURI().getPath().equals("/health")){status=404;body="not found";}else if(!exchange.getRequestMethod().equals("GET")){status=405;body="method not allowed";}else{status=200;body="ok";}byte[] bytes=body.getBytes(java.nio.charset.StandardCharsets.UTF_8);exchange.getResponseHeaders().set("Content-Type","text/plain; charset=utf-8");exchange.sendResponseHeaders(status,bytes.length);try(var output=exchange.getResponseBody()){output.write(bytes);}}});server.start();
    }
    java.net.URI uri(String path){return java.net.URI.create("http://127.0.0.1:"+server.getAddress().getPort()+path);}
    public void close(){server.stop(0);closed=true;}
}
''',source='https://docs.oracle.com/en/java/javase/21/docs/api/jdk.httpserver/com/sun/net/httpserver/HttpServer.html')
