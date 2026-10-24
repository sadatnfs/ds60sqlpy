"""Advanced C systems contracts with safe, bounded executable fixtures."""

from render import add
from render import case as E

add(
    "Undefined behavior, aliasing and object representation",
    """Undefined behavior is not a special runtime result such as a crash. It removes the language guarantee for the operation and can affect compiler reasoning about surrounding code. Common causes include out-of-bounds access, signed overflow, expired lifetimes and incompatible typed access. The effective-type and aliasing rules allow optimizers to assume certain pointer types do not refer to the same object. Use character access or memcpy for object representation rather than casting arbitrary byte storage to a typed pointer. Alignment and representation validity remain separate requirements. A plausible output from one build does not establish that an invalid operation is safe.""",
    """unsigned char can inspect object representation bytes. memcpy copies a specified number of bytes between valid nonoverlapping regions. memmove supports overlapping ranges. _Alignof describes a type alignment requirement. A pointer conversion alone does not create an object lifetime, correct alignment or valid value representation. This lesson deliberately demonstrates defined alternatives and never executes the invalid counterpart.""",
    [
        ("Effective type", "The type rules governing how stored values may be accessed."),
        ("Object representation", "The bytes used to represent an object."),
        ("Strict aliasing", "Rules restricting access through incompatible typed pointers."),
    ],
    [
        E(
            "Copy a representation safely",
            "Copy a float into bytes and back into a float object.",
            "The restored value is 1.5.",
            r"""float original=1.5f,restored=0.0f;unsigned char bytes[sizeof original];memcpy(bytes,&original,sizeof original);memcpy(&restored,bytes,sizeof restored);CHECK(restored==original);""",
            "The copied bytes originated from a valid object of the same type. This does not claim arbitrary external bytes are a valid float representation.",
        ),
        E(
            "Inspect bytes without type punning",
            "Read an integer representation through unsigned char.",
            "The byte view has exactly sizeof(int) bytes.",
            r"""int value=7;const unsigned char *bytes=(const unsigned char *)&value;unsigned int sum=0;for(size_t i=0;i<sizeof value;i++)sum+=bytes[i];CHECK(sizeof value>=1);(void)sum;""",
            "Character access is the appropriate representation-view mechanism. The test deliberately avoids assuming a particular byte order.",
        ),
        E(
            "Handle overlapping moves",
            "Shift abc right by one within a buffer using memmove.",
            "The buffer prefix becomes aabc.",
            r"""char text[8]="abc";memmove(text+1,text,4);CHECK(strcmp(text,"aabc")==0);""",
            "memmove supports overlap. memcpy would not provide the required contract for these overlapping ranges.",
        ),
        E(
            "Keep typed access in a real object",
            "Copy an int value into another int with memcpy.",
            "The target value becomes 9.",
            r"""int source=9,target=0;memcpy(&target,&source,sizeof target);CHECK(target==9);""",
            "Both source and destination are valid int objects with sufficient storage. No misaligned cast is involved.",
        ),
        E(
            "Inspect an alignment requirement",
            "Read the alignment of int and max_align_t.",
            "Both requirements are positive.",
            r"""CHECK(_Alignof(int)>0&&_Alignof(max_align_t)>0);""",
            "Alignment is part of a typed access precondition. A byte count alone cannot prove an arbitrary address is aligned.",
        ),
        E(
            "Transfer a bounded byte copy",
            "Copy a four-byte payload into an equally sized destination.",
            "All bytes match exactly.",
            r"""unsigned char source[4]={0,1,2,255},target[4]={0};memcpy(target,source,sizeof source);CHECK(memcmp(source,target,sizeof source)==0);""",
            "Here bytewise equality is the semantic contract because the objects are explicitly byte arrays, not structs with unspecified padding.",
        ),
    ],
    source="https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html",
)

add(
    "Sanitizers, debugger evidence and safe regressions",
    """Compiler warnings, static analysis, sanitizers and debugger traces reveal different classes of evidence. AddressSanitizer instruments many invalid memory accesses; UndefinedBehaviorSanitizer checks selected undefined operations. Neither establishes that every possible path is correct, and neither replaces ownership reasoning. A sanitizer failure should become a small regression case after the defect is repaired. Do not ship a reference that intentionally executes undefined behavior merely to print a diagnostic. This lesson runs safe regression cases and gives the separate instrumented build workflow. A debugger is most useful when you can name the first invariant that became false rather than merely stop at the final crash.""",
    """A prepared contributor build can add -g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer to compilation and linking. Execute the same checked source under that build. The ordinary pad uses its fixed reviewed flags and does not claim sanitizer execution. Keep source, compiler command, exit status and diagnostic together. Disable neither an assertion nor a sanitizer report without explaining the actual correction.""",
    [
        ("Instrumentation", "Additional checks inserted into a compiled program."),
        ("Regression fixture", "A small retained input exposing a prior defect."),
        ("Diagnostic evidence", "A trace or report tied to an actual source and execution."),
    ],
    [
        E(
            "Guard a formerly unsafe index",
            "Use a checked accessor on the final valid index.",
            "The value 6 is returned.",
            r"""int values[]={2,4,6},out=0;CHECK(at_index(values,3,2,&out)&&out==6);""",
            "The accessor proves the index is below length before reading.",
        ),
        E(
            "Reject the one-past index",
            "Request index 3 from length 3.",
            "The operation fails and output remains 9.",
            r"""int values[]={2,4,6},out=9;CHECK(!at_index(values,3,3,&out)&&out==9);""",
            "The regression preserves the boundary that an unchecked implementation would access illegally.",
        ),
        E(
            "Reject an empty view",
            "Request index zero from an empty logical view.",
            "No access occurs.",
            r"""int out=9;CHECK(!at_index(NULL,0,0,&out)&&out==9);""",
            "The function checks the pointer and bound instead of relying on a sanitizer to stop a bad access.",
        ),
        E(
            "Verify a valid allocation lifetime",
            "Allocate, initialize, inspect and free one integer.",
            "The value is checked before release.",
            r"""int *p=malloc(sizeof *p);CHECK(p!=NULL);*p=7;CHECK(*p==7);free(p);p=NULL;CHECK(p==NULL);""",
            "There is no post-free dereference in a production reference. A historical failing source belongs only in a clearly isolated diagnostic exercise.",
        ),
        E(
            "Retain output capacity checks",
            "Format a short message into sufficient storage.",
            "The write fits completely.",
            r"""char out[8];int n=snprintf(out,sizeof out,"%s","ready");CHECK(n>=0&&(size_t)n<sizeof out&&strcmp(out,"ready")==0);""",
            "The explicit return-value check remains useful even when instrumentation is enabled.",
        ),
        E(
            "Transfer a newly discovered boundary",
            "Test a singleton at indices zero and one.",
            "Only zero is valid.",
            r"""int values[]={5},out=0;CHECK(at_index(values,1,0,&out)&&out==5);CHECK(!at_index(values,1,1,&out));""",
            "A tiny case is easier to reason about and keep as a permanent regression than a large nondeterministic crash workload.",
        ),
    ],
    helper="static bool at_index(const int *values,size_t n,size_t i,int *out){if(values==NULL||out==NULL||i>=n)return false;*out=values[i];return true;}",
    source="https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html",
    boundary="In a separately prepared Linux contributor directory, compile the complete reference with cc -std=c17 -g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer main.c -o lesson-sanitized, then execute it. Sanitizer availability is a toolchain capability, not implied by the ordinary pad. Keep sanitizer results separate from normal compiler/run receipts.",
)

add(
    "Checked arithmetic and allocation-size contracts",
    """Integer overflow is often a memory-safety defect in disguise. A wrapped allocation size can reserve less storage than later code assumes, and signed overflow cannot safely be used as the condition that detects itself. Validate before the operation using inequalities whose own arithmetic is defined. Keep signed value arithmetic separate from size_t storage arithmetic, and validate conversions at their boundary. The chosen failure policy should preserve outputs and let callers distinguish overflow from a legitimate zero. Compiler overflow builtins can be useful, but portable C17 logic remains worth understanding before depending on a toolchain extension.""",
    """For a positive addend b, a+b fits int only when a<=INT_MAX-b. For a negative b, require a>=INT_MIN-b. For size_t multiplication, if b is nonzero require a<=SIZE_MAX/b. Check output pointers before writing. These preconditions avoid evaluating the dangerous expression until its validity is established. A zero multiplier is a valid mathematical case, even when an allocator wrapper later rejects zero-sized storage by policy.""",
    [
        ("Precondition check", "A condition established before a potentially invalid operation."),
        ("Checked arithmetic", "Arithmetic that reports range failure explicitly."),
        (
            "Conversion boundary",
            "A point where values move between representations with different ranges.",
        ),
    ],
    [
        E(
            "Add ordinary values",
            "Add 7 and 5 through the checked helper.",
            "The result is 12.",
            r"""int out=0;CHECK(add_checked(7,5,&out)&&out==12);""",
            "The normal case uses the same guarded path as boundary cases.",
        ),
        E(
            "Reject positive overflow",
            "Add one to INT_MAX.",
            "The operation fails and preserves output.",
            r"""int out=9;CHECK(!add_checked(INT_MAX,1,&out)&&out==9);""",
            "The addition itself is never evaluated after the precondition fails.",
        ),
        E(
            "Reject negative overflow",
            "Add negative one to INT_MIN.",
            "The operation fails without evaluating the overflow.",
            r"""int out=9;CHECK(!add_checked(INT_MIN,-1,&out)&&out==9);""",
            "Checking the negative boundary requires a separate inequality from the positive case.",
        ),
        E(
            "Accept exact boundaries",
            "Add zero to both int extremes.",
            "Both exact boundary values are accepted.",
            r"""int out=0;CHECK(add_checked(INT_MAX,0,&out)&&out==INT_MAX);CHECK(add_checked(INT_MIN,0,&out)&&out==INT_MIN);""",
            "An overconservative check that rejects every extreme would violate the valid-domain contract.",
        ),
        E(
            "Reject a size product",
            "Multiply SIZE_MAX by two through a size helper.",
            "The helper rejects it and preserves output.",
            r"""size_t out=7;CHECK(!size_product(SIZE_MAX,2,&out)&&out==7);""",
            "The division comparison avoids wrapping before allocation-size validation.",
        ),
        E(
            "Transfer the zero product",
            "Multiply SIZE_MAX by zero.",
            "The checked mathematical result is zero.",
            r"""size_t out=7;CHECK(size_product(SIZE_MAX,0,&out)&&out==0);""",
            "Arithmetic validity and whether a zero-sized allocation is useful are separate policies.",
        ),
    ],
    helper="""static bool add_checked(int a,int b,int *out){if(out==NULL||(b>0&&a>INT_MAX-b)||(b<0&&a<INT_MIN-b))return false;*out=a+b;return true;}
static bool size_product(size_t a,size_t b,size_t *out){if(out==NULL||(b!=0&&a>SIZE_MAX/b))return false;*out=a*b;return true;}""",
)

add(
    "Generic byte APIs, alignment and element-size discipline",
    """C can write generic storage algorithms using void pointers and explicit element sizes. That flexibility moves type information into the API contract. A wrong element size can copy partial objects, overrun storage or produce misaligned access. void pointer arithmetic is not standard C, so byte traversal uses unsigned char pointers. A generic operation should state overlap, alignment, lifetime and ownership rules rather than claiming that void means any operation is safe. Keep type-specific interpretation at a reviewed boundary and prefer typed wrappers for common callers.""",
    """void * can hold object pointers and convert back to an appropriate object pointer. unsigned char * supports bytewise stepping. A swap helper can exchange representations one byte at a time without allocating, provided its two regions are valid, equally sized and nonoverlapping. qsort receives element size explicitly; the comparator must cast each supplied pointer to the actual element type. Generic code still needs bounded size arithmetic.""",
    [
        ("Type erasure", "Removing concrete type information from an interface."),
        ("Element size", "The storage width the generic algorithm uses per element."),
        ("Typed wrapper", "A type-specific API around a more general implementation."),
    ],
    [
        E(
            "Swap integer objects",
            "Exchange two ints using their exact object size.",
            "The values become 7 and 2.",
            r"""int a=2,b=7;swap_bytes(&a,&b,sizeof a);CHECK(a==7&&b==2);""",
            "The size comes from the actual object rather than a guessed platform width.",
        ),
        E(
            "Swap fixed byte arrays",
            "Exchange two three-byte arrays.",
            "Their byte contents exchange exactly.",
            r"""unsigned char a[]={1,2,3},b[]={4,5,6};swap_bytes(a,b,sizeof a);CHECK(a[0]==4&&a[2]==6&&b[0]==1&&b[2]==3);""",
            "The operation changes representation bytes without interpreting them as another type.",
        ),
        E(
            "Use a zero-length operation",
            "Invoke the helper with size zero and valid object pointers.",
            "Both objects remain unchanged.",
            r"""int a=2,b=7;swap_bytes(&a,&b,0);CHECK(a==2&&b==7);""",
            "The loop performs no accesses. This fixture uses valid pointers rather than assuming every generic API accepts NULL for zero length.",
        ),
        E(
            "Round-trip a swap",
            "Swap two ints twice.",
            "The original values return.",
            r"""int a=2,b=7;swap_bytes(&a,&b,sizeof a);swap_bytes(&a,&b,sizeof a);CHECK(a==2&&b==7);""",
            "This property complements the exact one-swap result; by itself it would also accept a no-op implementation.",
        ),
        E(
            "Read bytes through a generic input",
            "Count three nonzero bytes in a four-byte buffer.",
            "The count is 3.",
            r"""unsigned char data[]={1,0,2,3};CHECK(count_nonzero(data,sizeof data)==3);""",
            "The semantic unit is explicitly a byte, so no typed alignment assumption is needed.",
        ),
        E(
            "Transfer a typed structure copy",
            "Copy a Pair into another Pair using its exact size.",
            "Both semantic fields match.",
            r"""struct Pair a={2,3},b={0,0};memcpy(&b,&a,sizeof b);CHECK(b.x==2&&b.y==3);""",
            "The destination is a real object of the same type. Semantic verification checks fields rather than unspecified padding bytes.",
        ),
    ],
    helper="""struct Pair{int x,y;};
static void swap_bytes(void *left,void *right,size_t size){unsigned char *a=left,*b=right;for(size_t i=0;i<size;i++){unsigned char saved=a[i];a[i]=b[i];b[i]=saved;}}
static size_t count_nonzero(const void *data,size_t size){const unsigned char *bytes=data;size_t count=0;for(size_t i=0;i<size;i++)if(bytes[i]!=0)count++;return count;}""",
)

add(
    "Flexible array members and single-allocation records",
    """A flexible array member lets a struct end with a variable-sized trailing region. It must be the final member and does not contribute ordinary array elements to sizeof the base struct. Allocate enough storage for both the header and payload, with overflow checks before addition and multiplication. Keeping related data in one allocation can simplify ownership and improve locality, but every accessor must still respect the recorded payload length. Copying only sizeof the header does not clone the trailing payload. C struct assignment and generic serialization need special care for this layout.""",
    """struct Packet { size_t length; unsigned char data[]; } declares a flexible member. Allocate sizeof(struct Packet)+length bytes after proving length<=SIZE_MAX-sizeof(struct Packet). The member may have alignment-related placement details, so access it through the declared member rather than guessing an offset. One free releases the entire owned record. This fixture stores bytes, avoiding additional element-alignment arithmetic.""",
    [
        (
            "Flexible array member",
            "A final struct array member whose storage is supplied by a larger allocation.",
        ),
        ("Header size", "The fixed storage occupied by the struct before its variable payload."),
        ("Contiguous ownership", "One allocation containing metadata and related data."),
    ],
    [
        E(
            "Create a trailing payload",
            "Create a packet containing bytes 1, 2, 3.",
            "Length and all three bytes are retained.",
            r"""unsigned char data[]={1,2,3};struct Packet *p=packet_create(data,3);CHECK(p!=NULL&&p->length==3&&p->data[0]==1&&p->data[2]==3);free(p);""",
            "One owner releases header and payload together.",
        ),
        E(
            "Create an empty packet",
            "Create a packet with length zero.",
            "The header exists and records zero length.",
            r"""struct Packet *p=packet_create(NULL,0);CHECK(p!=NULL&&p->length==0);free(p);""",
            "The helper avoids calling memcpy on absent payload pointers when no bytes are requested.",
        ),
        E(
            "Reject total-size overflow",
            "Request SIZE_MAX payload bytes.",
            "The operation returns NULL before allocation.",
            r"""CHECK(packet_create(NULL,SIZE_MAX)==NULL);""",
            "Checking the addition before allocation prevents a wrapped header-plus-payload size.",
        ),
        E(
            "Clone the complete record",
            "Create two packets from the same source and mutate one.",
            "The other payload remains unchanged.",
            r"""unsigned char data[]={4,5};struct Packet *a=packet_create(data,2),*b=packet_create(data,2);CHECK(a!=NULL&&b!=NULL);b->data[0]=9;CHECK(a->data[0]==4&&b->data[0]==9);free(a);free(b);""",
            "Separate complete allocations create independent owners. A base-struct assignment would not copy the flexible payload.",
        ),
        E(
            "Preserve binary zero",
            "Store a payload containing a zero byte.",
            "Length remains three and the zero is retained.",
            r"""unsigned char data[]={7,0,8};struct Packet *p=packet_create(data,3);CHECK(p!=NULL&&p->length==3&&p->data[1]==0);free(p);""",
            "The payload is length-delimited binary data rather than a C string.",
        ),
        E(
            "Transfer source independence",
            "Change the original source after packet construction.",
            "The owned packet retains its copied value.",
            r"""unsigned char data[]={1};struct Packet *p=packet_create(data,1);CHECK(p!=NULL);data[0]=9;CHECK(p->data[0]==1);free(p);""",
            "Construction copies input bytes. A borrowed-view API would require a different lifetime contract.",
        ),
    ],
    helper="""struct Packet{size_t length;unsigned char data[];};
static struct Packet *packet_create(const unsigned char *data,size_t length){if(length>SIZE_MAX-sizeof(struct Packet)||(length>0&&data==NULL))return NULL;struct Packet *p=malloc(sizeof *p+length);if(p==NULL)return NULL;p->length=length;if(length>0)memcpy(p->data,data,length);return p;}""",
)

add(
    "POSIX descriptors, pipes and explicit endpoint closure",
    """POSIX file descriptors are small integer handles to open resources. They are not FILE pointers, and their read/write operations do not use the same buffering contract. A pipe provides a byte stream from one endpoint to another. Reads can be short, and EOF occurs only after all write endpoints are closed and buffered bytes are consumed. Forgetting an inherited or duplicated write endpoint can make a reader wait forever. Every descriptor needs a known owner and close point. These examples create only local anonymous pipes and close them within each case; they never open host paths or contact a network.""",
    """pipe fills two descriptors: index zero reads and index one writes. read and write return ssize_t, with negative values indicating errors. A robust general loop handles EINTR and partial transfers under a total byte budget. close releases one descriptor reference. dup creates another reference to the same underlying open description, so closing one reference does not necessarily end the stream. POSIX APIs are platform extensions, not ISO C17 itself.""",
    [
        ("File descriptor", "A process-local integer handle to an open POSIX resource."),
        ("Pipe endpoint", "One read or write side of a byte stream."),
        ("Descriptor ownership", "Responsibility for closing each acquired handle."),
    ],
    [
        E(
            "Transfer a small pipe payload",
            "Write abc, close the writer and read the bytes.",
            "Three bytes arrive unchanged.",
            r"""int fds[2];CHECK(pipe(fds)==0);CHECK(write(fds[1],"abc",3)==3);CHECK(close(fds[1])==0);char out[4]={0};CHECK(read(fds[0],out,3)==3&&strcmp(out,"abc")==0);CHECK(close(fds[0])==0);""",
            "The tiny write is within the pipe atomic-write bound. General streams still require loops for partial operations.",
        ),
        E(
            "Observe EOF after closure",
            "Close an unused writer and read from its empty pipe.",
            "read returns zero.",
            r"""int fds[2];CHECK(pipe(fds)==0);CHECK(close(fds[1])==0);char byte=0;CHECK(read(fds[0],&byte,1)==0);CHECK(close(fds[0])==0);""",
            "Zero is EOF for this positive-sized read, not an error. All writers are closed before waiting.",
        ),
        E(
            "Read a payload in two pieces",
            "Write four bytes and request two bytes at a time.",
            "The pieces are ab and cd.",
            r"""int fds[2];CHECK(pipe(fds)==0);CHECK(write(fds[1],"abcd",4)==4);CHECK(close(fds[1])==0);char a[3]={0},b[3]={0};CHECK(read(fds[0],a,2)==2&&read(fds[0],b,2)==2);CHECK(strcmp(a,"ab")==0&&strcmp(b,"cd")==0);CHECK(close(fds[0])==0);""",
            "A stream does not preserve application record boundaries. The receiver chooses how many bytes to request.",
        ),
        E(
            "Retain binary zeros",
            "Send bytes 1, 0, 2 through a pipe.",
            "All three bytes are preserved.",
            r"""int fds[2];unsigned char data[]={1,0,2},out[3]={0};CHECK(pipe(fds)==0);CHECK(write(fds[1],data,3)==3);CHECK(close(fds[1])==0);CHECK(read(fds[0],out,3)==3&&memcmp(data,out,3)==0);CHECK(close(fds[0])==0);""",
            "POSIX reads report lengths and do not interpret null-terminated strings.",
        ),
        E(
            "Account for duplicated ownership",
            "Duplicate the write descriptor, then close both before reading EOF.",
            "EOF arrives after both references close.",
            r"""int fds[2];CHECK(pipe(fds)==0);int duplicate=dup(fds[1]);CHECK(duplicate>=0);CHECK(close(fds[1])==0&&close(duplicate)==0);char byte=0;CHECK(read(fds[0],&byte,1)==0);CHECK(close(fds[0])==0);""",
            "Closing only the original descriptor would leave another writer reference alive.",
        ),
        E(
            "Transfer a bounded record decoder",
            "Read exactly a two-byte tag from a three-byte payload.",
            "The tag is OK and one byte remains for the next read.",
            r"""int fds[2];CHECK(pipe(fds)==0);CHECK(write(fds[1],"OK7",3)==3);CHECK(close(fds[1])==0);char tag[3]={0},value=0;CHECK(read(fds[0],tag,2)==2&&read(fds[0],&value,1)==1);CHECK(strcmp(tag,"OK")==0&&value=='7');CHECK(close(fds[0])==0);""",
            "The caller defines framing. Real protocol code must validate lengths and handle interruption or partial reads rather than assume every call fills its buffer.",
        ),
    ],
    headers="unistd.h sys/types.h",
    source="https://pubs.opengroup.org/onlinepubs/9799919799/functions/pipe.html",
    boundary="This lesson uses POSIX descriptors supported by the Linux container profile. The API is not part of ISO C17 and is not a native Windows runtime promise. Windows learners execute the same Linux worker through WSL 2.",
)

add(
    "Signals, interruption and minimal handlers",
    """A signal is an asynchronous notification delivered to a process or thread under platform rules. A handler can interrupt ordinary execution at an inconvenient point, so it cannot safely call arbitrary library functions or manipulate general shared state. Keep handlers minimal: record a permitted signal flag and let normal control flow perform cleanup. volatile sig_atomic_t is the standard C pattern for a simple handler communication flag, but volatile is not a general thread synchronization mechanism. A synchronous raise in this fixture makes observation deterministic. Production signal handling needs a broader shutdown and interrupted-system-call policy.""",
    """signal installs a handler and returns the previous disposition or SIG_ERR. raise delivers a signal to the running program according to the implementation. A handler receives the signal number. Assign a sig_atomic_t flag and return. Do not call printf, malloc or mutex operations from a portable signal handler. The Linux production alternative sigaction offers more precise disposition control and is a separate POSIX API.""",
    [
        ("Signal handler", "A function invoked for an asynchronous signal notification."),
        ("Async-signal safety", "The restricted operations permitted in signal-handler context."),
        ("sig_atomic_t", "An integer type usable for simple atomic access in signal handling."),
    ],
    [
        E(
            "Install and restore a handler",
            "Install the lesson handler for SIGINT and restore the previous disposition.",
            "Both operations succeed.",
            r"""void (*previous)(int)=signal(SIGINT,lesson_handler);CHECK(previous!=SIG_ERR);CHECK(signal(SIGINT,previous)!=SIG_ERR);""",
            "The fixture restores process state instead of leaving a changed signal policy for unrelated later work.",
        ),
        E(
            "Record a raised notification",
            "Raise SIGINT while the lesson handler is installed.",
            "The signal flag becomes one.",
            r"""signal_seen=0;void (*previous)(int)=signal(SIGINT,lesson_handler);CHECK(previous!=SIG_ERR);CHECK(raise(SIGINT)==0);CHECK(signal_seen==1);CHECK(signal(SIGINT,previous)!=SIG_ERR);""",
            "The handler only assigns a flag. The ordinary flow performs assertions and restoration after the handler returns.",
        ),
        E(
            "Keep work outside the handler",
            "Translate an already set flag into a normal-flow shutdown decision.",
            "The normal-flow decision becomes stop.",
            r"""signal_seen=1;bool stop=(signal_seen!=0);CHECK(stop);signal_seen=0;""",
            "Complex cleanup belongs outside the handler, where ordinary library and ownership rules apply.",
        ),
        E(
            "Handle no notification",
            "Inspect a cleared signal flag.",
            "The shutdown decision remains false.",
            r"""signal_seen=0;CHECK(signal_seen==0);""",
            "The explicit initial state prevents a stale flag from being mistaken for a new event.",
        ),
        E(
            "Reset between independent operations",
            "Set then clear the flag in ordinary control flow.",
            "The next operation begins without a stale notification.",
            r"""signal_seen=1;signal_seen=0;CHECK(signal_seen==0);""",
            "Reset policy is part of lifecycle design. A real event loop must consider whether clearing can race with a new notification.",
        ),
        E(
            "Transfer a bounded shutdown model",
            "Stop admitting work after observing the signal flag while retaining active-work count.",
            "Admission stops and unfinished work remains visible.",
            r"""bool accepting=true;int active=2;signal_seen=1;if(signal_seen)accepting=false;CHECK(!accepting&&active==2);signal_seen=0;""",
            "A stop request does not mean in-flight operations completed. Drain or cancel them under a separate bounded policy.",
        ),
    ],
    headers="signal.h",
    helper="""static volatile sig_atomic_t signal_seen=0;
static void lesson_handler(int number){if(number==SIGINT)signal_seen=1;}""",
    source="https://www.gnu.org/software/libc/manual/html_node/Signal-Handling.html",
    boundary="The reference temporarily installs and restores a handler inside its own worker process. It does not signal other processes or change the host engine. For real POSIX services, study sigaction, signal masks, EINTR and a documented graceful-shutdown sequence.",
)

add(
    "POSIX threads and joined object lifetimes",
    """A thread executes concurrently within the process and shares its address space. Passing a pointer to a thread does not extend the target lifetime. Keep the argument object alive until the worker no longer accesses it, normally by joining the worker before leaving its owning scope. Each worker can write to distinct result storage without a mutex when no conflicting access occurs and the parent waits before reading. Shared mutation needs synchronization, taught next. Thread creation and joining can fail, so their return values belong to the resource contract. Detached threads require a different ownership design and are not a shortcut around joining.""",
    """pthread_create takes a pointer to a pthread_t, optional attributes, a function void *(*)(void *) and an argument pointer. The worker converts that argument back to its actual type. pthread_join waits for termination and can retrieve a returned pointer, whose lifetime still needs justification. POSIX pthread functions generally return an error number directly rather than setting errno in the same way as read or write.""",
    [
        (
            "Thread argument lifetime",
            "The interval during which a worker may access its supplied data.",
        ),
        (
            "Join",
            "Waiting for a specific thread to finish and reclaiming joinable-thread resources.",
        ),
        ("Disjoint result storage", "Separate objects written by separate workers."),
    ],
    [
        E(
            "Join one calculation",
            "Start a thread squaring input 7 and join it.",
            "The retained result is 49.",
            r"""struct Work work={.input=7,.output=0};pthread_t thread;CHECK(pthread_create(&thread,NULL,square_worker,&work)==0);CHECK(pthread_join(thread,NULL)==0);CHECK(work.output==49);""",
            "The stack argument remains alive until after join. Reading output before synchronization would not have this contract.",
        ),
        E(
            "Keep separate arguments",
            "Start two workers with inputs 2 and 3.",
            "Their independent outputs are 4 and 9.",
            r"""struct Work work[2]={{2,0},{3,0}};pthread_t threads[2];for(size_t i=0;i<2;i++)CHECK(pthread_create(&threads[i],NULL,square_worker,&work[i])==0);for(size_t i=0;i<2;i++)CHECK(pthread_join(threads[i],NULL)==0);CHECK(work[0].output==4&&work[1].output==9);""",
            "Each worker receives its own stable object rather than the address of one changing loop variable.",
        ),
        E(
            "Retrieve a stable pointer result",
            "Have the worker return its caller-owned argument pointer.",
            "Join returns that same live object address.",
            r"""struct Work work={5,0};pthread_t thread;void *returned=NULL;CHECK(pthread_create(&thread,NULL,square_worker,&work)==0);CHECK(pthread_join(thread,&returned)==0);CHECK(returned==&work&&work.output==25);""",
            "The returned pointer is valid because the caller still owns its storage. Returning a pointer to a worker-local automatic object would be invalid.",
        ),
        E(
            "Handle a zero input",
            "Run the worker on input zero.",
            "The output is zero.",
            r"""struct Work work={0,9};pthread_t thread;CHECK(pthread_create(&thread,NULL,square_worker,&work)==0);CHECK(pthread_join(thread,NULL)==0);CHECK(work.output==0);""",
            "The result demonstrates real computation rather than relying on the initial output field.",
        ),
        E(
            "Aggregate after all joins",
            "Run four workers for inputs 1 through 4 and sum results afterward.",
            "The total is 30.",
            r"""struct Work work[4]={{1,0},{2,0},{3,0},{4,0}};pthread_t threads[4];for(size_t i=0;i<4;i++)CHECK(pthread_create(&threads[i],NULL,square_worker,&work[i])==0);int sum=0;for(size_t i=0;i<4;i++){CHECK(pthread_join(threads[i],NULL)==0);sum+=work[i].output;}CHECK(sum==30);""",
            "Only the parent mutates the aggregate. Worker completion order does not change the integer result.",
        ),
        E(
            "Transfer reusable execution",
            "Run the same argument object through two joined invocations sequentially.",
            "The second input produces its own output 16.",
            r"""struct Work work={3,0};pthread_t thread;CHECK(pthread_create(&thread,NULL,square_worker,&work)==0);CHECK(pthread_join(thread,NULL)==0);work.input=4;CHECK(pthread_create(&thread,NULL,square_worker,&work)==0);CHECK(pthread_join(thread,NULL)==0);CHECK(work.output==16);""",
            "Reusing storage is safe after the previous worker has finished. Overlapping invocations on the same mutable argument would need synchronization.",
        ),
    ],
    headers="pthread.h",
    helper="""struct Work{int input,output;};
static void *square_worker(void *argument){struct Work *work=argument;work->output=work->input*work->input;return work;}""",
    source="https://pubs.opengroup.org/onlinepubs/9799919799/functions/pthread_create.html",
    boundary="This is actual pthread execution in the Linux C profile. It is a POSIX capability rather than an ISO C17 requirement. Every worker is joined, and all argument objects outlive their workers.",
)

add(
    "Mutexes, condition variables and predicate loops",
    """A mutex protects shared state only when every relevant reader and writer follows the same locking protocol. A condition variable lets a thread wait for a state predicate to become true while releasing the mutex atomically during the wait. Notifications are not stored as durable messages, and waking does not prove the predicate is true. Always recheck it in a loop to handle spurious wakeups and other consumers. Change the predicate under the same mutex used by waiters. Keep lock ownership and destruction explicit, and do not destroy a mutex or condition variable while another thread can still use it.""",
    """pthread_mutex_lock and unlock delimit the protected region. pthread_cond_wait expects the mutex to be locked, releases it while waiting, and reacquires it before returning. while(!ready) wait is the correct shape for this fixture. Signal after updating the protected state. Join the worker before destroying synchronization objects. A sleep cannot replace the predicate protocol.""",
    [
        ("Predicate", "The shared-state condition a waiting thread actually needs."),
        (
            "Condition variable",
            "A mechanism for waiting while atomically releasing and reacquiring a mutex.",
        ),
        ("Spurious wakeup", "A return from waiting that still requires predicate rechecking."),
    ],
    [
        E(
            "Protect a shared count",
            "Run four threads doing one hundred locked increments each.",
            "The final count is 400.",
            r"""CHECK(locked_total(4,100)==400);""",
            "Every increment is inside the same critical section, and the parent joins all writers before reading the final value.",
        ),
        E(
            "Handle one worker",
            "Run one worker doing seven increments.",
            "The result is 7.",
            r"""CHECK(locked_total(1,7)==7);""",
            "The sequential boundary exercises the same synchronization implementation without depending on contention.",
        ),
        E(
            "Handle zero loop iterations",
            "Run two workers whose increment loops are empty.",
            "The result remains zero.",
            r"""CHECK(locked_total(2,0)==0);""",
            "Worker creation and cleanup still occur even though the protected state never changes.",
        ),
        E(
            "Wait for a predicate",
            "Wait until a worker publishes ready with value 42.",
            "The parent observes value 42.",
            r"""CHECK(wait_for_value()==42);""",
            "The while loop checks actual state after every wakeup. The signal itself is not treated as the result payload.",
        ),
        E(
            "Repeat independent synchronization",
            "Create and destroy the predicate fixture twice.",
            "Both operations return 42.",
            r"""CHECK(wait_for_value()==42&&wait_for_value()==42);""",
            "Each invocation owns fresh synchronization objects and joins before destruction, avoiding cross-run state leakage.",
        ),
        E(
            "Transfer count invariance",
            "Compare two workers times five increments with five workers times two.",
            "Both totals are 10.",
            r"""CHECK(locked_total(2,5)==10&&locked_total(5,2)==10);""",
            "Scheduling changes but the protected update count remains invariant. This is correctness evidence, not a performance comparison.",
        ),
    ],
    headers="pthread.h",
    helper="""struct CounterState{pthread_mutex_t mutex;int count,iterations;};
static void *increment_worker(void *argument){struct CounterState *s=argument;for(int i=0;i<s->iterations;i++){CHECK(pthread_mutex_lock(&s->mutex)==0);s->count++;CHECK(pthread_mutex_unlock(&s->mutex)==0);}return NULL;}
static int locked_total(size_t workers,int iterations){CHECK(workers<=5);struct CounterState s={.count=0,.iterations=iterations};CHECK(pthread_mutex_init(&s.mutex,NULL)==0);pthread_t threads[5];for(size_t i=0;i<workers;i++)CHECK(pthread_create(&threads[i],NULL,increment_worker,&s)==0);for(size_t i=0;i<workers;i++)CHECK(pthread_join(threads[i],NULL)==0);int result=s.count;CHECK(pthread_mutex_destroy(&s.mutex)==0);return result;}
struct ReadyState{pthread_mutex_t mutex;pthread_cond_t condition;bool ready;int value;};
static void *publish_worker(void *argument){struct ReadyState *s=argument;CHECK(pthread_mutex_lock(&s->mutex)==0);s->value=42;s->ready=true;CHECK(pthread_cond_signal(&s->condition)==0);CHECK(pthread_mutex_unlock(&s->mutex)==0);return NULL;}
static int wait_for_value(void){struct ReadyState s={.ready=false,.value=0};CHECK(pthread_mutex_init(&s.mutex,NULL)==0);CHECK(pthread_cond_init(&s.condition,NULL)==0);pthread_t worker;CHECK(pthread_create(&worker,NULL,publish_worker,&s)==0);CHECK(pthread_mutex_lock(&s.mutex)==0);while(!s.ready)CHECK(pthread_cond_wait(&s.condition,&s.mutex)==0);int result=s.value;CHECK(pthread_mutex_unlock(&s.mutex)==0);CHECK(pthread_join(worker,NULL)==0);CHECK(pthread_cond_destroy(&s.condition)==0);CHECK(pthread_mutex_destroy(&s.mutex)==0);return result;}""",
    source="https://pubs.opengroup.org/onlinepubs/9799919799/functions/pthread_cond_wait.html",
)

add(
    "C11 atomics and release-acquire publication",
    """Atomic types make individual accesses participate in a defined concurrency model. They are not interchangeable with volatile, and they do not automatically protect a multi-field invariant. The default sequentially consistent operations are a useful starting point. Weaker memory orders require a proof connecting the writer and reader. A release store can publish preceding writes to a reader whose acquire load observes that store. A relaxed counter can count independent events without publishing unrelated memory. Lock-free status is implementation-dependent; atomic does not mean every operation avoids a lock on every platform.""",
    """atomic_int declares an atomic integer and atomic_init initializes it before sharing. atomic_fetch_add returns the previous value. atomic_compare_exchange_strong updates only when the current value matches expected and writes the observed value back to expected on failure. memory_order_release and memory_order_acquire form a publication relationship when the acquire observes the release. Avoid hand-built lock-free containers until ownership, reclamation and ABA hazards are understood.""",
    [
        ("Atomic object", "An object accessed through the C atomic operation contract."),
        ("Memory order", "The ordering guarantees requested by an atomic operation."),
        ("Publication", "Making initialized non-atomic state visible through synchronization."),
    ],
    [
        E(
            "Inspect fetch-add semantics",
            "Add 3 to an atomic integer initially 2.",
            "The returned old value is 2 and current value is 5.",
            r"""atomic_int value;atomic_init(&value,2);int old=atomic_fetch_add(&value,3);CHECK(old==2&&atomic_load(&value)==5);""",
            "The return value is the prior state. Confusing it with the new value can create off-by-one ticketing logic.",
        ),
        E(
            "Compare and exchange successfully",
            "Replace expected value 2 with 7.",
            "The operation succeeds and stores 7.",
            r"""atomic_int value;atomic_init(&value,2);int expected=2;CHECK(atomic_compare_exchange_strong(&value,&expected,7));CHECK(atomic_load(&value)==7);""",
            "The update is conditional on the observed state, not an unconditional assignment.",
        ),
        E(
            "Inspect failed compare-exchange",
            "Attempt replacement with stale expected value 2 when current is 3.",
            "It fails and expected becomes 3.",
            r"""atomic_int value;atomic_init(&value,3);int expected=2;CHECK(!atomic_compare_exchange_strong(&value,&expected,7));CHECK(expected==3&&atomic_load(&value)==3);""",
            "The API returns current observation through expected, which a retry loop must handle deliberately.",
        ),
        E(
            "Count independent events",
            "Perform ten relaxed increments before reading in the same thread.",
            "The count is 10.",
            r"""atomic_int count;atomic_init(&count,0);for(int i=0;i<10;i++)atomic_fetch_add_explicit(&count,1,memory_order_relaxed);CHECK(atomic_load_explicit(&count,memory_order_relaxed)==10);""",
            "This fixture demonstrates the counter API, not publication of unrelated memory. A concurrent relaxed counter has a different reasoning purpose from a readiness flag.",
        ),
        E(
            "Publish initialized data",
            "Use a release flag from a worker and acquire it before reading its payload.",
            "The payload is 42.",
            r"""struct Publication p;atomic_init(&p.ready,false);p.value=0;pthread_t worker;CHECK(pthread_create(&worker,NULL,atomic_publisher,&p)==0);while(!atomic_load_explicit(&p.ready,memory_order_acquire)){sched_yield();}CHECK(p.value==42);CHECK(pthread_join(worker,NULL)==0);""",
            "The payload read follows the acquire observation of the release store. Changing the flag to an ordinary or merely volatile object would remove the required synchronization.",
        ),
        E(
            "Transfer an atomic exchange",
            "Replace a flag value and inspect the returned prior state.",
            "The old state is false and the new state true.",
            r"""atomic_bool ready;atomic_init(&ready,false);bool old=atomic_exchange(&ready,true);CHECK(!old&&atomic_load(&ready));""",
            "Exchange is one atomic operation. A separate load then store would not provide the same indivisible state transition under concurrent access.",
        ),
    ],
    headers="stdatomic.h pthread.h sched.h",
    helper="""struct Publication{atomic_bool ready;int value;};
static void *atomic_publisher(void *argument){struct Publication *p=argument;p->value=42;atomic_store_explicit(&p->ready,true,memory_order_release);return NULL;}""",
    source="https://gcc.gnu.org/onlinedocs/gcc/_005f_005fatomic-Builtins.html",
    boundary="The reference executes a tiny joined publication example. It does not implement a general lock-free queue or memory-reclamation scheme. The cited GCC documentation also explains ordering concepts; the lesson source uses standard C11 atomics available in C17, not compiler builtin spellings.",
)

add(
    "Data layout, locality and honest performance experiments",
    """Memory access patterns can dominate arithmetic cost. An array of structs keeps each record together; a struct of arrays keeps one field across many records contiguous. Which layout is better depends on the operations performed, not a universal rule. Padding, alignment, cache lines and compiler vectorization influence observed performance. Begin with equivalent results and operation counts, then measure representative workloads under controlled builds. Do not publish a speedup based on one tiny timing or assume a particular cache-line size from a diagram. Optimization must preserve bounds, aliasing and numerical contracts.""",
    """sizeof reports actual object size including padding. offsetof gives a field offset without dereferencing a null pointer. Iterate only over initialized logical elements. restrict can promise nonaliasing to the compiler, but violating that promise is a correctness defect; it is not a harmless performance hint. The fixture compares layouts semantically and intentionally makes no wall-clock threshold assertion.""",
    [
        ("Locality", "Accessing nearby data within a short time interval."),
        ("Array of structs", "A layout grouping complete records together."),
        ("Struct of arrays", "A layout grouping each field across records together."),
    ],
    [
        E(
            "Sum one field in records",
            "Sum x fields from three Point records.",
            "The result is 6.",
            r"""struct Point records[]={{1,10},{2,20},{3,30}};int sum=0;for(size_t i=0;i<3;i++)sum+=records[i].x;CHECK(sum==6);""",
            "This traversal touches a selected field in each record. Whether unused fields waste bandwidth depends on the real layout and workload.",
        ),
        E(
            "Compute the same result by columns",
            "Sum an x column containing 1, 2, 3.",
            "The result is also 6.",
            r"""int x[]={1,2,3};int y[]={10,20,30};int sum=0;for(size_t i=0;i<3;i++)sum+=x[i];CHECK(sum==6&&y[2]==30);""",
            "Equivalent semantics must be established before comparing timings. The y column remains independent storage.",
        ),
        E(
            "Inspect legal field offsets",
            "Inspect x and y offsets in Point.",
            "Offsets are within the struct and preserve declaration order.",
            r"""CHECK(offsetof(struct Point,x)<sizeof(struct Point));CHECK(offsetof(struct Point,y)>offsetof(struct Point,x));""",
            "The check does not assume an exact padding count. Layout is an ABI property that may vary by implementation.",
        ),
        E(
            "Count algorithmic work",
            "Scan six values and count iterations.",
            "Exactly six visits occur.",
            r"""int values[]={1,2,3,4,5,6};size_t visits=0;int sum=0;for(size_t i=0;i<6;i++){visits++;sum+=values[i];}CHECK(visits==6&&sum==21);""",
            "Deterministic operation evidence is different from elapsed-time measurement, which needs repeated controlled experiments.",
        ),
        E(
            "Preserve result under blocking",
            "Sum the same data in blocks of two.",
            "The total remains 21.",
            r"""int values[]={1,2,3,4,5,6};int sum=0;for(size_t block=0;block<6;block+=2)for(size_t i=block;i<block+2;i++)sum+=values[i];CHECK(sum==21);""",
            "This toy blocking change preserves bounds exactly. Real blocked loops must handle a final partial block.",
        ),
        E(
            "Transfer a partial block",
            "Sum five values in blocks of two with a bounded final block.",
            "The total is 15 without a sixth access.",
            r"""int values[]={1,2,3,4,5};int sum=0;for(size_t block=0;block<5;block+=2){size_t end=block+2;if(end>5)end=5;for(size_t i=block;i<end;i++)sum+=values[i];}CHECK(sum==15);""",
            "The incomplete final block is a correctness case that an optimization must retain. Timing only even-sized inputs would miss it.",
        ),
    ],
    helper="struct Point{int x,y;};",
    source="https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html",
)

add(
    "C ABI boundaries and foreign-function ownership",
    """An application binary interface describes how compiled components exchange calls, values and symbols. A C function name alone does not define the entire contract: integer widths, struct layout, calling convention, ownership, error reporting and callback lifetime also matter. C interfaces are often used from C++, Rust or managed languages, but each side must agree on representation and who releases returned storage. Prefer explicit lengths and fixed-width types for data crossing the boundary. Do not return pointers to automatic locals or require another language to guess which allocator should free an allocation.""",
    """extern declares a function or object defined elsewhere; C++ callers use an extern \"C\" declaration wrapper to request C linkage. A stable buffer API can accept caller-owned output plus capacity and return a status and required length. Keep structs simple and versioned when they form a public ABI. A foreign pointer must satisfy the same C lifetime, alignment and bounds rules as a native pointer.""",
    [
        ("ABI", "The binary-level contract between compiled components."),
        (
            "Calling convention",
            "The rules for passing arguments, returning results and managing call state.",
        ),
        (
            "Allocator boundary",
            "The component responsible for releasing storage created by a particular allocator.",
        ),
    ],
    [
        E(
            "Use caller-owned output",
            "Copy hello into sufficient caller storage through a status API.",
            "The output is complete and required length is 5.",
            r"""char out[8];size_t required=0;CHECK(copy_api("hello",out,sizeof out,&required)==API_OK);CHECK(required==5&&strcmp(out,"hello")==0);""",
            "Caller-owned storage avoids requiring the foreign runtime to guess a deallocator.",
        ),
        E(
            "Report insufficient capacity",
            "Request the same copy into four bytes.",
            "The status is too-small and required length is 5.",
            r"""char out[4]="old";size_t required=0;CHECK(copy_api("hello",out,sizeof out,&required)==API_TOO_SMALL);CHECK(required==5&&strcmp(out,"old")==0);""",
            "The API reports the required payload length and preserves output on failure. The caller must reserve one more byte for termination.",
        ),
        E(
            "Support a size query",
            "Call with no output buffer and capacity zero.",
            "The required payload length is still reported.",
            r"""size_t required=0;CHECK(copy_api("abc",NULL,0,&required)==API_TOO_SMALL&&required==3);""",
            "A deliberate size-query mode is useful across language boundaries, but it must be specified rather than inferred from null behavior.",
        ),
        E(
            "Reject a missing required-output pointer",
            "Call without a place to report required length.",
            "The API returns invalid.",
            r"""char out[4];CHECK(copy_api("abc",out,sizeof out,NULL)==API_INVALID);""",
            "Validation precedes dereference. Every pointer parameter has an explicit role and null policy.",
        ),
        E(
            "Keep fixed-width values exact",
            "Pass a uint32_t value through an identity boundary.",
            "All 32 bits remain unchanged.",
            r"""uint32_t value=UINT32_C(0x89abcdef);CHECK(identity_u32(value)==value);""",
            "A foreign declaration must use a compatible unsigned 32-bit representation, not assume that its default integer type matches.",
        ),
        E(
            "Transfer an empty payload",
            "Copy an empty string into one byte.",
            "The API succeeds and stores a terminator.",
            r"""char out[1];size_t required=9;CHECK(copy_api("",out,sizeof out,&required)==API_OK&&required==0&&out[0]=='\0');""",
            "The empty payload still requires one writable byte under this null-terminated ABI contract.",
        ),
    ],
    helper="""enum ApiStatus{API_OK,API_TOO_SMALL,API_INVALID};
static enum ApiStatus copy_api(const char *source,char *out,size_t capacity,size_t *required){if(source==NULL||required==NULL)return API_INVALID;size_t n=strlen(source);*required=n;if(n==SIZE_MAX||out==NULL||capacity<=n)return API_TOO_SMALL;memcpy(out,source,n+1);return API_OK;}
static uint32_t identity_u32(uint32_t value){return value;}""",
    source="https://gcc.gnu.org/onlinedocs/gcc/Code-Gen-Options.html",
    boundary="The pad tests the C side of an ABI contract. Calling it from another language requires a separately compiled shared library and matching foreign declarations, plus explicit loading and ownership tests. Do not claim cross-language acceptance from this one-file executable alone.",
)

add(
    "State-machine parsing and bounded input grammars",
    """A parser should define the language it accepts before processing bytes. A small state machine makes separator, digit and termination rules visible. It is safer than repeatedly guessing with partial conversions and ignoring leftovers. This lesson parses a deliberately narrow grammar: one or more unsigned decimal integers separated by single commas, with no spaces, signs or quoted fields. It is not a general CSV parser. Each digit update checks for overflow before multiplying by ten, and the output count is bounded by caller capacity. Invalid input preserves the caller output by parsing into a bounded temporary array first.""",
    """The parser alternates between expecting a digit and accepting further digits or a comma. A comma requires a completed number and another number afterward. End-of-input commits the last value only if a digit was seen. The accumulator bound uses value>(UINT_MAX-digit)/10 before value*10+digit. A temporary staging array makes the final output update failure-atomic for the declared maximum of eight numbers.""",
    [
        ("Grammar", "The exact forms of input a parser accepts."),
        ("Parser state", "The information needed to interpret the next byte."),
        ("Staged output", "Temporary results committed only after complete validation."),
    ],
    [
        E(
            "Parse a valid list",
            "Parse 1,20,3 into capacity three.",
            "Three values are returned in order.",
            r"""unsigned out[3]={0};size_t count=0;CHECK(parse_list("1,20,3",out,3,&count)&&count==3&&out[0]==1&&out[1]==20&&out[2]==3);""",
            "The parser validates the entire grammar before publishing output.",
        ),
        E(
            "Reject an empty field",
            "Parse 1,,3.",
            "The parse fails and prior output is unchanged.",
            r"""unsigned out[3]={9,9,9};size_t count=7;CHECK(!parse_list("1,,3",out,3,&count)&&out[0]==9&&count==7);""",
            "Two separators in a row violate the required-digit state.",
        ),
        E(
            "Reject a trailing separator",
            "Parse 1,2,.",
            "The parse fails.",
            r"""unsigned out[3]={0};size_t count=0;CHECK(!parse_list("1,2,",out,3,&count));""",
            "The final comma requires another number. Accepting it silently would change the declared grammar.",
        ),
        E(
            "Enforce output capacity",
            "Parse three values into capacity two.",
            "The operation fails without an overflow.",
            r"""unsigned out[2]={9,9};size_t count=7;CHECK(!parse_list("1,2,3",out,2,&count)&&out[0]==9&&count==7);""",
            "The destination capacity is a hard bound, not a suggestion. The staged parser rejects excess before copying.",
        ),
        E(
            "Reject numeric overflow",
            "Parse a number with far too many digits.",
            "The range check rejects it.",
            r"""unsigned out[1]={0};size_t count=0;CHECK(!parse_list("999999999999999999999999",out,1,&count));""",
            "The arithmetic check occurs before the overflowing multiplication.",
        ),
        E(
            "Transfer exact grammar boundaries",
            "Parse zero successfully and reject leading whitespace.",
            "Zero is valid; space-prefixed input is not.",
            r"""unsigned out[1]={9};size_t count=0;CHECK(parse_list("0",out,1,&count)&&out[0]==0&&count==1);CHECK(!parse_list(" 1",out,1,&count));""",
            "Whitespace handling is a deliberate grammar choice. A higher-level input layer can normalize it explicitly if the product requires that policy.",
        ),
    ],
    helper=r"""static bool parse_list(const char *text,unsigned *out,size_t capacity,size_t *count){if(text==NULL||out==NULL||count==NULL)return false;unsigned temporary[8];size_t used=0;unsigned value=0;bool digit_seen=false;for(const unsigned char *p=(const unsigned char *)text;;p++){unsigned char c=*p;if(c>='0'&&c<='9'){unsigned digit=(unsigned)(c-'0');if(value>(UINT_MAX-digit)/10U)return false;value=value*10U+digit;digit_seen=true;}else if(c==','||c=='\0'){if(!digit_seen||used>=8||used>=capacity)return false;temporary[used++]=value;if(c=='\0')break;value=0;digit_seen=false;}else{return false;}}memcpy(out,temporary,used*sizeof temporary[0]);*count=used;return true;}""",
)

add(
    "Capstone: a validated data pipeline with explicit ownership",
    """The capstone combines parsing, range checks, bounded storage, deterministic aggregation and failure-atomic output. A production C component is understandable when each boundary states its grammar, ownership, resource limit and failure behavior. This fixture accepts a narrow line format name,count with one comma, a short nonempty ASCII name and a nonnegative decimal count. It deliberately rejects quoting and multiline fields rather than pretending to implement full CSV. A real general-purpose CSV reader needs the richer format contract. The pipeline validates every record before committing its summary, so one malformed record cannot publish a partial total as if the batch completed.""",
    """parse_record separates a bounded name from a complete decimal value using strtol and an end pointer. summarize stages row count and total, checks addition before updating, and commits only when every row is valid. The output remains unchanged on failure. The separately prepared stats project illustrates headers and tests; this capstone keeps its full deterministic data path within the ordinary one-file pad.""",
    [
        ("Data contract", "The grammar, ranges and meaning required at a data boundary."),
        ("Batch atomicity", "Publishing a summary only after all required records are accepted."),
        (
            "Operational evidence",
            "Source-bound diagnostics and results explaining what actually completed.",
        ),
    ],
    [
        E(
            "Summarize valid records",
            "Process alpha,3 and beta,4.",
            "Two rows produce total 7.",
            r"""const char *rows[]={"alpha,3","beta,4"};struct Summary out={0};CHECK(summarize(rows,2,&out)&&out.rows==2&&out.total==7);""",
            "The total represents the complete accepted batch, not merely a successful prefix.",
        ),
        E(
            "Reject a malformed record",
            "Process one valid record followed by a negative count.",
            "The batch fails and the previous summary remains unchanged.",
            r"""const char *rows[]={"alpha,3","beta,-1"};struct Summary out={9,99};CHECK(!summarize(rows,2,&out)&&out.rows==9&&out.total==99);""",
            "Staging prevents a partial total from masquerading as a successful batch result.",
        ),
        E(
            "Handle an empty batch",
            "Summarize zero records.",
            "Rows and total are both zero.",
            r"""struct Summary out={9,99};CHECK(summarize(NULL,0,&out)&&out.rows==0&&out.total==0);""",
            "The empty input has an explicit identity result. No record pointer is accessed.",
        ),
        E(
            "Reject extra field syntax",
            "Parse a line with two commas.",
            "The record is rejected.",
            r"""unsigned value=0;CHECK(!parse_record("alpha,3,extra",&value));""",
            "The accepted grammar is intentionally narrow. Extra fields must not be silently ignored.",
        ),
        E(
            "Preserve a legitimate zero",
            "Process alpha,0.",
            "One row contributes zero to the total.",
            r"""const char *rows[]={"alpha,0"};struct Summary out={0};CHECK(summarize(rows,1,&out)&&out.rows==1&&out.total==0);""",
            "A zero measurement differs from missing or invalid input, and row count retains that distinction.",
        ),
        E(
            "Transfer repeatable recovery",
            "Fail one batch, then run a corrected batch against the same output.",
            "Only the corrected complete batch publishes total 8.",
            r"""const char *bad[]={"x,bad"},*good[]={"x,8"};struct Summary out={0};CHECK(!summarize(bad,1,&out));CHECK(summarize(good,1,&out)&&out.rows==1&&out.total==8);""",
            "The failed attempt leaves no hidden partial state. Re-running corrected input is safe under this pure in-memory batch contract.",
        ),
    ],
    headers="errno.h",
    helper=r"""struct Summary{size_t rows;unsigned total;};
static bool parse_record(const char *line,unsigned *out){if(line==NULL||out==NULL)return false;const char *comma=strchr(line,',');if(comma==NULL||comma==line||(size_t)(comma-line)>15||strchr(comma+1,',')!=NULL)return false;for(const char *p=line;p<comma;p++)if(!((*p>='a'&&*p<='z')||(*p>='A'&&*p<='Z')))return false;if(comma[1]<'0'||comma[1]>'9')return false;errno=0;char *end=NULL;unsigned long value=strtoul(comma+1,&end,10);if(errno==ERANGE||*end!='\0'||value>UINT_MAX)return false;*out=(unsigned)value;return true;}
static bool summarize(const char *const *rows,size_t count,struct Summary *out){if(out==NULL||(count>0&&rows==NULL)||count>100)return false;struct Summary staged={0};for(size_t i=0;i<count;i++){unsigned value=0;if(!parse_record(rows[i],&value)||value>UINT_MAX-staged.total)return false;staged.total+=value;staged.rows++;}*out=staged;return true;}""",
    boundary="Extend this project by writing a header contract, independent tests, a bounded file-reading adapter and a command-line error policy in a separately prepared directory. Add real CSV quoting only with an explicit state machine and tests for commas, escaped quotes, embedded newlines, malformed records and size limits. The current parser truthfully implements only its declared simple line grammar.",
)
