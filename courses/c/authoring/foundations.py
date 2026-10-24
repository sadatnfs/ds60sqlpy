"""Original C17 foundations with only defined, bounded executable examples."""

from render import add
from render import case as E

add(
    "Source, compilation, linking and checked execution",
    """C source is text describing declarations and operations. The preprocessor handles directives, the compiler translates a translation unit, and the linker combines machine-code objects with required libraries. The executable is a separate artifact from main.c. A syntax error prevents compilation; an unresolved symbol prevents linking; an assertion can fail only after execution begins. These stages require different diagnoses. C does not automatically validate every runtime memory operation, so successful compilation is a starting point rather than a safety proof. Begin with independently checked scalar results before learning pointers and resource ownership.""",
    """#include makes header declarations available. int main(void) is an entrypoint with no parameters; returning zero signals successful termination. Braces form a block and semicolons finish most statements. printf formats values, while puts writes a string plus a newline. assert from assert.h checks a condition when NDEBUG is not defined. %d expects an int, and a mismatched format argument can be undefined behavior.""",
    [
        ("Translation unit", "The source after preprocessing, compiled as one unit."),
        ("Linker", "The tool resolving references among compiled objects and libraries."),
        ("Assertion", "An explicit runtime check of a claimed property."),
    ],
    [
        E(
            "Check a first value",
            "Store 2 plus 3 in an int.",
            "The stored value is 5.",
            r"""int total = 2 + 3; CHECK(total == 5);""",
            "The expectation is known independently of the program. A print statement alone would not reject a wrong calculation.",
        ),
        E(
            "Format a checked result",
            "Format total=5 into a bounded character buffer.",
            "The result length is 7 and text is total=5.",
            r"""char out[16]; int n = snprintf(out, sizeof out, "total=%d", 5); CHECK(n == 7); CHECK(strcmp(out, "total=5") == 0);""",
            "snprintf returns the length that would be required, excluding the terminating null byte. A caller must compare it with capacity before treating output as complete.",
        ),
        E(
            "Trace statement order",
            "Start at 1, increment, then multiply by 3.",
            "The result is 6.",
            r"""int count = 1; count += 1; count *= 3; CHECK(count == 6);""",
            "Changing operation order changes the state trajectory. Separate statements make sequencing explicit.",
        ),
        E(
            "Inspect a boolean condition",
            "Compare 4 with 4 and 4 with 5.",
            "Equality is true and inequality is true.",
            r"""bool same = (4 == 4); bool different = (4 != 5); CHECK(same && different);""",
            "An equality expression compares values. Assignment uses a different operator and changes state.",
        ),
        E(
            "Use an explicit return contract",
            "Call a helper returning the value 7.",
            "The caller receives 7.",
            r"""CHECK(seven() == 7);""",
            "The declaration gives the compiler a return-type contract. A missing or incompatible declaration should be repaired before execution.",
        ),
        E(
            "Transfer a receipt calculation",
            "Multiply 4 items by a unit amount of 6.",
            "The checked amount is 24.",
            r"""int items = 4; int unit = 6; int amount = items * unit; CHECK(amount == 24);""",
            "These small values fit int. A reusable arithmetic API later needs a range and overflow policy rather than relying on one benign fixture.",
        ),
    ],
    helper="static int seven(void) { return 7; }",
    source="https://gcc.gnu.org/onlinedocs/gcc/Overall-Options.html",
)

add(
    "Integer ranges, signedness and floating approximation",
    """An integer type has a finite range. C guarantees minimum ranges for fundamental integer types, not that int has one universal size. Fixed-width types from stdint.h exist when the implementation supports exactly those widths. Unsigned arithmetic is defined modulo one more than its maximum value; signed overflow is undefined behavior. That difference is a semantic rule, not an invitation to guess CPU wraparound. Floating-point types approximate many real numbers and need deliberate comparison policies. Conversion can lose information even when the source program compiles without an error.""",
    """sizeof reports a size in char units, and sizeof(char) is always one; CHAR_BIT gives bits per char. INT_MAX and UINT_MAX expose implementation limits. A U suffix creates an unsigned integer constant. Integer division truncates toward zero. Convert an operand before division when a fractional result is required. fabs computes an absolute floating difference; a tolerance is specific to the numerical problem.""",
    [
        ("Range", "The set of values a type can represent."),
        ("Unsigned modular arithmetic", "Arithmetic reduced modulo the unsigned type range."),
        (
            "Undefined behavior",
            "An operation for which the C standard imposes no behavioral requirements.",
        ),
    ],
    [
        E(
            "Compare integer and floating division",
            "Compute 7/2 and 7/2.0.",
            "The results are 3 and 3.5.",
            r"""int whole = 7 / 2; double fraction = 7 / 2.0; CHECK(whole == 3 && fraction == 3.5);""",
            "Converting the already truncated integer result afterward cannot restore the missing fraction.",
        ),
        E(
            "Observe defined unsigned wrap",
            "Add one to UINT_MAX in unsigned arithmetic.",
            "The result is zero.",
            r"""unsigned int n = UINT_MAX; n += 1U; CHECK(n == 0U);""",
            "This result is guaranteed for unsigned arithmetic. Repeating the experiment with INT_MAX would invoke undefined behavior and is not an acceptable runnable example.",
        ),
        E(
            "Inspect representation facts",
            "Check sizeof(char) and minimum CHAR_BIT.",
            "A char occupies one char unit and has at least eight bits.",
            r"""CHECK(sizeof(char) == 1); CHECK(CHAR_BIT >= 8);""",
            "A C byte is defined in char units. Do not silently assume every historical or embedded target has eight-bit bytes.",
        ),
        E(
            "Widen before multiplication",
            "Multiply two int64_t values of 50000.",
            "The product is 2500000000.",
            r"""int64_t a = 50000; int64_t b = 50000; CHECK(a * b == INT64_C(2500000000));""",
            "The operand type determines the arithmetic. Casting an already-overflowed signed product afterward cannot repair undefined behavior.",
        ),
        E(
            "Check a tiny floating calculation",
            "Add 0.1 and 0.2 and compare to 0.3.",
            "The absolute error is below 1e-15.",
            r"""double a = 0.1, b = 0.2; CHECK(fabs((a + b) - 0.3) < 1e-15);""",
            "The tolerance is appropriate only for this tiny example. Large-scale or iterative calculations need error analysis and nonfinite-value handling.",
        ),
        E(
            "Transfer negative division",
            "Divide -7 by 2 and inspect its remainder.",
            "The quotient is -3 and remainder -1.",
            r"""int q = -7 / 2, r = -7 % 2; CHECK(q == -3 && r == -1 && q * 2 + r == -7);""",
            "Truncation toward zero differs from floor division. The reconstruction identity links the quotient and remainder.",
        ),
    ],
    headers="math.h",
    source="https://www.gnu.org/software/libc/manual/html_node/Integers.html",
)

add(
    "Expressions, conversions and sequencing",
    """An expression can compute a value and sometimes change state. C does not guarantee one universal evaluation order for every operator or function argument. Modifying one scalar more than once without the required sequencing can be undefined behavior. Keep complex updates in separate statements until the ordering is clear. The usual arithmetic conversions also affect comparisons: mixing a negative signed integer with an unsigned value can convert the negative operand into a large unsigned value. Parentheses clarify grouping but do not create sequencing where the language supplies none. Distinguish precedence, associativity and evaluation order.""",
    """&& and || short-circuit and sequence their left operand before a needed right operand. The conditional operator evaluates only its selected second or third operand. Assignment returns the assigned value, so accidental assignment inside a condition can be legal but wrong. ++ changes a value; using it in a larger expression requires careful reasoning. Prefer explicit temporary variables for updates with several observable effects.""",
    [
        ("Precedence", "Rules grouping operators in an expression."),
        ("Sequencing", "A language-defined order between evaluations."),
        ("Usual arithmetic conversions", "Rules selecting a common arithmetic representation."),
    ],
    [
        E(
            "Group before calculating",
            "Compare 2+3*4 with (2+3)*4.",
            "The values are 14 and 20.",
            r"""CHECK(2 + 3 * 4 == 14); CHECK((2 + 3) * 4 == 20);""",
            "Parentheses alter grouping. This example has no side effects, so it does not depend on evaluation order.",
        ),
        E(
            "Use a short-circuit guard",
            "Guard an array access with a false length test.",
            "The access is skipped and the condition is false.",
            r"""int values[1] = {7}; size_t length = 0; bool found = length > 0 && values[0] == 7; CHECK(!found);""",
            "The right operand is evaluated only when the left is true. A guard must precede the operation it protects.",
        ),
        E(
            "Sequence updates explicitly",
            "Increment x and then calculate twice its updated value.",
            "x is 2 and the result is 4.",
            r"""int x = 1; x += 1; int result = x * 2; CHECK(x == 2 && result == 4);""",
            "Separate statements avoid unsequenced read/write hazards and make the intended state transition visible.",
        ),
        E(
            "Expose signed-unsigned conversion",
            "Compare -1 with 1U under the usual conversion rules.",
            "The comparison -1 < 1U is false on this int/unsigned-int pair.",
            r"""int negative = -1; unsigned int positive = 1U; CHECK(!((unsigned int)negative < positive));""",
            "The explicit cast displays the same unsigned conversion that the mixed comparison would perform implicitly. The negative value becomes large rather than remaining mathematically negative; the cast also keeps this reference warning-clean.",
        ),
        E(
            "Choose one conditional branch",
            "Select a valid value while the other branch would divide by zero.",
            "Only the chosen branch is evaluated and result is 7.",
            r"""int zero = 0; int value = true ? 7 : 10 / zero; CHECK(value == 7);""",
            "The unchosen operand of ?: is not evaluated. This safe fixture demonstrates the rule without executing the invalid division.",
        ),
        E(
            "Transfer assignment diagnosis",
            "Assign 3 to a variable, then separately compare it with 3.",
            "The assignment changes the variable and equality tests it.",
            r"""int x = 0; x = 3; bool same = (x == 3); CHECK(same && x == 3);""",
            "Using = where == was intended may compile because assignment is an expression. Warnings and clear statement boundaries help expose that defect.",
        ),
    ],
    source="https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html",
)

add(
    "Branches, loops and invariants",
    """Control flow chooses which operations execute. A loop invariant describes what remains true before and after each iteration, connecting repeated steps to the intended result. For summation, the accumulator equals the sum of elements already visited. Empty input is then handled by the initial state rather than a special fabricated element. Index-based loops should use a half-open range from zero to length. An off-by-one error in C can access memory outside the array without a guaranteed runtime exception. Prove the bound before access rather than relying on a crash to identify mistakes.""",
    """if treats zero as false and nonzero as true. for combines initialization, condition and update. while checks before the body; do-while checks afterward. break exits the nearest loop or switch, while continue skips to the next iteration. switch cases fall through unless control exits explicitly. Use size_t for lengths and indices, and avoid decrement loops that accidentally wrap an unsigned counter below zero.""",
    [
        ("Loop invariant", "A property preserved by each iteration."),
        ("Half-open range", "A range including its start and excluding its end."),
        ("Fallthrough", "Continuing from one switch case into subsequent statements."),
    ],
    [
        E(
            "Trace a prefix sum",
            "Sum 2, 4 and 6 with a length-bounded loop.",
            "The result is 12.",
            r"""int values[] = {2,4,6}; int sum = 0; for(size_t i=0;i<3;i++){sum += values[i];} CHECK(sum == 12);""",
            "Each iteration adds exactly one valid element. The index is proven less than the declared length before access.",
        ),
        E(
            "Handle zero iterations",
            "Sum zero elements from a valid storage object.",
            "The accumulator remains zero.",
            r"""int values[1] = {9}; size_t length = 0; int sum = 0; for(size_t i=0;i<length;i++){sum += values[i];} CHECK(sum == 0);""",
            "The example uses a real array because zero-length arrays are not standard C17. The logical length may still be zero.",
        ),
        E(
            "Find the first match",
            "Search 3, 8, 8 and stop on the first 8.",
            "The index is 1.",
            r"""int values[] = {3,8,8}; size_t found = 3; for(size_t i=0;i<3;i++){if(values[i]==8){found=i;break;}} CHECK(found == 1);""",
            "The sentinel equals length and is never dereferenced. break preserves the first-match contract.",
        ),
        E(
            "Include an exact threshold",
            "Classify score 60 with passing threshold 60.",
            "The boundary passes.",
            r"""int score = 60; bool passed = score >= 60; CHECK(passed);""",
            "This distinguishes an inclusive threshold from a strict comparison. The policy should be stated before choosing the operator.",
        ),
        E(
            "Terminate a switch case",
            "Map code 2 to value 20 with explicit breaks.",
            "The result is 20.",
            r"""int code=2,result=0;switch(code){case 1:result=10;break;case 2:result=20;break;default:result=-1;break;}CHECK(result==20);""",
            "An omitted break can execute later case statements. Deliberate fallthrough needs a clear explanation and compiler-supported annotation policy.",
        ),
        E(
            "Transfer reverse traversal safely",
            "Visit indices 2, 1 and 0 using a positive-count loop.",
            "The reversed number is 321.",
            r"""int values[]={1,2,3};int out=0;for(size_t remaining=3;remaining>0;remaining--){size_t i=remaining-1;out=out*10+values[i];}CHECK(out==321);""",
            "The subtraction occurs only while remaining is positive. A condition i>=0 on size_t would never become false after wraparound.",
        ),
    ],
)

add(
    "Functions, prototypes and output parameters",
    """A function contract names inputs, outputs, side effects and failure behavior. A prototype lets the compiler check calls before seeing the implementation. C passes arguments by value, so changing a scalar parameter does not change its caller. A pointer parameter can permit a function to modify a caller-owned object, but the function must state whether null is accepted and what object size is required. Returning a status plus writing through an output pointer is a common C API pattern. On failure, define whether the output remains unchanged rather than leaving callers to guess.""",
    """static limits a file-scope function to its translation unit. A prototype such as int twice(int x) declares parameter and result types. void in an empty parameter list means no parameters in C17. bool try_area(int w,int h,int *out) can report success and provide an output separately. Validate preconditions before writing through out. Returning a pointer to an automatic local object creates a dangling pointer and must not be used.""",
    [
        ("Prototype", "A declaration describing a function call interface."),
        ("Output parameter", "A pointer through which a function returns a value."),
        ("Failure atomicity", "A contract that failed operations leave specified state unchanged."),
    ],
    [
        E(
            "Call a pure calculation",
            "Evaluate twice for 7 and 0.",
            "The results are 14 and 0.",
            r"""CHECK(twice(7)==14);CHECK(twice(0)==0);""",
            "The helper has no external state and its tiny input range avoids overflow. A general API would need a stated range.",
        ),
        E(
            "Return an output on success",
            "Calculate area for width 3 and height 4.",
            "Success is true and output becomes 12.",
            r"""int out=-1;CHECK(try_area(3,4,&out));CHECK(out==12);""",
            "The status and result are distinct. The caller checks status before using the new output.",
        ),
        E(
            "Preserve output on rejection",
            "Request area with width zero.",
            "The call fails and output remains -1.",
            r"""int out=-1;CHECK(!try_area(0,4,&out));CHECK(out==-1);""",
            "The helper validates before writing. This makes failure behavior predictable and supports retries or alternative handling.",
        ),
        E(
            "Trace copied scalar state",
            "Pass 5 to a helper that reassigns its parameter.",
            "The caller remains 5.",
            r"""int value=5;reassign(value);CHECK(value==5);""",
            "The function receives a scalar copy. Pointer-based mutation is a different explicit interface.",
        ),
        E(
            "Reject a missing output target",
            "Call try_area with a null output pointer.",
            "The call fails without dereferencing it.",
            r"""CHECK(!try_area(3,4,NULL));""",
            "This API deliberately accepts null as a rejected input. Other APIs may require non-null, but that precondition must be documented.",
        ),
        E(
            "Transfer overflow prevention",
            "Request INT_MAX times 2.",
            "The operation rejects it and preserves output.",
            r"""int out=9;CHECK(!try_area(INT_MAX,2,&out));CHECK(out==9);""",
            "Checking w > INT_MAX/h before multiplication avoids executing signed overflow while deciding whether overflow would occur.",
        ),
    ],
    helper="""static int twice(int x){return 2*x;}
static void reassign(int value){value=99;(void)value;}
static bool try_area(int w,int h,int *out){if(out==NULL||w<=0||h<=0||w>INT_MAX/h)return false;*out=w*h;return true;}""",
)

add(
    "Arrays, bounds and element counts",
    """An array owns a fixed number of elements of one type. Its valid indices run from zero through length minus one. C does not attach a runtime bounds check to each subscript. In many expressions an array converts to a pointer to its first element, which loses the length information. A function receiving an array-like parameter therefore normally needs a separate element count. sizeof applied to an actual array measures the whole array, but sizeof applied to a pointer measures the pointer object. Confusing these contexts is a common source of incomplete loops and out-of-bounds access.""",
    """int values[3] allocates three integers. A partial initializer fills remaining elements with zero. sizeof values / sizeof values[0] derives an element count only where values is still an array. A parameter written int values[] is adjusted to a pointer parameter. Pass the logical length explicitly and document whether a null pointer is permitted for length zero. Never dereference the one-past position.""",
    [
        ("Array extent", "The number of elements in an array object."),
        (
            "Array-to-pointer conversion",
            "Conversion to a pointer to the first element in most expressions.",
        ),
        ("Logical length", "The number of elements an operation is allowed to use."),
    ],
    [
        E(
            "Derive a local element count",
            "Create a three-element array and calculate its count with sizeof.",
            "The count is 3.",
            r"""int values[]={2,4,6};size_t n=sizeof values/sizeof values[0];CHECK(n==3);""",
            "The expression works because values is an array in this scope. Moving it unchanged into a pointer-taking helper would change its meaning.",
        ),
        E(
            "Pass an explicit length",
            "Sum three elements through a pointer-and-length API.",
            "The result is 12.",
            r"""int values[]={2,4,6};CHECK(sum_items(values,3)==12);""",
            "The API relies on the caller providing at least three live elements. The pointer alone cannot prove that extent.",
        ),
        E(
            "Inspect partial initialization",
            "Initialize only the first element of a three-element array.",
            "The remaining two elements are zero.",
            r"""int values[3]={7};CHECK(values[0]==7&&values[1]==0&&values[2]==0);""",
            "This initialization rule differs from an uninitialized automatic array, whose elements must not be read before assignment.",
        ),
        E(
            "Use a logical prefix",
            "Sum only the first two elements of a three-element array.",
            "The result is 6.",
            r"""int values[]={2,4,99};CHECK(sum_items(values,2)==6);""",
            "Physical capacity and logical length are separate. The third stored value is intentionally outside this operation.",
        ),
        E(
            "Handle an empty logical view",
            "Call the sum contract with null and length zero.",
            "The sum is zero and no access occurs.",
            r"""CHECK(sum_items(NULL,0)==0);""",
            "This particular helper accepts an empty null view because its loop performs no access. Do not assume every library function accepts null with a zero size.",
        ),
        E(
            "Transfer independent array storage",
            "Copy elements into a distinct array and mutate the copy.",
            "The original first element remains 1.",
            r"""int a[]={1,2};int b[2];for(size_t i=0;i<2;i++)b[i]=a[i];b[0]=9;CHECK(a[0]==1&&b[0]==9);""",
            "C arrays cannot be assigned as whole arrays with =. Explicit element copy or a correctly sized memcpy creates separate element storage.",
        ),
    ],
    helper="static int sum_items(const int *values,size_t n){int out=0;for(size_t i=0;i<n;i++)out+=values[i];return out;}",
)

add(
    "Strings, null terminators and output capacities",
    """A C string is a character sequence terminated by a null character. The terminator occupies storage but is not counted by strlen. A character array is not automatically a valid string: its contents must include a terminator within accessible storage before string functions can safely scan it. String literals must not be modified. A writable array initialized from a literal has its own storage. A pointer to a literal has a different mutation contract even when both can be read through const char pointers. Byte strings also do not automatically provide Unicode character indexing.""",
    """char word[] = "cat" creates four characters including the terminator. strlen counts bytes before that terminator. sizeof word counts the array storage in this scope. strcmp compares string content; pointer equality compares addresses instead. snprintf limits writes and reports the required length, allowing truncation detection. Reserve capacity for the terminating null byte and never repair a missing bound by hoping the next memory byte is zero.""",
    [
        ("Null terminator", "A zero character marking the end of a C string."),
        ("Capacity", "The total writable storage available to an output operation."),
        ("Truncation", "An output that does not fit completely in its destination."),
    ],
    [
        E(
            "Compare length and storage",
            "Create the writable string cat.",
            "strlen is 3 while array size is 4.",
            r"""char word[]="cat";CHECK(strlen(word)==3&&sizeof word==4);""",
            "The fourth byte is the terminator. Forgetting it when allocating an output creates a one-byte overflow risk.",
        ),
        E(
            "Modify owned text",
            "Change the first character of a writable cat array.",
            "The result is bat.",
            r"""char word[]="cat";word[0]='b';CHECK(strcmp(word,"bat")==0);""",
            "The array is writable. Performing the same assignment through a pointer to a string literal would be undefined behavior.",
        ),
        E(
            "Detect bounded truncation",
            "Format hello into a four-character buffer.",
            "The required length is 5 and stored text is hel.",
            r"""char out[4];int n=snprintf(out,sizeof out,"%s","hello");CHECK(n==5&&strcmp(out,"hel")==0);CHECK((size_t)n>=sizeof out);""",
            "The return value reports required length, not just bytes stored. Check a negative result before converting to size_t in a general helper.",
        ),
        E(
            "Accept exact capacity",
            "Store cat in a four-character buffer.",
            "The complete text fits with its terminator.",
            r"""char out[4];int n=snprintf(out,sizeof out,"%s","cat");CHECK(n==3&&strcmp(out,"cat")==0);""",
            "Capacity equal to payload length is insufficient. This destination has one additional character for termination.",
        ),
        E(
            "Compare content rather than pointers",
            "Create two separate arrays containing cat.",
            "strcmp reports equality.",
            r"""char a[]="cat";char b[]="cat";CHECK(strcmp(a,b)==0);""",
            "The arrays are distinct objects with equal content. Address equality is the wrong contract for textual equality.",
        ),
        E(
            "Transfer an empty string",
            "Create a one-character array containing only zero.",
            "Its string length is zero.",
            r"""char empty[1]={'\0'};CHECK(strlen(empty)==0&&sizeof empty==1);""",
            "Even an empty C string needs a terminator object. A null pointer is absence of an object, not an empty string.",
        ),
    ],
    source="https://www.gnu.org/software/libc/manual/html_node/String-Length.html",
)

add(
    "Pointers, addresses and explicit mutation",
    """A pointer identifies an object or function, or holds a null value. Dereferencing a pointer requires a live target with appropriate type, alignment and access permissions. C does not keep an object alive merely because a pointer still refers to it. A pointer to an automatic local object becomes invalid when that object lifetime ends. Passing a pointer copies the pointer value, while mutation through it can affect the caller-owned target. Prefer an explicit pointer contract over hidden global state. A null check is necessary for optional pointers, but it cannot prove that a non-null pointer still refers to valid storage.""",
    """&object obtains an address and *pointer accesses its target. int *p declares a pointer to int. Parentheses matter: *p += 1 changes the target, while p += 1 changes the pointer position. NULL is a null pointer constant. A function can return a pointer to caller-owned or static storage if its lifetime is documented, but must not return a pointer to an expired automatic local.""",
    [
        ("Pointer target", "The object a pointer designates."),
        ("Dereference", "Accessing the target through its pointer."),
        ("Lifetime", "The interval during which an object exists and may be accessed."),
    ],
    [
        E(
            "Change a caller-owned value",
            "Increment integer 4 through its address.",
            "The caller value becomes 5.",
            r"""int n=4;increment(&n);CHECK(n==5);""",
            "The helper receives a pointer copy, but that copy still designates the original integer.",
        ),
        E(
            "Read a target copy",
            "Copy the integer behind a pointer, then change the target.",
            "The copied value stays 3 and the target becomes 9.",
            r"""int n=3;int *p=&n;int copy=*p;*p=9;CHECK(copy==3&&n==9);""",
            "Dereferencing to obtain an int copies that scalar value. Retaining the pointer would retain access to future target changes.",
        ),
        E(
            "Reject an absent target",
            "Pass NULL to an optional update helper.",
            "The helper returns false without an access.",
            r"""CHECK(!set_if_present(NULL,8));""",
            "Null is a valid absence representation under this helper contract. Other invalid pointers cannot be repaired by this check.",
        ),
        E(
            "Update a present target",
            "Pass an integer address to the same helper.",
            "The helper returns true and stores 8.",
            r"""int n=1;CHECK(set_if_present(&n,8)&&n==8);""",
            "The caller owns the object and keeps it alive throughout the call.",
        ),
        E(
            "Distinguish pointer and target change",
            "Point p at a, then reassign p to b.",
            "Neither integer changes merely because p changes.",
            r"""int a=2,b=7;int *p=&a;p=&b;CHECK(a==2&&b==7&&*p==7);""",
            "Pointer assignment changes which object is designated. It is not a write to either prior or new target.",
        ),
        E(
            "Transfer a swap contract",
            "Swap two caller-owned integers through pointers.",
            "The values exchange positions.",
            r"""int a=2,b=7;swap_ints(&a,&b);CHECK(a==7&&b==2);""",
            "A temporary preserves the first value before overwriting it. The API requires two valid writable int objects.",
        ),
    ],
    helper="""static void increment(int *p){*p+=1;}
static bool set_if_present(int *p,int value){if(p==NULL)return false;*p=value;return true;}
static void swap_ints(int *a,int *b){int saved=*a;*a=*b;*b=saved;}""",
)

add(
    "Pointer arithmetic and bounded array views",
    """Pointer arithmetic is defined relative to an array object. A pointer may move among its elements and to the one-past position; the one-past pointer can be compared or used as an end marker but not dereferenced. Subtracting two pointers is defined only under the appropriate same-array relationship and when the result fits ptrdiff_t. Unrelated addresses are not a portable ordering mechanism. A pointer-and-length view makes the valid range explicit without owning the storage. Its lifetime remains limited by the underlying array. Treat an end pointer as a boundary, not as an extra element.""",
    """values+i points to element i and *(values+i) is equivalent to values[i] within valid bounds. end-begin produces an element count, not a byte count. A traversal can use p!=end before dereference. const int * restricts mutation through that view. Zero-length views need a documented representation; avoid performing pointer arithmetic on NULL merely because the intended length is zero.""",
    [
        (
            "One-past pointer",
            "A valid boundary pointer immediately after an array, never dereferenced.",
        ),
        ("Pointer difference", "The element distance between pointers into the same array."),
        ("Borrowed view", "A non-owning pointer plus an access bound."),
    ],
    [
        E(
            "Relate indexing and arithmetic",
            "Read the second element through both forms.",
            "Both yield 4.",
            r"""int values[]={2,4,6};CHECK(values[1]==*(values+1)&&*(values+1)==4);""",
            "The equivalence applies because the computed pointer remains within the live array.",
        ),
        E(
            "Measure an array interval",
            "Subtract begin from one-past end.",
            "The difference is 3 elements.",
            r"""int values[]={2,4,6};int *begin=values;int *end=values+3;ptrdiff_t n=end-begin;CHECK(n==3);""",
            "The result counts int elements. Multiplying by sizeof(int) would be a separate byte-size calculation.",
        ),
        E(
            "Traverse before the boundary",
            "Sum through a begin/end pointer loop.",
            "The result is 12.",
            r"""int values[]={2,4,6};int sum=0;for(const int *p=values;p!=values+3;p++){sum+=*p;}CHECK(sum==12);""",
            "The condition proves p is not one-past before dereference. Incrementing the final valid pointer reaches the end marker safely.",
        ),
        E(
            "Construct a subview",
            "View two elements starting at the second element.",
            "The subview contains 4 and 6.",
            r"""int values[]={2,4,6};const int *view=values+1;size_t n=2;CHECK(n==2&&view[0]==4&&view[1]==6);""",
            "The subview borrows the original array. It must not outlive that array or expand beyond its remaining extent.",
        ),
        E(
            "Keep an empty boundary non-dereferenced",
            "Use equal begin and end pointers inside one array.",
            "The traversal performs zero accesses.",
            r"""int values[1]={9};const int *begin=values,*end=values;size_t visits=0;for(const int *p=begin;p!=end;p++){visits++;}CHECK(visits==0);""",
            "This empty interval uses valid pointers into a real object. It avoids inventing a zero-sized array or arithmetic on NULL.",
        ),
        E(
            "Transfer mutation through a subview",
            "Change the first element of a borrowed suffix.",
            "The corresponding original element changes.",
            r"""int values[]={1,2,3};int *suffix=values+1;suffix[0]=8;CHECK(values[1]==8&&values[0]==1);""",
            "A view does not copy storage. The shared mutation must be part of the API contract.",
        ),
    ],
)

add(
    "Structs, enums and tagged domain values",
    """A struct groups named fields into one object. An enum gives meaningful names to integer constants, but it does not automatically prevent every other integer value from appearing in the representation. A tagged union pairs a discriminator with a union whose active interpretation depends on that tag. This can model alternatives without allocating a class hierarchy, but every reader must check the tag before interpreting the stored payload. Struct assignment copies fields, including pointer values rather than their targets. Struct padding and representation are implementation details, so bytewise comparison or raw struct serialization is not a general semantic equality policy.""",
    """struct Point names a type unless a typedef adds a shorter alias. A designated initializer uses .field=value. The dot operator accesses a struct value; -> accesses through a struct pointer. A union shares storage among alternatives. Switch on an enum tag and handle unexpected values explicitly. Compare meaningful fields rather than relying on memcmp over padding bytes.""",
    [
        ("Struct", "A value composed of named fields."),
        ("Discriminator", "A tag identifying which alternative a value represents."),
        ("Padding", "Implementation-inserted storage between or after fields."),
    ],
    [
        E(
            "Use named fields",
            "Construct Point with x 2 and y 3.",
            "The field sum is 5.",
            r"""struct Point p={.x=2,.y=3};CHECK(p.x+p.y==5);""",
            "Designated initialization preserves field meaning even if declaration order changes.",
        ),
        E(
            "Copy scalar fields",
            "Copy a Point and change the copied x.",
            "The original x stays 2.",
            r"""struct Point a={2,3};struct Point b=a;b.x=9;CHECK(a.x==2&&b.x==9);""",
            "Scalar fields are copied into independent struct storage. Pointer fields would still designate their original targets.",
        ),
        E(
            "Interpret an integer alternative",
            "Create a tagged number with an integer payload.",
            "The checked payload is 7.",
            r"""struct Value v={.tag=VALUE_INT,.data.integer=7};CHECK(v.tag==VALUE_INT&&v.data.integer==7);""",
            "The tag establishes which union member this design permits the reader to interpret.",
        ),
        E(
            "Interpret a text alternative",
            "Create a tagged value containing a borrowed string.",
            "The text is ready.",
            r"""struct Value v={.tag=VALUE_TEXT,.data.text="ready"};CHECK(v.tag==VALUE_TEXT&&strcmp(v.data.text,"ready")==0);""",
            "The text pointer borrows static string-literal storage. A general API would document ownership for dynamically supplied text.",
        ),
        E(
            "Compare semantic fields",
            "Compare two equal Points by x and y.",
            "Semantic equality is true.",
            r"""struct Point a={2,3},b={2,3};CHECK(a.x==b.x&&a.y==b.y);""",
            "Field comparison ignores padding. C does not supply whole-struct ==, and memcmp can distinguish irrelevant representation bytes.",
        ),
        E(
            "Transfer invalid-tag diagnosis",
            "Pass an unexpected discriminator to a validator.",
            "The validator rejects it.",
            r"""CHECK(!valid_tag((enum ValueTag)99));""",
            "An enum name list is not a runtime input validator. External integer data still needs range or membership checks.",
        ),
    ],
    helper="""struct Point{int x,y;};
enum ValueTag{VALUE_INT,VALUE_TEXT};
struct Value{enum ValueTag tag;union{int integer;const char *text;}data;};
static bool valid_tag(enum ValueTag tag){return tag==VALUE_INT||tag==VALUE_TEXT;}""",
)

add(
    "Scope, storage duration and object lifetime",
    """Scope determines where a name is visible; lifetime determines when its object exists. They are related but different. An automatic local object usually lasts until its block ends. A static-storage object exists for the program duration even when its name is visible only inside one function. Allocated storage has a lifetime controlled by allocation and release, taught next. A pointer does not extend any of these lifetimes automatically. Returning an automatic local address is invalid after return, while returning a static object address can be valid but introduces shared mutable state and reentrancy concerns.""",
    """A block can shadow an outer variable with the same name. static inside a function preserves one object across calls and zero-initializes it before execution. A file-scope static declaration also restricts linkage to the translation unit. These are different uses of the same keyword. Keep automatic variables explicitly initialized before reading them. Do not use the value of a pointer after its target lifetime has ended.""",
    [
        ("Scope", "The region where a name can be used."),
        ("Storage duration", "The category governing how long storage is retained."),
        (
            "Reentrancy",
            "Whether an operation can be entered again without corrupting shared execution state.",
        ),
    ],
    [
        E(
            "Trace block shadowing",
            "Declare an outer value 3 and a separate inner value 7.",
            "After the inner block, the outer remains 3.",
            r"""int value=3;{int value=7;CHECK(value==7);}CHECK(value==3);""",
            "The names are the same but designate distinct objects. Shadowing can be legal while still reducing readability.",
        ),
        E(
            "Retain static state",
            "Call a function with one static counter twice.",
            "It returns 1 and then 2.",
            r"""CHECK(next_count()==1);CHECK(next_count()==2);""",
            "The counter is initialized once and survives function returns. This shared state would require synchronization if called concurrently.",
        ),
        E(
            "Return a static address",
            "Get a pointer to a static read-only value.",
            "The target remains valid and equals 7.",
            r"""const int *p=static_value();CHECK(*p==7);""",
            "The target lifetime spans the program. const restricts mutation through this pointer but does not make every static design automatically thread-safe.",
        ),
        E(
            "Keep automatic state per call",
            "Call a function with an initialized local counter twice.",
            "Both calls return 1.",
            r"""CHECK(local_count()==1&&local_count()==1);""",
            "Each call creates a fresh automatic object. This differs from the retained static counter.",
        ),
        E(
            "Separate visibility from lifetime",
            "Retain a value copy obtained from an inner block.",
            "The copied scalar remains 9 afterward.",
            r"""int copy=0;{int local=9;copy=local;}CHECK(copy==9);""",
            "The scalar copy has its own lifetime. Retaining &local instead would produce an invalid pointer after the block.",
        ),
        E(
            "Transfer initialized aggregation",
            "Initialize an accumulator before processing an empty range.",
            "The result is the defined zero identity.",
            r"""int total=0;size_t count=0;for(size_t i=0;i<count;i++)total+=(int)i;CHECK(total==0);""",
            "Reading an uninitialized automatic accumulator would not be repaired by an empty loop. Initialization is part of the algorithm.",
        ),
    ],
    helper="""static int next_count(void){static int count=0;count++;return count;}
static const int *static_value(void){static const int value=7;return &value;}
static int local_count(void){int count=0;count++;return count;}""",
)

add(
    "Const-correct views and mutation boundaries",
    """const describes permitted access through a type-qualified expression. A pointer to const int prevents modifying the target through that pointer, while a const pointer prevents changing which target the pointer designates. These are different guarantees. A mutable object can be observed through a const view and changed through another valid mutable path. An object originally defined const must not be modified by casting away qualification. Const-correct APIs communicate read-only intent and let callers pass immutable data safely, but they do not automatically provide deep immutability, ownership or synchronization.""",
    """const int *p reads as a pointer to a const-qualified int. int *const p is a const pointer to a mutable int. const int *const p combines both restrictions. Function parameters can use const for borrowed read-only arrays. A struct containing a pointer can still reference mutable storage even if the outer struct is accessed through a const pointer; deep ownership requires a broader design.""",
    [
        ("Const-qualified view", "An access path that forbids mutation through that path."),
        ("Const pointer", "A pointer object that cannot be reassigned after initialization."),
        ("Deep immutability", "A policy preventing mutation throughout a reachable object graph."),
    ],
    [
        E(
            "Read through a const view",
            "Observe a mutable integer through const int pointer.",
            "The read yields 4.",
            r"""int value=4;const int *view=&value;CHECK(*view==4);""",
            "The view is read-only, but the underlying object was not defined const.",
        ),
        E(
            "Observe another valid mutation",
            "Change the mutable object through its original name.",
            "The const view now reads 7.",
            r"""int value=4;const int *view=&value;value=7;CHECK(*view==7);""",
            "Const access does not freeze a shared mutable object or create a snapshot.",
        ),
        E(
            "Use a fixed pointer target",
            "Create an int pointer that cannot be reassigned, then update its target.",
            "The target becomes 8.",
            r"""int value=1;int *const fixed=&value;*fixed=8;CHECK(value==8);""",
            "The pointer object is fixed while the designated int remains writable.",
        ),
        E(
            "Read an immutable object",
            "Declare a const integer and access it through a const pointer.",
            "The value is 9.",
            r"""const int value=9;const int *p=&value;CHECK(*p==9);""",
            "No cast is used to bypass the qualification. Modifying an object originally defined const would be undefined behavior.",
        ),
        E(
            "Pass a read-only array contract",
            "Sum a const array using a const pointer parameter.",
            "The sum is 6.",
            r"""const int values[]={1,2,3};CHECK(read_sum(values,3)==6);""",
            "A read-only parameter accepts both const and mutable inputs while promising not to change elements through that path.",
        ),
        E(
            "Transfer snapshot independence",
            "Copy the scalar observed through a const view and then mutate the original.",
            "The snapshot remains 2 while the view reads 5.",
            r"""int value=2;const int *view=&value;int snapshot=*view;value=5;CHECK(snapshot==2&&*view==5);""",
            "A value copy establishes an independent snapshot; qualification alone does not.",
        ),
    ],
    helper="static int read_sum(const int *values,size_t n){int sum=0;for(size_t i=0;i<n;i++)sum+=values[i];return sum;}",
)

add(
    "Preprocessing, macros and compile-time contracts",
    """The preprocessor transforms tokens before the compiler performs ordinary type checking. Header inclusion, conditional compilation and macros can be useful, but a macro is not a normal function. Its arguments may be substituted more than once, and missing parentheses can change expression grouping. Side-effecting arguments such as increments are therefore hazardous in many function-like macros. Prefer typed functions or static inline functions for behavior when possible. Use macros for configuration and declarations that need preprocessing, and keep conditional platform code small and documented. The same source should not silently change semantic contracts because a build flag was forgotten.""",
    """#define creates a macro replacement. Parenthesize each expression argument and the full result, but understand that this does not prevent repeated evaluation. #if and #ifdef select tokens before compilation. Include guards prevent repeated header definitions. _Static_assert checks a constant expression during compilation. _Generic can select an expression by type in C11 and later without becoming a runtime type system.""",
    [
        ("Macro expansion", "Token replacement before ordinary compilation."),
        (
            "Repeated evaluation",
            "An argument expression being executed multiple times after substitution.",
        ),
        ("Compile-time assertion", "A condition required for successful translation."),
    ],
    [
        E(
            "Use a parenthesized macro safely",
            "Square the side-effect-free expression 2+3.",
            "The result is 25.",
            r"""CHECK(SQUARE(2+3)==25);""",
            "Parentheses preserve grouping. This macro still evaluates its argument twice, so side effects remain inappropriate.",
        ),
        E(
            "Prefer a typed helper for mutation",
            "Pass value++ to a normal square function.",
            "The result is 9 and value increments once to 4.",
            r"""int value=3;int result=square_int(value++);CHECK(result==9&&value==4);""",
            "A function argument expression is evaluated once for this call. SQUARE(value++) would create an unsequenced modification hazard.",
        ),
        E(
            "Require a representation fact",
            "Check the language-required char size at translation time.",
            "Compilation accepts the true static assertion.",
            r"""_Static_assert(sizeof(char)==1,"char unit must be one");CHECK(sizeof(char)==1);""",
            "A compile-time invariant fails before execution. It is different from a runtime assertion about input data.",
        ),
        E(
            "Read a configuration constant",
            "Use a fixed capacity macro of 8.",
            "The declared buffer has eight elements.",
            r"""int values[LESSON_CAPACITY]={0};CHECK(sizeof values/sizeof values[0]==8);""",
            "Configuration macros can express shared compile-time sizes. Runtime input still needs checking against that fixed capacity.",
        ),
        E(
            "Select by a simple type",
            "Use a generic selection for int and double expressions.",
            "The selected labels are integer and floating.",
            r"""CHECK(strcmp(TYPE_LABEL(3),"integer")==0);CHECK(strcmp(TYPE_LABEL(3.0),"floating")==0);""",
            "_Generic chooses from declared compatible types at translation time. It does not inspect arbitrary serialized data at runtime.",
        ),
        E(
            "Transfer an inline-style function contract",
            "Square zero and negative three through the typed helper.",
            "The results are 0 and 9.",
            r"""CHECK(square_int(0)==0&&square_int(-3)==9);""",
            "The helper has ordinary type checking and one evaluation per argument. Large magnitudes still need an overflow policy.",
        ),
    ],
    helper="""#define SQUARE(x) ((x)*(x))
#define LESSON_CAPACITY 8
#define TYPE_LABEL(x) _Generic((x), int: "integer", double: "floating", default: "other")
static int square_int(int value){return value*value;}""",
    source="https://gcc.gnu.org/onlinedocs/cpp/Macro-Pitfalls.html",
)

add(
    "Parsing numbers with complete error evidence",
    """External text must be parsed under an explicit grammar and range policy. atoi cannot report all useful failure distinctions, so robust code often uses strtol with an end pointer and errno. Parsing can consume no digits, stop before trailing garbage, or overflow the target type. A long result may still fail to fit an int even when strtol itself succeeded. Reset errno before the call and inspect it afterward. Define whitespace and sign rules deliberately. Preserve the output on failure so a caller cannot mistake a partial or stale result for a successful parse.""",
    """strtol(text,&end,10) parses base-ten text and stores where parsing stopped. end==text means no digits were consumed. errno==ERANGE reports range failure for long. Require *end=='\\0' for this lesson's whole-string contract, then compare against INT_MIN and INT_MAX before converting. This helper accepts strtol leading whitespace and signs, but rejects trailing whitespace or other trailing text; a different user-facing policy should normalize explicitly before parsing.""",
    [
        ("End pointer", "The location immediately after the parsed numeric prefix."),
        (
            "Range error",
            "A value outside the representation accepted by the parser or target type.",
        ),
        ("Whole-string contract", "A rule requiring all input text to belong to one valid value."),
    ],
    [
        E(
            "Parse a complete integer",
            "Parse 42 into an output integer.",
            "Success is true and output is 42.",
            r"""int out=0;CHECK(parse_int("42",&out)&&out==42);""",
            "The parser validates complete consumption and final target range before assignment.",
        ),
        E(
            "Reject trailing garbage",
            "Parse 42x with an existing output of 7.",
            "The call fails and output remains 7.",
            r"""int out=7;CHECK(!parse_int("42x",&out)&&out==7);""",
            "A valid prefix is not a valid complete input under this contract.",
        ),
        E(
            "Reject empty input",
            "Parse an empty string.",
            "No numeric value is accepted.",
            r"""int out=7;CHECK(!parse_int("",&out)&&out==7);""",
            "The end pointer equals the start when no digits are consumed. A zero result alone cannot reveal that failure.",
        ),
        E(
            "Reject an oversized number",
            "Parse a very long positive integer.",
            "The operation rejects the range overflow.",
            r"""int out=7;CHECK(!parse_int("999999999999999999999999999999",&out)&&out==7);""",
            "The test does not assume a particular long width. The fixture exceeds ordinary supported widths and exercises parser range evidence.",
        ),
        E(
            "Retain a valid negative value",
            "Parse -7.",
            "The output is -7.",
            r"""int out=0;CHECK(parse_int("-7",&out)&&out==-7);""",
            "A sign is part of this chosen grammar. Domain validation may impose additional restrictions afterward.",
        ),
        E(
            "Transfer the whitespace policy",
            "Compare leading whitespace with trailing whitespace.",
            "Leading whitespace is accepted; trailing whitespace is rejected.",
            r"""int out=0;CHECK(parse_int(" 3",&out)&&out==3);CHECK(!parse_int("3 ",&out));""",
            "This deliberate contrast makes the grammar observable. Do not change it accidentally by ignoring the end pointer.",
        ),
    ],
    headers="errno.h",
    helper=r"""static bool parse_int(const char *text,int *out){if(text==NULL||out==NULL)return false;errno=0;char *end=NULL;long value=strtol(text,&end,10);if(end==text||*end!='\0'||errno==ERANGE||value<INT_MIN||value>INT_MAX)return false;*out=(int)value;return true;}""",
    source="https://www.gnu.org/software/libc/manual/html_node/Parsing-of-Integers.html",
)
