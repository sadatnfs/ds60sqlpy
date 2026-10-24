"""Original beginner Go lessons. Each case includes independent executable evidence."""

from render import add
from render import case as E

add(
    "From source text to a checked Go program",
    """A Go program is source text organized into packages. A runnable executable needs package main and a function named main with no arguments or return values. The compiler checks names and types before any statement executes. A successful build creates machine code for a particular operating system and processor architecture; the source file itself is not the executable. Inside a single goroutine, statements follow the program\'s control flow. Printing a reassuring message proves only that a print statement ran. A useful reference instead computes a result and checks an independently known expectation. This distinction becomes important when later lessons contain cancellation, partial failure and distributed state.""",
    """package declares the compilation unit\'s package. import makes another package available under a name such as fmt. func main() declares the entrypoint; braces delimit its body. A short declaration with := creates a variable and infers its type. fmt.Sprintf constructs text while fmt.Println writes it. Go inserts many semicolons automatically, so keep an opening brace on the declaration line. The helper check(condition, message) panics on false; its message should identify the broken claim.""",
    [
        ("Package", "A collection of source files compiled together."),
        ("Entrypoint", "The function invoked when this executable starts."),
        ("Assertion", "An explicit check of a claimed program property."),
    ],
    [
        E(
            "Predict a first value",
            "Bind greeting to Hello, Go and check its exact text.",
            "greeting equals Hello, Go.",
            r"""greeting := "Hello, Go"; check(greeting == "Hello, Go", "greeting")""",
            "The quotes delimit a string literal; they are not part of the stored value. Matching the exact text catches a changed greeting even if printing would still look reasonable.",
        ),
        E(
            "Compute before formatting",
            "Add 2 and 3, then format total=5.",
            "The integer is 5 and the text is total=5.",
            r"""total := 2 + 3; line := fmt.Sprintf("total=%d", total); check(total == 5 && line == "total=5", "format")""",
            "The arithmetic result and its presentation are separate values. %d formats a decimal integer, and a wrong formatting verb can produce diagnostic text rather than the intended representation.",
        ),
        E(
            "Trace statement order",
            "Start count at 1, add 1, then multiply by 3.",
            "The final count is 6.",
            r"""count := 1; count++; count *= 3; check(count == 6, "order")""",
            "Multiplication observes the already-incremented value. Reversing the last two statements produces 4, so source order is part of the contract.",
        ),
        E(
            "Distinguish zero initialization",
            "Declare an int and a bool without explicit values.",
            "The values are 0 and false.",
            r"""var n int; var ready bool; check(n == 0 && !ready, "zero values")""",
            "Every declared Go variable has a defined zero value. That avoids uninitialized numeric storage, but zero may still be an invalid domain value that requires validation.",
        ),
        E(
            "Repair a naming assumption",
            "Bind total and Total to different integers and compare them.",
            "The names refer to distinct variables.",
            r"""total := 3; Total := 7; check(total != Total, "case-sensitive names")""",
            "Identifier case matters. Export rules use capitalization across package boundaries; local variables with different case remain separate bindings.",
        ),
        E(
            "Transfer to a receipt",
            "Format an item count of 4 and unit price of 6 as amount=24.",
            "The checked result is amount=24.",
            r"""items, unit := 4, 6; receipt := fmt.Sprintf("amount=%d", items*unit); check(receipt == "amount=24", "receipt")""",
            "This combines calculation and representation while keeping the expected result independently inspectable. The example assumes whole units; currency rounding needs a separate policy.",
        ),
    ],
)

add(
    "Numeric types, constants and explicit conversions",
    """A type determines which values and operations are valid. int has an implementation-dependent width, while int64 and uint32 declare particular widths. A conversion changes representation; it is not a proof that the original value fits. Untyped numeric constants can retain exact values until context chooses a concrete type. Variables already have concrete types, so mixing integer and floating arithmetic requires an explicit decision. Integer division truncates toward zero. Floating-point values represent a finite set of approximations, and repeated calculations need a tolerance chosen from the domain. Never repair a numerical test with a tolerance large enough to hide a fundamentally wrong algorithm.""",
    """var n int64 fixes the variable\'s type. float64(n) converts the value; converting after integer division cannot restore a lost fraction. uint8 wraps values during nonconstant conversion modulo its range. A constant that cannot fit its target type is rejected by the compiler. math.Abs gives an absolute difference, and strconv.ParseInt returns both a value and an error when decoding external text.""",
    [
        ("Concrete type", "The representation and operations attached to a variable."),
        ("Conversion", "An explicit change to another type."),
        ("Truncation", "Discarding a fractional component toward zero."),
    ],
    [
        E(
            "Compare two divisions",
            "Compute 7/2 and float64(7)/2.",
            "The results are 3 and 3.5.",
            r"""a := 7 / 2; b := float64(7) / 2; check(a == 3 && b == 3.5, "division")""",
            "Converting before division selects floating arithmetic. float64(7/2) would instead be 3.0 because integer division has already occurred.",
        ),
        E(
            "Expose narrowing",
            "Convert a variable holding 260 to uint8.",
            "The narrowed value is 4.",
            r"""n := 260; small := uint8(n); check(small == 4, "narrowing")""",
            "The eight-bit unsigned result retains the value modulo 256. A direct constant assignment of 260 to uint8 would be rejected instead of silently accepted.",
        ),
        E(
            "Preserve a wide product",
            "Multiply two explicitly int64 values of 50000.",
            "The product is 2500000000.",
            r"""a, b := int64(50000), int64(50000); check(a*b == 2500000000, "wide product")""",
            "Choose a width that can represent the result before the operation. Converting an already-overflowed result afterward cannot recover the mathematical value.",
        ),
        E(
            "Check approximate arithmetic",
            "Add floating variables 0.1 and 0.2 and compare with a 1e-15 tolerance.",
            "The absolute difference from 0.3 is below 1e-15.",
            r"""a, b := 0.1, 0.2; check(math.Abs((a+b)-0.3) < 1e-15, "rounding")""",
            "The tolerance applies to this tiny calculation, not every numerical problem. Relative scale, accumulated error and NaN handling matter in larger algorithms.",
        ),
        E(
            "Reject invalid numeric text",
            "Parse the text 12x as a base-ten signed integer.",
            "Parsing returns a non-nil error.",
            r"""_, err := strconv.ParseInt("12x", 10, 64); check(err != nil, "invalid number")""",
            "Ignoring the error can turn malformed input into a misleading default or partial result. Validation belongs at the boundary where text becomes a numeric value.",
        ),
        E(
            "Transfer signed division",
            "Divide -7 by 2 and compute its remainder.",
            "The quotient is -3 and the remainder is -1.",
            r"""q, r := -7/2, -7%2; check(q == -3 && r == -1 && q*2+r == -7, "signed division")""",
            "Truncation toward zero differs from floor division for negative operands. The reconstruction identity confirms the relationship between quotient and remainder.",
        ),
    ],
    imports="math strconv",
)

add(
    "Decisions, loops and invariants",
    """Control flow determines which statements execute. A condition is a boolean expression, not a number used as a truth value. Go\'s for statement covers counting loops, condition-controlled loops and collection iteration. The safest way to reason about a loop is to name an invariant: a statement true before the first iteration and preserved by every iteration. In a prefix sum, the accumulator contains exactly the elements already visited. Empty input is therefore not an exceptional accident; the initial accumulator already represents its result. Short-circuit operators also affect execution, which makes a guard before a potentially unsafe operation meaningful.""",
    """if condition { ... } selects a branch. && skips the right operand when the left is false. for i := 0; i < len(items); i++ visits a half-open index interval. break leaves the innermost loop; continue skips to its next iteration. switch compares one expression against alternatives and does not fall through by default. A boundary using <= instead of < often attempts one extra iteration.""",
    [
        ("Invariant", "A property maintained across every loop iteration."),
        ("Short circuit", "Skipping an operand after the result is determined."),
        ("Half-open interval", "A range including its start and excluding its end."),
    ],
    [
        E(
            "Trace a prefix sum",
            "Sum 2, 4 and 6 while checking every visited prefix.",
            "The final sum is 12 and three elements were visited.",
            r"""items := []int{2,4,6}; sum := 0; for _, x := range items { sum += x }; check(sum == 12 && len(items) == 3, "sum")""",
            "The accumulator starts at the additive identity. Each iteration includes exactly one new value; double addition or a skipped element breaks the independently known total.",
        ),
        E(
            "Handle empty data",
            "Apply the same summation to an empty slice.",
            "The result is 0 with no special invented element.",
            r"""sum := 0; for _, x := range []int{} { sum += x }; check(sum == 0, "empty sum")""",
            "The loop body never runs. A correct initial state makes the empty case follow from the same algorithm rather than a separate patch.",
        ),
        E(
            "Use a safe guard",
            "Guard access to the first element of an empty slice with a length check.",
            "The condition is false and no indexing occurs.",
            r"""items := []int{}; positive := len(items) > 0 && items[0] > 0; check(!positive, "guard")""",
            "Reversing the operands would index before proving a valid position. Short-circuit behavior is part of this safety argument.",
        ),
        E(
            "Find the first match",
            "Find the first 8 in 3, 8, 8.",
            "Its index is 1.",
            r"""found := -1; for i,x := range []int{3,8,8} { if x == 8 { found = i; break } }; check(found == 1, "first match")""",
            "Without break, the later match replaces the first one. The -1 sentinel distinguishes absence from a valid first index of zero.",
        ),
        E(
            "Classify an exact boundary",
            "Classify a score of 60 as pass using a threshold of 60.",
            "The boundary belongs to the passing branch.",
            r"""score := 60; label := "fail"; if score >= 60 { label = "pass" }; check(label == "pass", "inclusive boundary")""",
            "Boundary tests distinguish >= from >. Natural-language requirements should make inclusion explicit rather than leaving it to an arbitrary operator choice.",
        ),
        E(
            "Transfer to a filtered count",
            "Count nonnegative values in -2, 0, 4 and -1.",
            "Exactly 2 values satisfy the predicate.",
            r"""count := 0; for _,x := range []int{-2,0,4,-1} { if x < 0 { continue }; count++ }; check(count == 2, "filtered count")""",
            "continue avoids the increment for negative inputs. Zero is included deliberately, so the boundary case rejects a mistakenly positive-only predicate.",
        ),
    ],
)

add(
    "Functions and value-passing contracts",
    """A function separates a computation from its callers. Its contract names accepted inputs, returned values, mutation and failure. Go passes arguments by value. For an integer this copies the integer; for a slice it copies a descriptor whose backing storage may still be shared. Multiple return values make a result plus error a normal language pattern. Named return variables are real local variables, not a replacement for clear control flow. A pure function depends only on its inputs and does not mutate shared state, which usually makes boundary tests simpler. Design the contract before deciding whether a pointer or a collection is convenient.""",
    """func twice(x int) int declares a parameter and a return type. return ends the invocation. (int, error) declares two returned values, which callers normally bind together and check before using the result. A variadic parameter ...int accepts zero or more values; within the function it is a slice. A return from a helper returns only from that helper, not the caller.""",
    [
        ("Parameter", "A local variable initialized from an argument value."),
        (
            "Pure function",
            "A function whose result depends only on its inputs without external mutation.",
        ),
        ("Precondition", "An input requirement checked before calculation."),
    ],
    [
        E(
            "Implement a pure helper",
            "Implement twice and check inputs 7 and 0.",
            "The results are 14 and 0.",
            r"""check(twice(7) == 14 && twice(0) == 0, "twice")""",
            "The zero case confirms the helper calculates from its input rather than returning a memorized positive result.",
        ),
        E(
            "Return an explicit failure",
            "Implement positiveArea that rejects a nonpositive dimension.",
            "3 by 4 returns 12; zero width returns an error.",
            r"""area, err := positiveArea(3,4); check(err == nil && area == 12, "area"); _, err = positiveArea(0,4); check(err != nil, "invalid area")""",
            "The error describes a domain policy. Another geometry API might allow zero area, but its contract must say so.",
        ),
        E(
            "Trace copied scalar state",
            "Pass 5 to a helper that reassigns its local parameter.",
            "The caller still holds 5.",
            r"""n := 5; reassign(n); check(n == 5, "value copy")""",
            "Reassigning the copied parameter does not reassign the caller variable. This is a language rule, not a compiler optimization.",
        ),
        E(
            "Return both ordered values",
            "Implement bounds for two integers.",
            "Inputs 9 and 2 return 2 then 9.",
            r"""low, high := bounds(9,2); check(low == 2 && high == 9, "bounds")""",
            "Multiple returns can make a small contract clearer than mutating two caller-owned outputs.",
        ),
        E(
            "Test a variadic identity",
            "Sum zero inputs and then 1, 2 and 3.",
            "The results are 0 and 6.",
            r"""check(total() == 0 && total(1,2,3) == 6, "variadic")""",
            "An empty variadic argument list is a normal case. The accumulator's identity determines its answer.",
        ),
        E(
            "Transfer the contract",
            "Call the area helper with a negative height and keep the error visible.",
            "The invalid domain is rejected before returning a usable area.",
            r"""value, err := positiveArea(3,-1); check(err != nil && value == 0, "negative dimension")""",
            "Using only value while discarding err would erase the distinction between a valid zero and a rejected request. This helper deliberately reserves zero for its error path.",
        ),
    ],
    imports="errors",
    helper=r"""func twice(x int) int { return 2*x }
func positiveArea(w,h int) (int,error) { if w <= 0 || h <= 0 { return 0, errors.New("positive dimensions required") }; return w*h,nil }
func reassign(x int) { x = 99 }
func bounds(a,b int) (int,int) { if a < b { return a,b }; return b,a }
func total(values ...int) int { n:=0; for _,v:=range values { n+=v }; return n }""",
)

add(
    "Arrays, slices and backing-storage ownership",
    """An array includes its length in its type and owns a fixed sequence of elements. A slice is a descriptor containing a pointer into backing storage, a length and a capacity. Copying that descriptor does not copy the elements. Two slices can therefore observe each other\'s mutations. append may reuse available storage or allocate new storage; code must not depend on which choice happens unless it controls the capacity contract. A full slice expression can restrict capacity and force a later append to allocate. The practical question is not whether a value looks like a collection, but who can mutate the same storage and for how long.""",
    """[]int constructs a slice type; [3]int constructs an array type. values[a:b] selects indices a through b-1. len is the visible element count and cap is the maximum length before reallocation is required. copy(dst,src) copies the smaller length and returns that count. append returns a new slice descriptor, so retain the returned value. A nil slice has length zero and can be appended to.""",
    [
        ("Backing array", "The element storage referenced by one or more slices."),
        ("Capacity", "The available length from a slice start within its backing storage."),
        ("Aliasing", "Multiple references to the same mutable storage."),
    ],
    [
        E(
            "Observe shared storage",
            "Take the first two elements of 1, 2, 3 and change the first through the slice.",
            "The original first element becomes 9.",
            r"""values:=[]int{1,2,3}; view:=values[:2]; view[0]=9; check(values[0]==9, "alias")""",
            "Slicing constructs a view over existing storage. It does not give the new variable independent ownership of its elements.",
        ),
        E(
            "Make an independent copy",
            "Copy 1, 2, 3 into a new slice and mutate that copy.",
            "The original stays 1 while the copy starts 9.",
            r"""values:=[]int{1,2,3}; cloned:=append([]int(nil), values...); cloned[0]=9; check(values[0]==1 && cloned[0]==9, "copy")""",
            "Appending into initially nil storage allocates enough backing storage for these nonempty values. Nested pointers would still require a deeper copy policy.",
        ),
        E(
            "Restrict append capacity",
            "Take values[:1:1] and append 8.",
            "The original second element remains 2.",
            r"""values:=[]int{1,2,3}; limited:=values[:1:1]; grown:=append(limited,8); check(values[1]==2 && grown[1]==8, "capacity boundary")""",
            "The three-index form caps available capacity at one. append must allocate to grow, which separates subsequent writes to the grown slice.",
        ),
        E(
            "Inspect a truncated copy",
            "Copy three source elements into a length-two destination.",
            "Exactly two elements are copied.",
            r"""dst:=make([]int,2); n:=copy(dst,[]int{4,5,6}); check(n==2 && dst[1]==5, "copy length")""",
            "Capacity alone does not determine how many elements copy writes; the destination length is the bound.",
        ),
        E(
            "Grow an empty slice",
            "Append 7 to a nil slice.",
            "The result has length 1 and value 7.",
            r"""var values []int; check(values==nil && len(values)==0,"nil slice"); values=append(values,7); check(len(values)==1 && values[0]==7,"append nil")""",
            "Nil is an empty slice value with no backing array. It supports ordinary append without an explicit allocation call.",
        ),
        E(
            "Transfer array semantics",
            "Copy a fixed array and mutate the copy.",
            "The original array remains unchanged.",
            r"""a:=[2]int{1,2}; b:=a; b[0]=9; check(a[0]==1 && b[0]==9,"array copy")""",
            "Array assignment copies every element, unlike slice-descriptor assignment. This contrast explains why representation affects mutation behavior.",
        ),
    ],
)

add(
    "Maps, presence and deterministic ordering",
    """A map associates keys with values. Reading an absent key returns the value type\'s zero value, which can be indistinguishable from a present key whose value is zero. The comma-ok form retains the presence information. Map iteration order is deliberately unspecified; reproducible reports must extract and sort keys rather than rely on an observed order. Maps share mutable storage when assigned, and ordinary maps are not safe for concurrent mutation without synchronization. A nil map can be read but cannot accept an assignment. Treat these properties as part of the data model when building counters, caches and configuration overlays.""",
    """map[string]int declares string keys and integer values. value, ok := counts[key] distinguishes absence from zero. make initializes writable map storage. delete removes a key and is harmless if the key is absent. range gives key/value pairs in an unspecified order. Use sort.Strings on extracted keys before producing ordered output.""",
    [
        ("Key", "A comparable value identifying a map entry."),
        ("Presence bit", "The boolean distinguishing an existing entry from absence."),
        ("Deterministic order", "An explicitly chosen ordering independent of map iteration."),
    ],
    [
        E(
            "Distinguish zero from missing",
            "Read present key zero and absent key missing with comma-ok.",
            "Both values are 0, but only zero is present.",
            r"""m:=map[string]int{"zero":0}; a,okA:=m["zero"]; b,okB:=m["missing"]; check(a==b && okA && !okB,"presence")""",
            "A numeric value alone cannot represent both absence and an intentional zero without losing information.",
        ),
        E(
            "Build a frequency table",
            "Count red, blue and red.",
            "red has count 2 and blue has count 1.",
            r"""m:=map[string]int{}; for _,v:=range []string{"red","blue","red"} { m[v]++ }; check(m["red"]==2 && m["blue"]==1,"counts")""",
            "Missing counts start at the zero value, which is useful here because zero is the correct additive identity.",
        ),
        E(
            "Sort report keys",
            "Extract keys beta and alpha and sort them.",
            "The first output key is alpha.",
            r"""m:=map[string]int{"beta":2,"alpha":1}; keys:=[]string{}; for k:=range m { keys=append(keys,k) }; sort.Strings(keys); check(keys[0]=="alpha" && keys[1]=="beta","sorted keys")""",
            "Sorting makes the presentation contract explicit. Repeatedly observing one map order never makes it guaranteed.",
        ),
        E(
            "Observe assigned map aliasing",
            "Assign a map to another variable and update through the second.",
            "Both names observe the changed entry.",
            r"""a:=map[string]int{"x":1}; b:=a; b["x"]=2; check(a["x"]==2,"map alias")""",
            "The assignment does not recursively clone map entries. Independent snapshots require a deliberate copy and a policy for nested mutable values.",
        ),
        E(
            "Remove an absent key safely",
            "Delete a missing key and then an existing key.",
            "The map ends empty without a failure.",
            r"""m:=map[string]int{"x":1}; delete(m,"absent"); delete(m,"x"); check(len(m)==0,"delete")""",
            "Idempotent deletion is helpful for cleanup: repeating the same intent does not introduce a new error for an already absent entry.",
        ),
        E(
            "Transfer nil read behavior",
            "Read a missing key from a nil map.",
            "The value is 0 and presence is false.",
            r"""var m map[string]int; v,ok:=m["x"]; check(v==0 && !ok,"nil read")""",
            "This safe read does not mean a nil map is writable. Initialize storage before assignment instead of using a panic as ordinary control flow.",
        ),
    ],
    imports="sort",
)

add(
    "Strings, bytes, runes and Unicode boundaries",
    """A Go string is an immutable sequence of bytes, not necessarily valid Unicode text. Source string literals are commonly UTF-8, but strings can contain arbitrary bytes. Indexing a string returns one byte. Ranging over a string decodes runes, which are Unicode code points; malformed encodings produce replacement runes. A user-perceived character can contain multiple code points, such as a letter plus combining accent. Byte length, rune count and displayed-character count therefore answer different questions. Choose a unit before slicing, counting or truncating text. Immutability protects a string value, while conversion to a mutable byte slice creates a separate editing representation.""",
    """len(text) counts bytes. []byte(text) and []rune(text) choose different element units. utf8.RuneCountInString counts decoded code points, while utf8.ValidString checks encoding validity. strings.TrimSpace removes surrounding Unicode whitespace and returns a string. A rune literal uses single quotes and has a numeric code-point value; a string literal uses double quotes.""",
    [
        ("Byte", "An eight-bit storage unit."),
        ("Rune", "Go alias for int32, commonly representing a Unicode code point."),
        ("UTF-8", "A variable-width encoding of Unicode code points."),
    ],
    [
        E(
            "Count two units",
            "Inspect A followed by a smiling face.",
            "There are 5 bytes and 2 runes.",
            r"""text:="A🙂"; check(len(text)==5 && utf8.RuneCountInString(text)==2,"text units")""",
            "The ASCII letter occupies one byte and this emoji occupies four. Neither count is a general grapheme-cluster algorithm.",
        ),
        E(
            "Edit a copied byte slice",
            "Convert cat to bytes, replace c with b and retain the original.",
            "The original is cat and the new string is bat.",
            r"""original:="cat"; data:=[]byte(original); data[0]='b'; check(original=="cat" && string(data)=="bat","copy edit")""",
            "The mutable byte slice provides an explicit editing boundary. This example uses ASCII so replacing one byte does not split a multibyte encoding.",
        ),
        E(
            "Reject malformed encoding",
            "Build a string from the single byte 0xff.",
            "UTF-8 validation returns false.",
            r"""text:=string([]byte{0xff}); check(!utf8.ValidString(text),"invalid encoding")""",
            "A string can exist without being valid UTF-8. Validation is a separate input contract, not an automatic property of the string type.",
        ),
        E(
            "Slice by rune position",
            "Convert A and the emoji to runes and retain the second rune.",
            "The resulting string is the intact emoji.",
            r"""r:=[]rune("A🙂"); check(string(r[1:])=="🙂","rune slice")""",
            "The conversion makes code-point indexing explicit. Arbitrary byte slicing could instead cut through the emoji encoding.",
        ),
        E(
            "Separate combining forms",
            "Count runes in e followed by a combining accent.",
            "There are 2 runes even though it can display as one character.",
            r"""text:="e\u0301"; check(utf8.RuneCountInString(text)==2,"combining")""",
            "A code point is not always a complete displayed character. Normalization and grapheme segmentation are distinct operations beyond this counting primitive.",
        ),
        E(
            "Transfer a whitespace policy",
            "Trim surrounding whitespace from a label without changing its internal space.",
            "The result is blue sky.",
            r"""label:=strings.TrimSpace(" \tblue sky\n"); check(label=="blue sky","trim")""",
            "Trimming is a domain policy. It is appropriate for this display label, but could corrupt a field where leading spaces are meaningful.",
        ),
    ],
    imports="unicode/utf8 strings",
)

add(
    "Structs and explicit domain models",
    """A struct groups named fields into one value. Naming fields makes the domain visible: a coordinate with X and Y is more readable than an unexplained two-element slice. Struct assignment copies fields, but fields containing slices, maps or pointers can continue to share referenced storage. Exported fields begin with uppercase letters, which also affects reflection-based encoders. Zero values are predictable, yet not every zero struct is a valid domain object. A constructor-like function can validate inputs and return a value plus error, but Go does not require all construction to pass through such a function. Choose visibility and validation together.""",
    """type Point struct { X, Y int } creates a named type with fields. Point{X:2,Y:3} uses keyed construction, so field meaning survives reordering. p.X selects a field. Comparable structs can be compared with == only if every field is comparable. A struct with a slice cannot be a map key. An anonymous embedded field promotes selectors but does not create class inheritance.""",
    [
        ("Struct", "A value composed of named fields."),
        ("Keyed literal", "Construction naming the field for each supplied value."),
        ("Shallow copy", "A field-by-field copy that can retain referenced storage."),
    ],
    [
        E(
            "Model a coordinate",
            "Construct Point with X 2 and Y 3 and calculate Manhattan distance from the origin.",
            "The distance is 5.",
            r"""p:=Point{X:2,Y:3}; check(p.X+p.Y==5,"point")""",
            "Named fields document the coordinate meaning. This tiny case assumes nonnegative coordinates; a general distance function needs absolute values.",
        ),
        E(
            "Observe scalar copy",
            "Copy a Point and change the copied X field.",
            "The original X remains 2.",
            r"""a:=Point{X:2,Y:3}; b:=a; b.X=9; check(a.X==2 && b.X==9,"struct copy")""",
            "Both fields contain scalar values, so assignment produces independent field storage.",
        ),
        E(
            "Expose a shallow field",
            "Copy a Batch struct containing a slice and mutate its first item.",
            "The original batch observes the mutation.",
            r"""a:=Batch{Items:[]int{1,2}}; b:=a; b.Items[0]=9; check(a.Items[0]==9,"shallow field")""",
            "The copied slice descriptor still points to the same backing array. A struct wrapper does not change the ownership semantics of its fields.",
        ),
        E(
            "Inspect zero state",
            "Declare a Point without a literal.",
            "Both coordinates are 0.",
            r"""var p Point; check(p==(Point{X:0,Y:0}),"struct zero")""",
            "Field zero values compose into a deterministic struct zero value. Whether that represents a meaningful domain object is a separate contract.",
        ),
        E(
            "Use a comparable key",
            "Store a label keyed by Point and retrieve it with an equal Point.",
            "The equal coordinate finds origin.",
            r"""m:=map[Point]string{{X:0,Y:0}:"origin"}; check(m[Point{}]=="origin","struct key")""",
            "Equality compares corresponding fields. Replacing a field with a slice would make this struct noncomparable and the map key invalid at compilation.",
        ),
        E(
            "Transfer validation",
            "Construct a named item with an empty name and then a valid name.",
            "The empty name is rejected; the valid name is retained.",
            r"""_,err:=newItem(""); check(err!=nil,"blank name"); item,err:=newItem("sample"); check(err==nil && item.Name=="sample","valid item")""",
            "Validation at construction reduces invalid states, but exported fields still allow later assignment. A stricter API would keep invariant-bearing fields unexported.",
        ),
    ],
    imports="errors",
    helper=r"""type Point struct { X,Y int }
type Batch struct { Items []int }
type Item struct { Name string }
func newItem(name string) (Item,error) { if name=="" { return Item{},errors.New("name required") }; return Item{Name:name},nil }""",
)

add(
    "Pointers, mutation and allocation lifetimes",
    """A pointer contains the address of a value. Passing a pointer still copies the pointer value, but both copies identify the same target. This is useful when mutation is the intended contract and dangerous when callers expect isolation. Go\'s garbage collector keeps reachable objects alive, so returning a pointer to a local variable is valid; the compiler decides where storage must live. That does not make every pointer safe to use: nil has no target and dereferencing it panics. Ordinary Go pointers do not support arithmetic. Use a value receiver or an independent copy when shared mutation is unnecessary, and make optional pointer semantics explicit.""",
    """&value obtains an address and *pointer dereferences it. In a type, *Point means a pointer to Point. new(T) returns a pointer to a zero T; it does not initialize maps or channels stored inside T. Selectors automatically follow a pointer to a struct, so p.X is convenient syntax for field access through p. A nil check guards dereference only when no unsynchronized writer can change the state between those operations.""",
    [
        ("Pointer", "A value identifying another value in memory."),
        ("Dereference", "Reading or writing the target of a pointer."),
        ("Reachability", "Whether live program state still refers to an allocated object."),
    ],
    [
        E(
            "Mutate through a pointer",
            "Create an integer 4 and increment it through a helper receiving its address.",
            "The caller value becomes 5.",
            r"""n:=4; increment(&n); check(n==5,"pointer mutation")""",
            "The helper changes the shared target, not the caller variable that stores the pointer. The mutation contract must be visible at the call site.",
        ),
        E(
            "Return a live value",
            "Return a pointer to a local integer initialized to 7.",
            "The returned pointer remains valid and reads 7.",
            r"""p:=seven(); check(*p==7,"returned pointer")""",
            "Go extends storage lifetime as needed. Stack-versus-heap placement is an implementation decision and should not be guessed from the lexical block alone.",
        ),
        E(
            "Guard absence",
            "Represent an optional integer with a nil pointer and inspect it without dereferencing.",
            "The pointer is absent.",
            r"""var p *int; check(p==nil,"nil pointer")""",
            "Nil is a useful absence marker only when callers check it. It is different from a pointer to an integer whose value is zero.",
        ),
        E(
            "Allocate a zero target",
            "Use new(int) and compare pointer presence with its stored value.",
            "The pointer is non-nil and its target is 0.",
            r"""p:=new(int); check(p!=nil && *p==0,"new zero")""",
            "Allocation and initialization are separate questions. A target can exist while carrying its type zero value.",
        ),
        E(
            "Separate copy and target",
            "Copy the integer behind a pointer, then change the original target.",
            "The copied integer remains 3 while the target becomes 9.",
            r"""n:=3; p:=&n; copied:=*p; *p=9; check(copied==3 && n==9,"copy target")""",
            "Dereferencing to obtain a scalar value copies that scalar. Retaining a pointer would instead retain access to the changing target.",
        ),
        E(
            "Transfer an optional update",
            "Implement setIfPresent so a nil pointer is a harmless no-op and a present pointer changes.",
            "The absent call returns false; the present value becomes 8.",
            r"""check(!setIfPresent(nil,8),"absent update"); n:=1; check(setIfPresent(&n,8) && n==8,"present update")""",
            "An explicit boolean tells the caller whether the update happened. Silently treating absent and updated states as identical would hide useful information.",
        ),
    ],
    helper=r"""func increment(p *int) { *p = *p + 1 }
func seven() *int { n:=7; return &n }
func setIfPresent(p *int,v int) bool { if p==nil { return false }; *p=v; return true }""",
)

add(
    "Methods, interfaces and the typed-nil trap",
    """A method associates behavior with a named type. An interface describes a set of methods, and a concrete type satisfies it implicitly by providing that set. This encourages small interfaces defined by the consumer instead of deep inheritance hierarchies. A value receiver receives a copy; a pointer receiver can mutate its target and has a different method set. An interface value contains both dynamic type information and a dynamic value. It is nil only when both are absent. Therefore an interface holding a typed nil pointer is not a nil interface. This matters especially when returning errors or optional implementations across package boundaries.""",
    """func (c Counter) Value() int declares a value receiver. func (c *Counter) Add(n int) uses a pointer receiver. type Valuer interface { Value() int } declares required behavior. A type assertion value, ok := item.(Concrete) checks a dynamic type safely. Prefer the comma-ok form when failure is expected, rather than a panic-producing assertion.""",
    [
        ("Method set", "The methods available for a type and its pointer form."),
        ("Interface", "A behavior contract expressed as methods."),
        ("Dynamic type", "The concrete type stored inside an interface value."),
    ],
    [
        E(
            "Dispatch through behavior",
            "Store Counter with value 3 in a Valuer interface.",
            "Calling Value returns 3.",
            r"""var v Valuer=Counter{N:3}; check(v.Value()==3,"interface dispatch")""",
            "The concrete type satisfies the interface without declaring that relationship. The caller depends only on the method contract.",
        ),
        E(
            "Mutate through a method",
            "Call Add on a pointer to Counter starting at 3.",
            "Its value becomes 5.",
            r"""c:=Counter{N:3}; c.Add(2); check(c.N==5,"pointer receiver")""",
            "The language can take the address of this addressable variable for the method call. The pointer receiver makes the mutation effective on the original value.",
        ),
        E(
            "Trace a value receiver",
            "Call a value-receiver helper that increments only its receiver copy.",
            "The returned value is 4 but the original remains 3.",
            r"""c:=Counter{N:3}; got:=c.Incremented(); check(got==4 && c.N==3,"receiver copy")""",
            "Changing a value receiver's scalar field changes the copied receiver. Fields that reference shared storage still require separate ownership reasoning.",
        ),
        E(
            "Expose typed nil",
            "Put a nil pointer to Counter inside an empty interface.",
            "The interface is not nil.",
            r"""var p *Counter; var item any=p; check(item!=nil,"typed nil")""",
            "The interface contains the dynamic type *Counter even though its dynamic pointer is nil. Comparing only the interface to nil does not test target availability.",
        ),
        E(
            "Use safe dynamic inspection",
            "Assert that an interface containing a string is an int with comma-ok.",
            "The assertion reports false without panicking.",
            r"""var item any="three"; _,ok:=item.(int); check(!ok,"type assertion")""",
            "A failed dynamic conversion is ordinary evidence when the input type is uncertain. A single-value assertion would turn this expected mismatch into a panic.",
        ),
        E(
            "Transfer substitutability",
            "Implement a second Valuer type returning a fixed value and use the same consuming helper.",
            "Both implementations can be read through one contract.",
            r"""check(readValue(Counter{N:2})==2 && readValue(Fixed(8))==8,"substitution")""",
            "The consumer should not depend on concrete fields or perform a type switch unless its real contract requires different behavior.",
        ),
    ],
    helper=r"""type Counter struct { N int }
func (c Counter) Value() int { return c.N }
func (c *Counter) Add(n int) { c.N+=n }
func (c Counter) Incremented() int { c.N++; return c.N }
type Valuer interface { Value() int }
type Fixed int
func (f Fixed) Value() int { return int(f) }
func readValue(v Valuer) int { return v.Value() }""",
)

add(
    "Errors as values and preserving causal context",
    """Errors describe unsuccessful operations without forcing every failure into panic recovery. A function returning a value and error makes the caller choose what to do next. The error chain should preserve both human context and a machine-inspectable cause. Wrapping with fmt.Errorf and %w adds context while errors.Is and errors.As can inspect underlying identity or type. Comparing formatted text is brittle because wording is presentation, not a stable contract. A nil error means the operation succeeded according to its API; it does not prove every downstream interpretation is valid. Handle failures where you can add useful context, recover deliberately or report them accurately.""",
    """errors.New constructs an error value. fmt.Errorf("read: %w", err) wraps an existing cause. errors.Is follows supported wrapping relationships to compare a sentinel; errors.As finds an error assignable to a target type. Return nil for a successful error result, not an interface containing a typed nil pointer. Avoid logging and returning the same error at every layer because repeated messages can obscure the causal chain.""",
    [
        ("Sentinel error", "A named error value used as an identity contract."),
        ("Wrapping", "Adding context while preserving an underlying cause."),
        ("Recovery policy", "A deliberate response to a particular failure class."),
    ],
    [
        E(
            "Preserve a cause",
            "Wrap ErrMissing with a record-reading context.",
            "errors.Is still recognizes ErrMissing.",
            r"""err:=fmt.Errorf("read record: %w",ErrMissing); check(errors.Is(err,ErrMissing),"wrapped cause")""",
            "%w exposes the cause to the error-inspection protocol. Replacing it with %v would format the cause as text but lose that wrapping relationship.",
        ),
        E(
            "Reject text equality",
            "Construct two separate errors with the same wording.",
            "Their identities differ.",
            r"""a:=errors.New("missing"); b:=errors.New("missing"); check(!errors.Is(a,b),"identity not text")""",
            "A matching message does not establish the same error contract. Use an exported sentinel or typed error only when callers should rely on that distinction.",
        ),
        E(
            "Inspect a typed boundary",
            "Return a LimitError carrying an allowed maximum and inspect it with errors.As.",
            "The extracted limit is 3.",
            r"""err:=fmt.Errorf("request: %w",&LimitError{Max:3}); var limit *LimitError; check(errors.As(err,&limit) && limit.Max==3,"typed error")""",
            "The type carries structured information without parsing presentation text. The target passed to errors.As is a pointer to the variable that should receive the matching error.",
        ),
        E(
            "Handle successful parsing",
            "Parse valid integer text and check error before value use.",
            "The result is 42 and the error is nil.",
            r"""v,err:=strconv.Atoi("42"); check(err==nil && v==42,"valid parse")""",
            "The success branch establishes that the returned value is usable. The ordering prevents an unvalidated value from leaking into a later calculation.",
        ),
        E(
            "Classify invalid parsing",
            "Parse malformed integer text and inspect its NumError.",
            "The typed parse error is present.",
            r"""_,err:=strconv.Atoi("4x"); var number *strconv.NumError; check(errors.As(err,&number),"parse error")""",
            "Typed inspection supports a specific response to invalid input. It should not be confused with retrying a transient external outage.",
        ),
        E(
            "Transfer joined failures",
            "Join missing and permission errors and inspect both causes.",
            "Both sentinels remain discoverable.",
            r"""err:=errors.Join(ErrMissing,ErrDenied); check(errors.Is(err,ErrMissing)&&errors.Is(err,ErrDenied),"joined errors")""",
            "Multiple failures can matter during cleanup or validation. Joining retains their identities instead of discarding all but the last failure.",
        ),
    ],
    imports="errors strconv",
    helper=r"""var ErrMissing=errors.New("missing record")
var ErrDenied=errors.New("access denied")
type LimitError struct { Max int }
func (e *LimitError) Error() string { return fmt.Sprintf("limit %d",e.Max) }""",
    source="https://pkg.go.dev/errors",
)

add(
    "Defer, cleanup and deliberate panic boundaries",
    """defer schedules a function call to execute when the surrounding function returns. It is a resource-lifetime tool, not a general background execution mechanism. Deferred calls run in last-in-first-out order, and their arguments are evaluated when the defer statement executes. Closures can instead read variables at the later execution time. panic unwinds the current goroutine\'s stack, running defers; recover can intercept it only in the appropriate deferred call during that unwind. Expected invalid input should normally be returned as an error. Recovering every panic and returning a success-shaped value conceals defects and can leave callers unable to distinguish completed work from aborted work.""",
    """defer cleanup() registers a call. defer func(){ ... }() registers a closure. A helper function is useful when each loop iteration needs its own cleanup boundary; deferring inside a long loop otherwise accumulates cleanup until the whole function returns. recover returns the active panic value when called correctly from a deferred function. A named return variable can be changed by deferred code, which is powerful but can make flow harder to read.""",
    [
        ("Deferred call", "A call executed when the surrounding function exits."),
        ("Stack unwind", "Returning through active frames after a panic."),
        ("Cleanup boundary", "The scope that owns and releases a resource."),
    ],
    [
        E(
            "Trace cleanup order",
            "Register first and second cleanup markers and return.",
            "The observed order is second then first.",
            r"""check(deferOrder()=="second,first","defer order")""",
            "The last registered cleanup runs first. This naturally unwinds nested acquisitions in the opposite order from acquisition.",
        ),
        E(
            "Compare captured arguments",
            "Defer a call with x as an argument, then change x.",
            "The deferred argument retains the earlier value 1.",
            r"""check(deferArgument()==1,"argument evaluation")""",
            "Call arguments are evaluated at registration. This differs from a closure that refers to x and reads it when the closure later runs.",
        ),
        E(
            "Compare a closure read",
            "Defer a closure reading x, then change x to 2.",
            "The closure observes 2.",
            r"""check(deferClosure()==2,"closure read")""",
            "The closure refers to the variable. Whether this is useful or misleading depends on the intended observation time.",
        ),
        E(
            "Contain a deliberate panic",
            "Panic with the known value broken inside a helper that recovers it.",
            "The helper reports broken explicitly.",
            r"""check(recoverKnown()=="broken","recovered value")""",
            "The recovery boundary converts this deliberate fixture into inspectable evidence. It does not justify swallowing arbitrary production panics.",
        ),
        E(
            "Preserve cleanup during failure",
            "Register cleanup and then panic inside a recovered helper.",
            "The cleanup marker is still set.",
            r"""check(cleanedAfterPanic(),"cleanup on panic")""",
            "Stack unwinding runs deferred cleanup before the outer recovery returns. Resource-release logic must still be safe when work is incomplete.",
        ),
        E(
            "Transfer function-scoped cleanup",
            "Run three helpers, each with its own deferred marker.",
            "All three markers are present after the loop.",
            r"""count:=0; for i:=0;i<3;i++ { scopedCleanup(&count) }; check(count==3,"iteration cleanup")""",
            "A helper creates a cleanup boundary per iteration. A defer in the outer loop's function would postpone all three releases until that outer function returned.",
        ),
    ],
    imports="strings",
    helper=r"""func deferOrder() (result string) { values:=[]string{}; defer func(){result=strings.Join(values,",")}(); defer func(){values=append(values,"first")}(); defer func(){values=append(values,"second")}(); return }
func deferArgument() (result int) { x:=1; defer func(v int){result=v}(x); x=2; return }
func deferClosure() (result int) { x:=1; defer func(){result=x}(); x=2; return }
func recoverKnown() (result string) { defer func(){ if v:=recover(); v!=nil { result=fmt.Sprint(v) } }(); panic("broken") }
func cleanedAfterPanic() (cleaned bool) { defer func(){recover()}(); defer func(){cleaned=true}(); panic("fixture") }
func scopedCleanup(count *int) { defer func(){*count=*count+1}() }""",
)

add(
    "Packages, modules and reproducible project boundaries",
    """A package is a compilation and visibility boundary; a module is a versioned collection of packages described by go.mod. An import path identifies a package, not an operating-system filename. Capitalized declarations are exported to other packages. The main package creates an executable, while reusable packages expose focused APIs. go.sum records module-content checksums but is not a substitute for reviewing dependency changes. An offline classroom pad cannot become a multi-file dependency project by containing a go.mod string. This lesson executes standard-library boundary examples and separately teaches the real project layout. Keep generated outputs, dependency selection and application source under distinct review.""",
    """The standard library already contains packages such as path, strings and strconv. An alias in an import declaration changes the local selector name, not the dependency\'s identity. For a real project, run go mod init example.org/learning/report in a prepared directory, place reusable code under a package folder, and use go test ./... plus go build ./cmd/report. Pin reviewed dependency versions with go get and commit go.mod and go.sum. Dependency retrieval is explicit setup, never a side effect of opening a lesson.""",
    [
        ("Module", "A versioned group of Go packages rooted at go.mod."),
        (
            "Exported name",
            "A declaration visible outside its package because its name begins uppercase.",
        ),
        ("Import path", "The logical identity used to select a package."),
    ],
    [
        E(
            "Use a package boundary",
            "Join logical slash-separated path segments with path.Join.",
            "The result is reports/daily.json.",
            r"""check(path.Join("reports","daily.json")=="reports/daily.json","path package")""",
            "path works with slash-separated logical paths. filepath is a different package whose behavior follows the host operating system.",
        ),
        E(
            "Compose standard-library APIs",
            "Trim and parse the text containing spaces around 12.",
            "The parsed value is 12.",
            r"""v,err:=strconv.Atoi(strings.TrimSpace(" 12 ")); check(err==nil && v==12,"package composition")""",
            "Each package contributes a small contract. Trimming is an explicit input policy, while numeric parsing remains independently fallible.",
        ),
        E(
            "Inspect exported spelling",
            "Compare a public API spelling with its lower-case variant as identifiers in a naming check.",
            "The public spelling begins with an uppercase rune.",
            r"""name:="ParseInt"; check(unicode.IsUpper([]rune(name)[0]),"export convention")""",
            "This checks the naming convention rather than trying to access an unexported symbol. Actual visibility is enforced by the compiler across package boundaries.",
        ),
        E(
            "Keep logical imports separate",
            "Clean a logical path containing a parent component.",
            "reports/tmp/../daily becomes reports/daily.",
            r"""check(path.Clean("reports/tmp/../daily")=="reports/daily","logical clean")""",
            "Cleaning a path is not authorization to access it. Real filesystem access needs confinement and symlink-aware policy, taught later.",
        ),
        E(
            "Reject malformed input at an API boundary",
            "Parse a nonnumeric public input after trimming.",
            "The numeric error remains non-nil.",
            r"""_,err:=strconv.Atoi(strings.TrimSpace(" none ")); check(err!=nil,"boundary error")""",
            "Packaging does not remove the need for validation. The wrapper should preserve a cause rather than return a plausible zero as if parsing succeeded.",
        ),
        E(
            "Transfer an API contract",
            "Build a deterministic report name from a validated positive integer.",
            "The resulting logical name is reports/day-3.json.",
            r"""day,err:=strconv.Atoi("3"); check(err==nil && day>0,"day"); name:=path.Join("reports",fmt.Sprintf("day-%d.json",day)); check(name=="reports/day-3.json","report name")""",
            "The boundary validates a domain value before formatting it into a path. Arbitrary user path fragments are not accepted by this contract.",
        ),
    ],
    imports="path strconv strings unicode",
    source="https://go.dev/doc/modules/managing-dependencies",
    boundary="""### Prepared external project

The browser reference is deliberately one file. To practice real packages, create `go.mod`, `cmd/report/main.go` and `internal/report/report.go` in a separately prepared project. The command package imports the internal package; the reusable package must not import the command package. Run `go test ./...` from the module root. A circular import is a design error, not something to bypass by changing build order. Standard-library-only projects can be built offline after the Go toolchain is installed.""",
)

add(
    "Table-driven tests and useful counterexamples",
    """Tests are executable claims about behavior. A test should distinguish the intended implementation from a plausible wrong one. Table-driven testing records input and expectation as data, then applies the same assertion logic to each case. Normal cases show use, boundary cases define edges, and invalid cases define failure behavior. A reference example in a single pad uses explicit checks; a real Go test lives in a file ending _test.go and receives *testing.T. Tests must not depend on global ordering, current time or a network service unless those dependencies are deliberately controlled. Coverage describes executed code, not the strength of the assertions.""",
    """A test table is often a slice of anonymous structs with name, input and want fields. In a prepared project, func TestName(t *testing.T) is discovered by go test, and t.Run creates named subtests. Compare actual and expected values directly; include the case name in failure messages. Fuzz tests describe invariants across generated inputs, but they need a bounded execution budget and persistent regression seeds. Do not treat successful compilation as a behavior test.""",
    [
        ("Test oracle", "The independent rule determining an expected result."),
        ("Boundary case", "An input at the edge of an accepted domain."),
        ("Regression case", "A retained input that exposes a previously observed defect."),
    ],
    [
        E(
            "Build a named table",
            "Test clamp with values below, inside and above the range 0 to 10.",
            "The outputs are 0, 4 and 10.",
            r"""cases:=[]struct{in,want int}{{-2,0},{4,4},{12,10}}; for _,tc:=range cases { check(clamp(tc.in)==tc.want,"clamp table") }""",
            "A wrong implementation that only returns its input fails the outside cases; one that always returns an endpoint fails the interior case.",
        ),
        E(
            "Include exact endpoints",
            "Test clamp at 0 and 10.",
            "Both endpoints are preserved.",
            r"""check(clamp(0)==0 && clamp(10)==10,"endpoints")""",
            "Endpoint tests distinguish inclusive boundaries from off-by-one policies. They should be named in the API contract.",
        ),
        E(
            "Check idempotence",
            "Apply clamp twice to values -2, 4 and 12.",
            "Applying it twice gives the same result as once.",
            r"""for _,x:=range []int{-2,4,12} { check(clamp(clamp(x))==clamp(x),"idempotence") }""",
            "This is a property rather than a single expected output. It complements concrete cases but would not reject every wrong constant function on its own.",
        ),
        E(
            "Reject a plausible mutant",
            "Compare the correct clamp with a mutant that incorrectly caps at 9.",
            "Input 10 distinguishes them.",
            r"""check(clamp(10)!=mutantClamp(10),"mutant rejected")""",
            "A test's value is visible when it rejects a realistic defect. Merely executing both functions without comparing them provides no such evidence.",
        ),
        E(
            "Cover a range invariant",
            "Check all integer inputs from -20 through 20.",
            "Every result lies between 0 and 10.",
            r"""for x:=-20;x<=20;x++ { v:=clamp(x); check(v>=0 && v<=10,"range invariant") }""",
            "This bounded exhaustive set supports the invariant for its chosen domain. It is not a proof about every possible integer or an excuse to remove exact cases.",
        ),
        E(
            "Transfer a fresh regression",
            "Retain input 11 as a regression for an implementation that forgets the upper cap.",
            "The result is 10.",
            r"""check(clamp(11)==10,"upper regression")""",
            "The smallest counterexample just beyond the boundary often explains the defect better than a large random value. Keep it after the fix.",
        ),
    ],
    helper=r"""func clamp(x int) int { if x<0 {return 0}; if x>10{return 10}; return x }
func mutantClamp(x int) int { if x<0{return 0}; if x>9{return 9}; return x }""",
    source="https://pkg.go.dev/testing",
)

add(
    "Generics and constraints without losing semantics",
    """Generics express algorithms whose structure is shared across several types. A type parameter is constrained by the operations the algorithm requires. comparable permits equality and map keys; it does not permit ordering or arithmetic. A constraint using a type set can admit underlying integer types with the ~ operator. Generic code still needs a meaningful domain contract: adding signed integers can overflow, floating equality can surprise, and pointer equality is not deep value equality. Prefer a normal function when only one concrete type is useful. A useful generic abstraction removes real duplication while preserving clear errors and readable call sites.""",
    """`func first[T any](items []T) (T,bool)` declares a type parameter `T`. `var zero T` obtains its zero value for an empty result. A custom constraint such as `interface { ~int | ~int64 }` admits named types with those underlying types. Type inference often determines `T` from arguments. A constraint belongs to compile-time capability checking; it is not runtime validation of application data.""",
    [
        ("Type parameter", "A placeholder type selected for a generic instantiation."),
        ("Constraint", "The allowed types and operations for a type parameter."),
        ("Type inference", "Deriving a type argument from call arguments."),
    ],
    [
        E(
            "Reuse an element contract",
            "Call first with an integer slice and a string slice.",
            "The results are 4 and red with presence true.",
            r"""a,okA:=first([]int{4,5}); b,okB:=first([]string{"red","blue"}); check(okA&&okB&&a==4&&b=="red","generic first")""",
            "The algorithm needs indexing and length, not knowledge of the element representation. That makes any an honest constraint here.",
        ),
        E(
            "Handle a generic empty value",
            "Call first with an empty integer slice.",
            "The result is zero with presence false.",
            r"""v,ok:=first([]int{}); check(v==0&&!ok,"empty generic")""",
            "A zero value alone cannot distinguish an empty input from a first element equal to zero. The boolean preserves that information.",
        ),
        E(
            "Preserve stable uniqueness",
            "Deduplicate 2, 1, 2 while preserving first occurrence.",
            "The result is 2 then 1.",
            r"""v:=unique([]int{2,1,2}); check(len(v)==2&&v[0]==2&&v[1]==1,"unique order")""",
            "A map tracks membership while the result slice preserves order. Returning map keys directly would lose the ordering contract.",
        ),
        E(
            "Admit a named underlying type",
            "Sum two values of a named Count type.",
            "The result is Count(7).",
            r"""check(sumInts([]Count{3,4})==Count(7),"underlying type")""",
            "The tilde constraint admits the underlying int representation while preserving the named result type.",
        ),
        E(
            "Test the empty sum identity",
            "Sum an empty int64 slice.",
            "The result is int64 zero.",
            r"""check(sumInts([]int64{})==0,"generic identity")""",
            "The identity must make sense for every allowed type. Expanding a constraint to unrelated types can invalidate an otherwise convenient implementation.",
        ),
        E(
            "Transfer equality semantics",
            "Deduplicate strings with different case.",
            "Red and red remain distinct.",
            r"""v:=unique([]string{"Red","red","Red"}); check(len(v)==2,"case policy")""",
            "comparable uses the language equality operation. Case folding or domain normalization would need an explicit preprocessing policy, not a hidden generic assumption.",
        ),
    ],
    helper=r"""type Count int
type Integer interface { ~int | ~int64 }
func first[T any](items []T) (T,bool) { if len(items)==0 {var zero T;return zero,false};return items[0],true }
func unique[T comparable](items []T) []T { seen:=map[T]bool{};out:=[]T{};for _,x:=range items {if !seen[x]{seen[x]=true;out=append(out,x)}};return out }
func sumInts[T Integer](items []T) T {var out T;for _,x:=range items {out+=x};return out }""",
    source="https://go.dev/doc/tutorial/generics",
)

add(
    "Closures, callbacks and controlled iteration",
    """A function value can be stored, passed and called like other values. A closure also refers to variables from its surrounding scope. That makes callbacks concise, but it makes lifetime and mutation worth tracing explicitly. Two closures can intentionally share one variable; two independent constructor calls can create separate state. A callback contract should describe when it is called, whether it may stop iteration and whether it can retain supplied values. Iterator-style APIs can avoid allocating intermediate slices, but early termination and cleanup must still be well defined. Do not confuse deferred execution with concurrent execution: a closure is not a goroutine by itself.""",
    """func(int) int is a function type. An anonymous func literal creates a function value. Returning a closure from makeCounter retains access to its captured count. A visitor returning bool can stop a traversal when false. Passing a function as a parameter makes selection policy explicit without an interface type when only one operation is needed.""",
    [
        ("Closure", "A function value that refers to surrounding variables."),
        ("Callback", "A function supplied for another operation to invoke."),
        ("Early termination", "Ending traversal once the caller has enough evidence."),
    ],
    [
        E(
            "Capture a changing variable",
            "Create a closure referring to factor, change factor, then call it.",
            "The closure uses the new factor 3.",
            r"""factor:=2; multiply:=func(x int)int{return factor*x}; factor=3; check(multiply(4)==12,"capture variable")""",
            "The closure refers to the variable rather than freezing its initial value. Explicitly copying a value into a new binding produces a different contract.",
        ),
        E(
            "Create independent counters",
            "Construct two counter closures and call the first twice.",
            "The first returns 1 then 2; the second starts at 1.",
            r"""a,b:=makeCounter(),makeCounter(); check(a()==1&&a()==2&&b()==1,"independent closures")""",
            "Each constructor invocation creates its own captured state. Sharing a single returned closure would share that state instead.",
        ),
        E(
            "Inject a transformation",
            "Map a doubling callback over 1, 2 and 3.",
            "The result is 2, 4 and 6.",
            r"""v:=mapInts([]int{1,2,3},func(x int)int{return 2*x}); check(len(v)==3&&v[0]==2&&v[2]==6,"callback")""",
            "The traversal owns iteration while the callback owns the element transformation. This separation is useful only when both contracts remain simple.",
        ),
        E(
            "Stop a visitor early",
            "Visit 1 through 5 and stop after observing 3.",
            "Exactly three values are visited.",
            r"""count:=0; visit(5,func(x int)bool{count++;return x<3}); check(count==3,"early stop")""",
            "The stop decision occurs after the third callback. Counting callbacks distinguishes stopping before a value from stopping after observing it.",
        ),
        E(
            "Handle an empty traversal",
            "Visit an empty range with a callback that would increment a count.",
            "The callback is never invoked.",
            r"""count:=0; visit(0,func(x int)bool{count++;return true}); check(count==0,"empty callback")""",
            "A caller should not need a fabricated sentinel callback to learn that there were no values. Empty behavior belongs in the traversal contract.",
        ),
        E(
            "Transfer explicit state",
            "Collect only even values from a bounded visitor.",
            "The collected values are 2 and 4.",
            r"""out:=[]int{};visit(4,func(x int)bool{if x%2==0{out=append(out,x)};return true});check(len(out)==2&&out[0]==2&&out[1]==4,"collector")""",
            "The closure intentionally mutates caller-owned collection state. Concurrent invocation would require a different synchronization contract; this visitor is sequential.",
        ),
    ],
    helper=r"""func makeCounter() func() int {n:=0;return func()int{n++;return n}}
func mapInts(items []int,f func(int)int) []int {out:=make([]int,len(items));for i,x:=range items{out[i]=f(x)};return out}
func visit(limit int,f func(int)bool){for i:=1;i<=limit;i++{if !f(i){return}}}""",
)
