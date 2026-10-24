"""Allocation, data structures and reusable C component contracts."""

from render import add
from render import case as E

add(
    "Dynamic allocation and single-owner release",
    """Allocated storage lets a program choose capacity at runtime. malloc returns uninitialized storage or a null pointer on failure; calloc also initializes its bytes to zero. The caller must establish an owner responsible for exactly one release after the last use. free ends the allocation lifetime, so every pointer into that allocation becomes invalid even if its numeric address still looks familiar. Setting one pointer to NULL does not repair other aliases. Calculate allocation sizes without overflowing size_t before calling an allocator. A successful allocation says storage exists, not that application fields have been initialized meaningfully.""",
    """malloc(count * sizeof *items) avoids repeating the element type, but multiplication needs a prior bound check. Check the returned pointer before use. calloc(count,sizeof *items) accepts element count and size separately, while still requiring an application resource budget. free(NULL) is defined and harmless. The helper here returns NULL for a zero count by its own contract and refuses multiplication overflow before allocation.""",
    [
        ("Allocation owner", "The component responsible for releasing dynamic storage."),
        ("Dangling pointer", "A pointer whose target lifetime has ended."),
        ("Size overflow", "An allocation-size calculation wrapping to an insufficient value."),
    ],
    [
        E(
            "Allocate and initialize",
            "Allocate three ints, assign 2, 4, 6 and sum them.",
            "The sum is 12 before release.",
            r"""int *p=allocate_ints(3);CHECK(p!=NULL);p[0]=2;p[1]=4;p[2]=6;CHECK(p[0]+p[1]+p[2]==12);free(p);""",
            "malloc storage must be initialized before reading. The owner releases it after the final valid access.",
        ),
        E(
            "Inspect zero-initialized integers",
            "Allocate three ints with calloc and read them.",
            "All three values are zero.",
            r"""int *p=calloc(3,sizeof *p);CHECK(p!=NULL);CHECK(p[0]==0&&p[1]==0&&p[2]==0);free(p);""",
            "For integer objects, all-bits-zero represents zero. Do not generalize that claim blindly to every possible pointer or floating representation.",
        ),
        E(
            "Define the empty allocation policy",
            "Request zero elements through the helper.",
            "The helper returns NULL without an allocation.",
            r"""CHECK(allocate_ints(0)==NULL);""",
            "The wrapper makes zero-size behavior predictable. Raw allocator zero-size behavior should not be treated as a portable nonempty object.",
        ),
        E(
            "Reject multiplication overflow",
            "Request SIZE_MAX elements.",
            "The helper returns NULL before multiplication or allocation.",
            r"""CHECK(allocate_ints(SIZE_MAX)==NULL);""",
            "The division bound proves the product will fit. Testing a wrapped product after multiplication would be too late.",
        ),
        E(
            "Release an absent allocation",
            "Call free on NULL.",
            "The operation is harmless.",
            r"""int *p=NULL;free(p);CHECK(p==NULL);""",
            "This defined behavior simplifies cleanup paths. It does not make double-free of a non-null stale pointer valid.",
        ),
        E(
            "Transfer ownership cleanup",
            "Allocate one value, release it and clear the owning pointer.",
            "The owner records absence afterward.",
            r"""int *p=allocate_ints(1);CHECK(p!=NULL);*p=9;CHECK(*p==9);free(p);p=NULL;CHECK(p==NULL);""",
            "Clearing the owner reduces accidental reuse through that variable. Any aliases would still need to be retired by the ownership protocol.",
        ),
    ],
    helper="static int *allocate_ints(size_t count){if(count==0||count>SIZE_MAX/sizeof(int))return NULL;return malloc(count*sizeof(int));}",
    source="https://www.gnu.org/software/libc/manual/html_node/Memory-Allocation.html",
)

add(
    "Reallocation and a checked dynamic vector",
    """A dynamic vector separates logical length from allocated capacity. Growth may move the allocation, invalidating prior element pointers. realloc returns a new pointer on success; on failure for a nonzero requested size, the original allocation remains owned and unchanged. Assigning realloc directly to the only owning pointer can therefore lose the original allocation on failure. Keep the result in a temporary, validate it, then update the vector. Growth arithmetic needs overflow checks and a resource policy. The vector here owns ints and preserves its old state when a reserve request is rejected.""",
    """A vector stores data, len and cap. reserve ensures capacity without changing length. push reserves before writing data[len], then increments length. pop checks nonempty before decrementing. destroy frees storage and resets all fields, making repeated cleanup harmless under this local ownership contract. Never retain an element pointer across a call that may grow the vector.""",
    [
        ("Length", "The number of initialized logical elements."),
        ("Capacity", "The number of elements fitting in allocated storage."),
        ("Reallocation", "Resizing storage, potentially changing its address."),
    ],
    [
        E(
            "Push into an empty vector",
            "Push 3 and 5 into a zero-initialized vector.",
            "Length is 2 and values are retained.",
            r"""struct Vector v={0};CHECK(vector_push(&v,3)&&vector_push(&v,5));CHECK(v.len==2&&v.data[0]==3&&v.data[1]==5);vector_destroy(&v);""",
            "The zero state is a usable empty vector. Growth happens before the first write.",
        ),
        E(
            "Reserve without adding elements",
            "Reserve capacity eight.",
            "Capacity is at least eight while length stays zero.",
            r"""struct Vector v={0};CHECK(vector_reserve(&v,8));CHECK(v.cap>=8&&v.len==0);vector_destroy(&v);""",
            "Reservation is storage preparation, not logical insertion. Treating capacity as length would expose uninitialized elements.",
        ),
        E(
            "Grow while preserving contents",
            "Push twenty sequential values.",
            "Every stored value matches its index.",
            r"""struct Vector v={0};for(int i=0;i<20;i++)CHECK(vector_push(&v,i));for(size_t i=0;i<v.len;i++)CHECK(v.data[i]==(int)i);vector_destroy(&v);""",
            "Each successful growth preserves the previously initialized prefix. Old element pointers must not be used after a possible move.",
        ),
        E(
            "Pop from a nonempty vector",
            "Push 7 then pop it.",
            "The returned value is 7 and length becomes zero.",
            r"""struct Vector v={0};int out=0;CHECK(vector_push(&v,7));CHECK(vector_pop(&v,&out)&&out==7&&v.len==0);vector_destroy(&v);""",
            "The vector retains capacity after removal, which can make later pushes cheap without changing the empty logical state.",
        ),
        E(
            "Reject an empty pop",
            "Pop an empty vector with an existing output value.",
            "The operation fails and output stays 9.",
            r"""struct Vector v={0};int out=9;CHECK(!vector_pop(&v,&out)&&out==9);vector_destroy(&v);""",
            "The failure path performs no decrement and no out-of-bounds read.",
        ),
        E(
            "Transfer reserve failure atomicity",
            "Reject SIZE_MAX capacity after storing one item.",
            "The original value and length remain intact.",
            r"""struct Vector v={0};CHECK(vector_push(&v,4));CHECK(!vector_reserve(&v,SIZE_MAX));CHECK(v.len==1&&v.data[0]==4);vector_destroy(&v);""",
            "Arithmetic rejection happens before realloc. This deterministic case tests state preservation without depending on host memory exhaustion.",
        ),
    ],
    helper="""struct Vector{int *data;size_t len,cap;};
static bool vector_reserve(struct Vector *v,size_t cap){if(cap<=v->cap)return true;if(cap>SIZE_MAX/sizeof *v->data)return false;int *next=realloc(v->data,cap*sizeof *v->data);if(next==NULL)return false;v->data=next;v->cap=cap;return true;}
static bool vector_push(struct Vector *v,int value){if(v->len==v->cap){size_t next=v->cap? v->cap*2:4;if(next<v->cap||!vector_reserve(v,next))return false;}v->data[v->len++]=value;return true;}
static bool vector_pop(struct Vector *v,int *out){if(v->len==0||out==NULL)return false;*out=v->data[--v->len];return true;}
static void vector_destroy(struct Vector *v){free(v->data);v->data=NULL;v->len=0;v->cap=0;}""",
    source="https://www.gnu.org/software/libc/manual/html_node/Changing-Block-Size.html",
)

add(
    "Ownership APIs, borrowing and independent clones",
    """A reusable C component needs an ownership vocabulary. A borrowed pointer grants temporary access without transferring release responsibility. An owned result makes the caller responsible for destruction. A clone creates independent owned storage; a shallow struct copy usually does not. Document whether a function consumes its input on success, on failure, both or neither. Ambiguity produces leaks, double-free and use-after-free defects that can be difficult to diagnose after components are combined. The small text owner here has one destructor and an explicit clone operation. It never represents a shallow copy as a second independent owner.""",
    """The owner struct contains a char pointer and length. create allocates length plus one, copies bytes and writes a terminator. clone calls the same creation policy on a borrowed source. destroy releases and resets the owner. Use a const pointer for borrowed read access. Returning a struct by value can transfer ownership, but subsequent copies must obey the documented move-or-clone policy because C does not enforce it automatically.""",
    [
        ("Borrow", "Temporary access without taking release responsibility."),
        ("Owned result", "A value whose recipient must release its resources."),
        ("Clone", "An independent allocation containing equivalent data."),
    ],
    [
        E(
            "Create an owned string",
            "Create an owner for alpha.",
            "Length is 5 and content is alpha.",
            r"""struct Text t={0};CHECK(text_create(&t,"alpha"));CHECK(t.len==5&&strcmp(t.data,"alpha")==0);text_destroy(&t);""",
            "The owner contains both storage and logical length. The terminator is additional storage, not part of len.",
        ),
        E(
            "Clone independent storage",
            "Clone cat and mutate the clone to bat.",
            "The original remains cat.",
            r"""struct Text a={0},b={0};CHECK(text_create(&a,"cat")&&text_create(&b,a.data));b.data[0]='b';CHECK(strcmp(a.data,"cat")==0&&strcmp(b.data,"bat")==0);text_destroy(&a);text_destroy(&b);""",
            "Two independently allocated owners can be destroyed separately. A plain struct assignment would share the pointer and make that unsafe.",
        ),
        E(
            "Borrow without releasing",
            "Read through a const pointer borrowed from an owner.",
            "The borrowed content is ready.",
            r"""struct Text t={0};CHECK(text_create(&t,"ready"));const char *view=t.data;CHECK(strcmp(view,"ready")==0);text_destroy(&t);""",
            "The view must not be used after destruction. Only the owning object performs release.",
        ),
        E(
            "Represent an owned empty string",
            "Create an owner for empty text.",
            "Length is zero but a valid terminator exists.",
            r"""struct Text t={0};CHECK(text_create(&t,""));CHECK(t.len==0&&t.data!=NULL&&t.data[0]=='\0');text_destroy(&t);""",
            "An empty string still needs one byte under this contract. It differs from an uninitialized or destroyed owner.",
        ),
        E(
            "Make cleanup idempotent",
            "Destroy the same reset owner twice.",
            "The owner stays empty.",
            r"""struct Text t={0};CHECK(text_create(&t,"x"));text_destroy(&t);text_destroy(&t);CHECK(t.data==NULL&&t.len==0);""",
            "Resetting the owning fields makes this API safe for repeated cleanup. Other stale aliases are not made safe automatically.",
        ),
        E(
            "Transfer a deliberate move",
            "Move ownership by assigning the struct and clearing the source.",
            "Only the destination retains the allocation.",
            r"""struct Text source={0};CHECK(text_create(&source,"move"));struct Text destination=source;source=(struct Text){0};CHECK(source.data==NULL&&strcmp(destination.data,"move")==0);text_destroy(&destination);""",
            "The explicit source reset is the manual move protocol. Leaving two apparent owners would make destruction ambiguous.",
        ),
    ],
    helper="""struct Text{char *data;size_t len;};
static bool text_create(struct Text *out,const char *source){if(out==NULL||source==NULL||out->data!=NULL)return false;size_t n=strlen(source);if(n==SIZE_MAX)return false;char *data=malloc(n+1);if(data==NULL)return false;memcpy(data,source,n+1);out->data=data;out->len=n;return true;}
static void text_destroy(struct Text *t){free(t->data);t->data=NULL;t->len=0;}""",
)

add(
    "File streams, short operations and reliable closure",
    """A FILE stream buffers I/O and tracks state such as end-of-file and errors. A read operation reports what happened; feof predicts nothing before an attempted read reaches the end. A short read can mean EOF or an error, so inspect stream state appropriately. Writes and close operations can fail, especially when buffered data is flushed. Resource ownership includes closing the stream on every completed path, not merely after the happy-path computation. These examples use tmpfile, which creates an owned temporary stream removed on closure. They do not read or overwrite learner files.""",
    """fwrite and fread return element counts, not necessarily byte counts unless element size is one. fseek or rewind changes position; rewind also clears error and EOF indicators. fgetc returns int so every unsigned-char value remains distinct from EOF. fgets reads a bounded line and retains a newline when one fits. fclose releases the stream and may report a final write failure.""",
    [
        ("Stream state", "The position, buffering and error indicators associated with FILE."),
        ("Short read", "Fewer elements returned than requested."),
        ("EOF indicator", "State set after a read encounters the end of a stream."),
    ],
    [
        E(
            "Round-trip an owned stream",
            "Write abc, rewind and read three bytes.",
            "Three bytes return and match abc.",
            r"""FILE *f=tmpfile();CHECK(f!=NULL);CHECK(fwrite("abc",1,3,f)==3);rewind(f);char data[4]={0};CHECK(fread(data,1,3,f)==3&&strcmp(data,"abc")==0);CHECK(fclose(f)==0);""",
            "The terminator comes from initialized output storage, not from fread. Binary reads do not automatically append a string terminator.",
        ),
        E(
            "Observe a short read",
            "Request four bytes from a two-byte stream.",
            "Two bytes return and EOF becomes set.",
            r"""FILE *f=tmpfile();CHECK(f!=NULL);CHECK(fwrite("ab",1,2,f)==2);rewind(f);char data[4];size_t n=fread(data,1,4,f);CHECK(n==2&&feof(f)&&!ferror(f));CHECK(fclose(f)==0);""",
            "The count is the primary evidence. EOF explains why the remaining requested bytes were unavailable.",
        ),
        E(
            "Avoid prechecking EOF",
            "Inspect an empty stream before and after a read.",
            "EOF is false before the read and true afterward.",
            r"""FILE *f=tmpfile();CHECK(f!=NULL);CHECK(!feof(f));CHECK(fgetc(f)==EOF&&feof(f));CHECK(fclose(f)==0);""",
            "A while(!feof(f)) loop can process a nonexistent final record because EOF is discovered by reading.",
        ),
        E(
            "Read a bounded line",
            "Read a newline-terminated line into sufficient storage.",
            "The newline remains in the result.",
            r"""FILE *f=tmpfile();CHECK(f!=NULL);CHECK(fputs("red\n",f)>=0);rewind(f);char line[8];CHECK(fgets(line,sizeof line,f)!=NULL&&strcmp(line,"red\n")==0);CHECK(fclose(f)==0);""",
            "Trimming a newline is a separate application policy. A full buffer without newline may indicate a partial line rather than a complete record.",
        ),
        E(
            "Clear EOF by rewinding",
            "Reach EOF, rewind and read the first character again.",
            "The first character is available again.",
            r"""FILE *f=tmpfile();CHECK(f!=NULL);CHECK(fputc('x',f)!=EOF);rewind(f);CHECK(fgetc(f)=='x'&&fgetc(f)==EOF);rewind(f);CHECK(!feof(f)&&fgetc(f)=='x');CHECK(fclose(f)==0);""",
            "Stream state changes with positioning operations. A prior EOF is not a permanent property of the underlying content.",
        ),
        E(
            "Transfer binary zero bytes",
            "Write and read a byte sequence containing zero.",
            "All three bytes survive, including the middle zero.",
            r"""unsigned char source[]={1,0,2},out[3]={0};FILE *f=tmpfile();CHECK(f!=NULL);CHECK(fwrite(source,1,3,f)==3);rewind(f);CHECK(fread(out,1,3,f)==3&&memcmp(source,out,3)==0);CHECK(fclose(f)==0);""",
            "Binary data is length-delimited, not terminated by zero. String functions would incorrectly treat the middle zero as an endpoint.",
        ),
    ],
    source="https://www.gnu.org/software/libc/manual/html_node/Streams.html",
)

add(
    "Binary formats, byte order and representation boundaries",
    """A portable binary format specifies bytes, widths and byte order rather than dumping an in-memory struct. Host representation can differ in endianness, padding, alignment and type sizes. Explicit encoding makes the wire contract inspectable and avoids leaking padding bytes. A decoder must validate the available length before reading fields and reject unsupported versions or values. Use unsigned types for shifts and masks, with shift counts inside the type width. memcpy can safely copy object representation bytes when the destination object and sizes are valid, but interpreting arbitrary bytes as a typed object still requires a representation contract.""",
    """A big-endian 32-bit encoding stores the most significant byte first. Cast each input byte to uint32_t before shifting so integer promotion does not produce a problematic signed operation. Read four bytes only after checking length. Bitwise OR combines disjoint fields. The format here assumes eight-bit bytes and requires that with _Static_assert because its external definition uses octets.""",
    [
        ("Endianness", "The byte order used to represent multibyte values."),
        ("Wire format", "A documented serialized representation independent of host layout."),
        ("Alignment", "An address requirement for accessing an object through a type."),
    ],
    [
        E(
            "Encode a known word",
            "Encode 0x12345678 in big-endian order.",
            "The bytes are 12, 34, 56, 78 in hexadecimal.",
            r"""unsigned char out[4];encode_u32(UINT32_C(0x12345678),out);CHECK(out[0]==0x12&&out[1]==0x34&&out[2]==0x56&&out[3]==0x78);""",
            "The explicit byte contract does not depend on host endianness.",
        ),
        E(
            "Decode a known word",
            "Decode bytes 00, 00, 01, 00.",
            "The numeric value is 256.",
            r"""unsigned char data[]={0,0,1,0};uint32_t value=0;CHECK(decode_u32(data,4,&value)&&value==256);""",
            "Each byte is promoted to the intended unsigned width before shifting.",
        ),
        E(
            "Reject a truncated field",
            "Attempt to decode only three available bytes.",
            "The decoder fails and preserves output.",
            r"""unsigned char data[]={1,2,3};uint32_t value=9;CHECK(!decode_u32(data,3,&value)&&value==9);""",
            "Length validation occurs before any fourth-byte access. Reading first and diagnosing later would already violate bounds.",
        ),
        E(
            "Round-trip zero",
            "Encode and decode numeric zero.",
            "The result is zero.",
            r"""unsigned char out[4];encode_u32(0,out);uint32_t value=1;CHECK(decode_u32(out,4,&value)&&value==0);""",
            "Zero is a valid payload, not an absent field or string terminator in this format.",
        ),
        E(
            "Round-trip the maximum",
            "Encode and decode UINT32_MAX.",
            "All bits survive.",
            r"""unsigned char out[4];encode_u32(UINT32_MAX,out);uint32_t value=0;CHECK(decode_u32(out,4,&value)&&value==UINT32_MAX);""",
            "The boundary case exercises every high bit and catches signed intermediate mistakes.",
        ),
        E(
            "Transfer a framed payload",
            "Decode the four bytes after a one-byte version field.",
            "Version 1 and payload 7 are interpreted separately.",
            r"""unsigned char frame[]={1,0,0,0,7};uint32_t value=0;CHECK(frame[0]==1&&decode_u32(frame+1,sizeof frame-1,&value)&&value==7);""",
            "A format should reject unsupported versions before interpreting fields under the wrong schema.",
        ),
    ],
    helper="""_Static_assert(CHAR_BIT==8,"this octet format requires 8-bit bytes");
static void encode_u32(uint32_t value,unsigned char out[4]){out[0]=(unsigned char)(value>>24);out[1]=(unsigned char)(value>>16);out[2]=(unsigned char)(value>>8);out[3]=(unsigned char)value;}
static bool decode_u32(const unsigned char *data,size_t n,uint32_t *out){if(n<4||data==NULL||out==NULL)return false;*out=((uint32_t)data[0]<<24)|((uint32_t)data[1]<<16)|((uint32_t)data[2]<<8)|(uint32_t)data[3];return true;}""",
)

add(
    "Function pointers, callbacks and comparator contracts",
    """A function pointer lets a component accept behavior as data. The function type must match the call interface; casting an incompatible function pointer does not make the call valid. A callback contract also describes when it is invoked, whether it may retain input pointers and how errors are reported. qsort accepts a comparator returning negative, zero or positive according to ordering. Subtracting integers to implement comparison can overflow, so compare relationally instead. Sorting correctness depends on a consistent comparator; a contradictory ordering can invalidate algorithm assumptions even when individual calls compile.""",
    """int (*compare)(const void *,const void *) declares a function pointer rather than a function returning a pointer. qsort passes pointers to elements, which the comparator converts to the correct element type. (a>b)-(a<b) yields the required sign without subtracting the values themselves. A separate callback context can carry state when an API provides one; avoid hidden global mutable state for reusable components.""",
    [
        ("Function pointer", "A value designating a function with a particular call type."),
        ("Callback contract", "The rules for invoking and retaining data passed to a callback."),
        ("Comparator", "A function defining a consistent ordering relation."),
    ],
    [
        E(
            "Invoke through a function pointer",
            "Assign a doubling function and call it with 4.",
            "The result is 8.",
            r"""int (*transform)(int)=double_value;CHECK(transform(4)==8);""",
            "The pointer type agrees with the function declaration, so the compiler can check the call.",
        ),
        E(
            "Sort integers safely",
            "Sort 3, 1, 2 with a relational comparator.",
            "The order becomes 1, 2, 3.",
            r"""int values[]={3,1,2};qsort(values,3,sizeof values[0],compare_ints);CHECK(values[0]==1&&values[1]==2&&values[2]==3);""",
            "The comparator reports ordering rather than a numeric distance between elements.",
        ),
        E(
            "Compare extreme values",
            "Compare INT_MIN and INT_MAX.",
            "The result correctly reports the first is smaller.",
            r"""int a=INT_MIN,b=INT_MAX;CHECK(compare_ints(&a,&b)<0);""",
            "Returning a-b would overflow for this case. Relational comparisons avoid that undefined behavior.",
        ),
        E(
            "Retain equal values",
            "Sort duplicate values 2, 1, 2.",
            "Both copies of 2 remain.",
            r"""int values[]={2,1,2};qsort(values,3,sizeof values[0],compare_ints);CHECK(values[0]==1&&values[1]==2&&values[2]==2);""",
            "Sorting reorders elements; it does not deduplicate them. qsort also does not promise stable order among equal keys.",
        ),
        E(
            "Inject a predicate",
            "Count even values in 1, 2, 3, 4 through a callback.",
            "The count is 2.",
            r"""int values[]={1,2,3,4};CHECK(count_if(values,4,is_even)==2);""",
            "Traversal and selection policy are separate responsibilities with a clear typed interface.",
        ),
        E(
            "Transfer an empty callback traversal",
            "Count over zero logical elements.",
            "The result is zero and no element is accessed.",
            r"""CHECK(count_if(NULL,0,is_even)==0);""",
            "This helper explicitly accepts the empty null view because it makes no callback or element access.",
        ),
    ],
    helper="""static int double_value(int value){return value*2;}
static int compare_ints(const void *left,const void *right){int a=*(const int *)left,b=*(const int *)right;return (a>b)-(a<b);}
static bool is_even(int value){return value%2==0;}
static size_t count_if(const int *values,size_t n,bool (*predicate)(int)){size_t count=0;for(size_t i=0;i<n;i++)if(predicate(values[i]))count++;return count;}""",
    source="https://www.gnu.org/software/libc/manual/html_node/Array-Sort-Function.html",
)

add(
    "Linked lists and mutation-safe traversal",
    """A linked list stores each element in a node that points to the next node. It can insert at the head without moving all existing elements, but each allocation and pointer chase has a cost. The head pointer is part of the mutable structure, so a function changing it often receives a pointer to that pointer. Every node has one release responsibility. When deleting during traversal, save the next pointer before freeing the current node; reading current->next afterward would use an expired object. Lists are useful when their mutation pattern fits the problem, not simply because pointers make them possible.""",
    """struct Node contains a value and next pointer. push_front allocates first and changes the head only after success. A Node **head lets the helper update the caller head. Iterative destruction retains next before free and resets the head afterward. Reverse uses previous, current and next pointers, maintaining a processed-prefix invariant without new allocations.""",
    [
        ("Node", "An element plus linkage to another element."),
        ("Head pointer", "The entry point to a linked structure."),
        ("Mutation invariant", "A structural property preserved while links are changed."),
    ],
    [
        E(
            "Insert at the head",
            "Push 1 and then 2.",
            "The list order is 2 then 1.",
            r"""struct Node *head=NULL;CHECK(push_front(&head,1)&&push_front(&head,2));CHECK(head->value==2&&head->next->value==1);destroy_list(&head);""",
            "Head insertion reverses arrival order. If FIFO order is required, a tail pointer or different structure is needed.",
        ),
        E(
            "Count a constructed list",
            "Push three values and count nodes.",
            "The length is 3.",
            r"""struct Node *head=NULL;for(int i=0;i<3;i++)CHECK(push_front(&head,i));CHECK(list_length(head)==3);destroy_list(&head);""",
            "The traversal stops at NULL and does not assume nodes occupy adjacent addresses.",
        ),
        E(
            "Handle an empty list",
            "Measure and destroy a null head.",
            "Length is zero and head stays NULL.",
            r"""struct Node *head=NULL;CHECK(list_length(head)==0);destroy_list(&head);CHECK(head==NULL);""",
            "An empty structure should have natural operations without a fabricated sentinel payload.",
        ),
        E(
            "Reverse without reallocating",
            "Build 3, 2, 1 and reverse it.",
            "The order becomes 1, 2, 3.",
            r"""struct Node *head=NULL;CHECK(push_front(&head,1)&&push_front(&head,2)&&push_front(&head,3));reverse_list(&head);CHECK(head->value==1&&head->next->value==2&&head->next->next->value==3);destroy_list(&head);""",
            "Saving next before rewiring preserves access to the unprocessed suffix.",
        ),
        E(
            "Reverse a singleton",
            "Reverse a one-node list.",
            "Its value and terminating link are preserved.",
            r"""struct Node *head=NULL;CHECK(push_front(&head,7));reverse_list(&head);CHECK(head->value==7&&head->next==NULL);destroy_list(&head);""",
            "The smallest nonempty structure checks the initial and final link conditions.",
        ),
        E(
            "Transfer double-reversal reasoning",
            "Reverse a two-node list twice.",
            "Its original order is restored.",
            r"""struct Node *head=NULL;CHECK(push_front(&head,1)&&push_front(&head,2));reverse_list(&head);reverse_list(&head);CHECK(head->value==2&&head->next->value==1);destroy_list(&head);""",
            "This involution property complements exact order tests. It alone would not reject a no-op implementation, so keep both forms of evidence.",
        ),
    ],
    helper="""struct Node{int value;struct Node *next;};
static bool push_front(struct Node **head,int value){struct Node *node=malloc(sizeof *node);if(node==NULL)return false;node->value=value;node->next=*head;*head=node;return true;}
static size_t list_length(const struct Node *head){size_t n=0;for(const struct Node *p=head;p!=NULL;p=p->next)n++;return n;}
static void destroy_list(struct Node **head){struct Node *p=*head;while(p!=NULL){struct Node *next=p->next;free(p);p=next;}*head=NULL;}
static void reverse_list(struct Node **head){struct Node *previous=NULL,*current=*head;while(current!=NULL){struct Node *next=current->next;current->next=previous;previous=current;current=next;}*head=previous;}""",
)

add(
    "Stacks, queues and ring-buffer invariants",
    """A stack removes the most recently inserted value; a queue removes the earliest. The same array storage can support different behavioral contracts. A bounded ring buffer reuses positions by wrapping indices modulo capacity. Keep occupancy separate from index values so full and empty are not confused when head equals tail. Every enqueue must prove spare capacity before writing, and every dequeue must prove nonempty state before reading. Fixed capacity makes resource use predictable and overflow behavior explicit. A concurrent queue requires additional synchronization; the sequential ring here is not automatically safe to share across threads.""",
    """The queue stores head and count. The next insertion index is (head+count)%capacity, and removal advances head modulo capacity. count ranges from zero through capacity. Returning bool plus an output pointer preserves the distinction between an empty queue and a legitimate zero-valued item. Rejected operations leave both structure and output unchanged.""",
    [
        ("FIFO", "First in, first out removal order."),
        ("LIFO", "Last in, first out removal order."),
        ("Ring buffer", "Fixed storage reused through wrapped indices."),
    ],
    [
        E(
            "Preserve FIFO order",
            "Enqueue 2 then 5 and dequeue twice.",
            "The values arrive as 2 then 5.",
            r"""struct Queue q={0};int out=0;CHECK(enqueue(&q,2)&&enqueue(&q,5));CHECK(dequeue(&q,&out)&&out==2);CHECK(dequeue(&q,&out)&&out==5);""",
            "The queue contract differs from a stack, which would return 5 first.",
        ),
        E(
            "Reject an empty read",
            "Dequeue from a new queue with output 9.",
            "The operation fails and output stays 9.",
            r"""struct Queue q={0};int out=9;CHECK(!dequeue(&q,&out)&&out==9&&q.count==0);""",
            "No element is read before the occupancy check. Zero cannot be used as an empty sentinel because zero may be a real item.",
        ),
        E(
            "Reject a full write",
            "Fill four slots and attempt a fifth insertion.",
            "The fifth fails and occupancy stays four.",
            r"""struct Queue q={0};for(int i=0;i<4;i++)CHECK(enqueue(&q,i));CHECK(!enqueue(&q,99)&&q.count==4);""",
            "A bounded container must state whether full means reject, overwrite or block. This one rejects without data loss.",
        ),
        E(
            "Wrap reused storage",
            "Fill, remove two values, then add two more.",
            "Remaining order is 2, 3, 4, 5.",
            r"""struct Queue q={0};int out=0;for(int i=0;i<4;i++)CHECK(enqueue(&q,i));CHECK(dequeue(&q,&out)&&dequeue(&q,&out));CHECK(enqueue(&q,4)&&enqueue(&q,5));for(int i=2;i<6;i++){CHECK(dequeue(&q,&out)&&out==i);}""",
            "Wrapped physical positions still implement one logical FIFO sequence.",
        ),
        E(
            "Retain a real zero",
            "Enqueue zero and then read it.",
            "The read succeeds with output zero.",
            r"""struct Queue q={0};int out=9;CHECK(enqueue(&q,0)&&dequeue(&q,&out)&&out==0);""",
            "Status and payload are separate channels, so an ordinary zero does not look like failure.",
        ),
        E(
            "Transfer stack contrast",
            "Push 2 and 5 into a bounded stack and pop once.",
            "The popped value is 5.",
            r"""int stack[4];size_t length=0;stack[length++]=2;stack[length++]=5;int out=stack[--length];CHECK(out==5&&length==1);""",
            "The pop index is the last occupied position. This direct fixture proves nonempty state before decrementing.",
        ),
    ],
    helper="""enum{QUEUE_CAPACITY=4};
struct Queue{int data[QUEUE_CAPACITY];size_t head,count;};
static bool enqueue(struct Queue *q,int value){if(q->count==QUEUE_CAPACITY)return false;size_t index=(q->head+q->count)%QUEUE_CAPACITY;q->data[index]=value;q->count++;return true;}
static bool dequeue(struct Queue *q,int *out){if(q->count==0||out==NULL)return false;*out=q->data[q->head];q->head=(q->head+1)%QUEUE_CAPACITY;q->count--;return true;}""",
)

add(
    "Hash tables, collisions and explicit occupancy",
    """A hash table maps a key to a candidate storage position. Different keys can collide, so a hash value is not proof of key equality. Open addressing resolves collisions by probing alternative slots under a bounded policy. Each slot needs occupancy information separate from its stored key and value, because zero may be a legitimate key or value. Deletion in an open-addressed table requires care: clearing a slot can break the search chain for later colliding entries. This small fixed table supports insertion, replacement and lookup, and deliberately does not pretend that naive clearing implements deletion.""",
    """The fixture uses unsigned integer keys and linear probing across eight slots. Every probe checks used and then compares the actual key. A probe loop has a capacity bound so a full table cannot cause an infinite search. Inserting an existing key replaces its value without consuming another slot. Production designs choose a load factor, resizing policy, hash function and collision-resistance requirements from their input threat model.""",
    [
        ("Collision", "Different keys selecting the same initial hash position."),
        ("Probe sequence", "The ordered candidate positions searched after a collision."),
        ("Load factor", "The fraction of table capacity occupied by entries."),
    ],
    [
        E(
            "Insert and retrieve",
            "Store key 1 with value 7.",
            "Lookup succeeds with 7.",
            r"""struct Table t={0};int out=0;CHECK(table_put(&t,1,7)&&table_get(&t,1,&out)&&out==7);""",
            "Lookup checks the actual key rather than trusting the initial slot alone.",
        ),
        E(
            "Resolve a collision",
            "Insert keys 1 and 9, which share the initial slot.",
            "Both values remain retrievable.",
            r"""struct Table t={0};int out=0;CHECK(table_put(&t,1,10)&&table_put(&t,9,90));CHECK(table_get(&t,1,&out)&&out==10);CHECK(table_get(&t,9,&out)&&out==90);""",
            "Linear probing finds another free slot while preserving the key distinction.",
        ),
        E(
            "Replace an existing key",
            "Write key 2 twice with different values.",
            "The latest value is 8.",
            r"""struct Table t={0};int out=0;CHECK(table_put(&t,2,3)&&table_put(&t,2,8));CHECK(table_get(&t,2,&out)&&out==8);""",
            "Replacement does not create duplicate logical keys.",
        ),
        E(
            "Distinguish absent from zero",
            "Store key zero with value zero and query a missing key.",
            "The stored zero succeeds; the missing key fails.",
            r"""struct Table t={0};int out=9;CHECK(table_put(&t,0,0)&&table_get(&t,0,&out)&&out==0);out=9;CHECK(!table_get(&t,3,&out)&&out==9);""",
            "Occupancy and return status preserve information that a zero sentinel would lose.",
        ),
        E(
            "Reject a full-table insertion",
            "Fill all eight slots and insert a new ninth key.",
            "The operation returns false without looping forever.",
            r"""struct Table t={0};for(unsigned i=0;i<8;i++)CHECK(table_put(&t,i,(int)i));CHECK(!table_put(&t,99,99));""",
            "Every probe sequence is bounded by capacity. A resizing implementation would allocate before changing the old table.",
        ),
        E(
            "Transfer replacement while full",
            "Replace an existing key after filling the table.",
            "Replacement still succeeds.",
            r"""struct Table t={0};for(unsigned i=0;i<8;i++)CHECK(table_put(&t,i,(int)i));int out=0;CHECK(table_put(&t,3,30)&&table_get(&t,3,&out)&&out==30);""",
            "Full storage prevents new keys, not an update to an already present key. This is a distinct edge condition.",
        ),
    ],
    helper="""enum{TABLE_CAPACITY=8};
struct Entry{bool used;unsigned key;int value;};
struct Table{struct Entry entries[TABLE_CAPACITY];};
static bool table_put(struct Table *t,unsigned key,int value){for(size_t step=0;step<TABLE_CAPACITY;step++){size_t i=(key%TABLE_CAPACITY+step)%TABLE_CAPACITY;struct Entry *e=&t->entries[i];if(!e->used||e->key==key){e->used=true;e->key=key;e->value=value;return true;}}return false;}
static bool table_get(const struct Table *t,unsigned key,int *out){for(size_t step=0;step<TABLE_CAPACITY;step++){size_t i=(key%TABLE_CAPACITY+step)%TABLE_CAPACITY;const struct Entry *e=&t->entries[i];if(!e->used)return false;if(e->key==key){*out=e->value;return true;}}return false;}""",
)

add(
    "Sorting, binary search and complexity evidence",
    """An algorithm contract includes input assumptions and output meaning. Binary search requires sorted data and a comparison relation consistent with that ordering. A lower-bound search returns the first position whose value is at least a target, including an insertion position when no element matches. Using a half-open interval makes empty input and one-past results natural. Midpoint arithmetic should avoid overflowing low+high. Complexity explains growth in operations, while runtime performance depends on constants, memory access and input distribution. Preserve exact boundary tests when optimizing rather than trusting a faster-looking implementation.""",
    """Maintain an interval [low, high) containing the answer. Compute middle as low+(high-low)/2. If values[middle] is below the target, advance low to middle+1; otherwise set high to middle. The interval strictly shrinks until both bounds meet. Never dereference the returned index before checking it is below length. Sorting and deduplication are different operations.""",
    [
        ("Lower bound", "The first index whose value is not less than a target."),
        ("Search invariant", "A statement preserving where the answer can lie."),
        ("Asymptotic growth", "How required work changes as input grows."),
    ],
    [
        E(
            "Find an interior boundary",
            "Search 2, 4, 6, 8 for target 5.",
            "The lower-bound index is 2.",
            r"""int values[]={2,4,6,8};CHECK(lower_bound(values,4,5)==2);""",
            "The result is an insertion position, not a claim that 5 exists.",
        ),
        E(
            "Find the first duplicate",
            "Search 1, 3, 3, 5 for target 3.",
            "The index is the first 3 at position 1.",
            r"""int values[]={1,3,3,5};CHECK(lower_bound(values,4,3)==1);""",
            "The high=middle branch keeps earlier equal values in the candidate interval.",
        ),
        E(
            "Handle no larger value",
            "Search 2, 4, 6 for target 9.",
            "The result is length 3.",
            r"""int values[]={2,4,6};CHECK(lower_bound(values,3,9)==3);""",
            "The returned one-past index must not be dereferenced.",
        ),
        E(
            "Handle empty input",
            "Search an empty logical view.",
            "The insertion index is zero.",
            r"""CHECK(lower_bound(NULL,0,7)==0);""",
            "The loop performs no access because low already equals high.",
        ),
        E(
            "Check the first boundary",
            "Search 2, 4, 6 for target 1.",
            "The index is zero.",
            r"""int values[]={2,4,6};CHECK(lower_bound(values,3,1)==0);""",
            "The answer can be before the first stored value without requiring a negative index.",
        ),
        E(
            "Transfer an exact membership check",
            "Use lower bound and then equality to test whether 4 is present.",
            "The guarded membership test succeeds.",
            r"""int values[]={2,4,6};size_t i=lower_bound(values,3,4);CHECK(i<3&&values[i]==4);""",
            "Membership requires both an in-range result and equality. A lower-bound index by itself is not proof of presence.",
        ),
    ],
    helper="static size_t lower_bound(const int *values,size_t n,int target){size_t low=0,high=n;while(low<high){size_t middle=low+(high-low)/2;if(values[middle]<target)low=middle+1;else high=middle;}return low;}",
)

add(
    "Recursion, trees and depth budgets",
    """Recursion solves a problem by invoking the same mechanism on smaller subproblems. A base case stops the process, and a progress measure explains why each step approaches it. A binary tree naturally decomposes into a root and subtrees, but an unbalanced tree can have depth proportional to its node count. Recursive traversal therefore consumes stack space according to depth, not just total work. For untrusted or very large structures, impose a depth budget or use an explicit stack. This lesson uses fixed stack-allocated nodes with no cycles and no ownership ambiguity, separating traversal reasoning from allocation mechanics.""",
    """A node stores value, left and right pointers. NULL represents an empty subtree. A sum traversal combines the root value with both subtree sums. A depth function returns zero for empty and one plus the greater child depth otherwise. The bounded search checks its remaining depth before descending. General graph traversal also needs visited-state handling because a cycle is not a valid finite tree.""",
    [
        ("Base case", "The condition ending recursive descent."),
        ("Progress measure", "A quantity that decreases toward termination."),
        ("Depth budget", "A bound on nested traversal steps."),
    ],
    [
        E(
            "Traverse a small tree",
            "Sum a root 2 with children 1 and 3.",
            "The total is 6.",
            r"""struct Tree left={1,NULL,NULL},right={3,NULL,NULL},root={2,&left,&right};CHECK(tree_sum(&root)==6);""",
            "Each node contributes once under the acyclic tree assumption.",
        ),
        E(
            "Handle an empty tree",
            "Sum NULL.",
            "The result is zero.",
            r"""CHECK(tree_sum(NULL)==0);""",
            "The empty subtree contributes the additive identity and ends recursion.",
        ),
        E(
            "Measure structural depth",
            "Measure the root and two children.",
            "The depth is 2.",
            r"""struct Tree left={1,NULL,NULL},right={3,NULL,NULL},root={2,&left,&right};CHECK(tree_depth(&root)==2);""",
            "Depth counts nested levels, not the three total nodes.",
        ),
        E(
            "Find an existing value",
            "Search the tree for 3 with sufficient budget.",
            "The value is found.",
            r"""struct Tree leaf={3,NULL,NULL},root={2,NULL,&leaf};CHECK(tree_contains(&root,3,2));""",
            "The budget permits visiting root and child. Each recursive call decreases the remaining allowance.",
        ),
        E(
            "Respect a depth limit",
            "Search for the child value with only one level allowed.",
            "The bounded search does not descend to the child.",
            r"""struct Tree leaf={3,NULL,NULL},root={2,NULL,&leaf};CHECK(!tree_contains(&root,3,1));""",
            "This bool API conflates not-found-within-budget and absent. A production diagnostic API should return a distinct budget-exhausted status when that distinction matters.",
        ),
        E(
            "Transfer a singleton",
            "Measure and sum one node containing 7.",
            "Depth is 1 and sum is 7.",
            r"""struct Tree root={7,NULL,NULL};CHECK(tree_depth(&root)==1&&tree_sum(&root)==7);""",
            "The singleton verifies that both empty-child base cases combine correctly.",
        ),
    ],
    helper="""struct Tree{int value;const struct Tree *left,*right;};
static int tree_sum(const struct Tree *node){if(node==NULL)return 0;return node->value+tree_sum(node->left)+tree_sum(node->right);}
static size_t tree_depth(const struct Tree *node){if(node==NULL)return 0;size_t a=tree_depth(node->left),b=tree_depth(node->right);return 1+(a>b?a:b);}
static bool tree_contains(const struct Tree *node,int target,size_t budget){if(node==NULL||budget==0)return false;if(node->value==target)return true;return tree_contains(node->left,target,budget-1)||tree_contains(node->right,target,budget-1);}""",
)

add(
    "Bounded string builders and failure-atomic appends",
    """Building text incrementally requires an invariant connecting length, capacity and termination. A valid builder keeps length below capacity and stores a null character at data[length]. An append must prove enough remaining space for both payload and terminator before copying. Failure should preserve the existing valid string rather than leave a half-written result that looks complete. Avoid repeated strcat scans when the current length is already known. This fixed-capacity builder makes the resource budget visible and rejects overflow; a dynamic builder would additionally need allocation failure and pointer-invalidation policies.""",
    """The builder owns a fixed character array and a length. append_text obtains the source length, checks it against capacity-1-length, then copies payload plus terminator with memcpy. The subtraction form avoids overflowing length+incoming+1. Source and destination must not overlap for this helper. Initial zero state is a valid empty string, which makes construction and cleanup simple.""",
    [
        ("Builder invariant", "The relationship between stored length, capacity and terminator."),
        ("Failure-atomic append", "An append that leaves the prior string unchanged on rejection."),
        ("Overlap contract", "Whether input and output memory ranges may share bytes."),
    ],
    [
        E(
            "Append two fragments",
            "Append red then space sky.",
            "The result is red sky with length 7.",
            r"""struct Builder b={0};CHECK(append_text(&b,"red")&&append_text(&b," sky"));CHECK(b.len==7&&strcmp(b.data,"red sky")==0);""",
            "The stored length avoids rescanning previous content before every append.",
        ),
        E(
            "Append empty text",
            "Append an empty fragment to abc.",
            "Length and content remain unchanged.",
            r"""struct Builder b={0};CHECK(append_text(&b,"abc")&&append_text(&b,""));CHECK(b.len==3&&strcmp(b.data,"abc")==0);""",
            "The empty append is a successful no-op, not an error or a new terminator-free state.",
        ),
        E(
            "Fill to exact payload capacity",
            "Append fifteen characters to capacity sixteen.",
            "The complete payload fits and remains terminated.",
            r"""struct Builder b={0};CHECK(append_text(&b,"123456789012345"));CHECK(b.len==15&&b.data[15]=='\0');""",
            "The final storage byte belongs to the terminator. Payload capacity is one less than total capacity.",
        ),
        E(
            "Reject one extra character",
            "Fill the builder then append x.",
            "The append fails without changing prior content.",
            r"""struct Builder b={0};CHECK(append_text(&b,"123456789012345"));CHECK(!append_text(&b,"x"));CHECK(b.len==15&&strcmp(b.data,"123456789012345")==0);""",
            "The bound is checked before copying, preserving a valid complete previous result.",
        ),
        E(
            "Reject an oversized first fragment",
            "Try a fragment longer than payload capacity.",
            "The builder remains an empty valid string.",
            r"""struct Builder b={0};CHECK(!append_text(&b,"1234567890123456"));CHECK(b.len==0&&b.data[0]=='\0');""",
            "A failed first append should not leave a misleading truncated result.",
        ),
        E(
            "Transfer a delimiter protocol",
            "Build a,b,c with explicit separators.",
            "The exact result is a,b,c.",
            r"""struct Builder b={0};CHECK(append_text(&b,"a")&&append_text(&b,",")&&append_text(&b,"b")&&append_text(&b,",")&&append_text(&b,"c"));CHECK(strcmp(b.data,"a,b,c")==0);""",
            "This is a fixed synthetic delimiter example. General CSV output needs quoting rules, not simple separator insertion.",
        ),
    ],
    helper="""struct Builder{char data[16];size_t len;};
static bool append_text(struct Builder *b,const char *source){size_t incoming=strlen(source);if(b->len>=sizeof b->data||incoming>sizeof b->data-1-b->len)return false;memcpy(b->data+b->len,source,incoming+1);b->len+=incoming;return true;}""",
)

add(
    "Testing, injected allocation failure and useful oracles",
    """Reliable tests target plausible defects rather than mirror the implementation line for line. A normal result, an exact boundary, malformed input and resource failure often exercise different contracts. Allocation failure is difficult to reproduce by exhausting real machine memory and should not be forced on a shared system. Inject a controlled allocator interface instead. The fake can fail on a selected call while recording ownership counts, making cleanup behavior deterministic. Such a fake proves local error-path logic, not the operating system allocator or every interleaving. Keep sanitizer and real integration evidence separate.""",
    """A function pointer supplies allocation behavior. The fixture allocator either delegates to malloc or returns NULL according to an explicit flag. The component validates and allocates before modifying the caller output pointer. Tests retain the previous output on failure. A useful oracle checks both the returned status and absence of unintended state changes; a nonzero exit alone cannot explain which invariant was violated.""",
    [
        (
            "Fault injection",
            "Deliberately supplying a particular failure under controlled conditions.",
        ),
        ("Test oracle", "An independent rule defining the correct outcome."),
        (
            "Failure-path coverage",
            "Evidence that cleanup and state preservation work when an operation fails.",
        ),
    ],
    [
        E(
            "Exercise successful allocation",
            "Copy a tiny string using the working allocator.",
            "The output owns an equal string.",
            r"""char *out=NULL;fail_allocation=false;CHECK(copy_with_allocator("abc",&out,controlled_alloc));CHECK(strcmp(out,"abc")==0);free(out);""",
            "The test checks content and then releases the owned result.",
        ),
        E(
            "Inject allocation failure",
            "Configure the allocator to return NULL.",
            "The copy fails and output remains NULL.",
            r"""char *out=NULL;fail_allocation=true;CHECK(!copy_with_allocator("abc",&out,controlled_alloc));CHECK(out==NULL);fail_allocation=false;""",
            "No real memory pressure is required. The failure is reproducible and isolated to this operation.",
        ),
        E(
            "Preserve an existing output pointer",
            "Fail allocation while output points to a separate valid buffer.",
            "The output pointer remains unchanged.",
            r"""char existing[]="old";char *out=existing;fail_allocation=true;CHECK(!copy_with_allocator("new",&out,controlled_alloc));CHECK(out==existing&&strcmp(out,"old")==0);fail_allocation=false;""",
            "The component does not erase caller state before it knows it can return a successful replacement.",
        ),
        E(
            "Test an empty valid input",
            "Copy empty text through the working allocator.",
            "A valid empty owned string is returned.",
            r"""char *out=NULL;CHECK(copy_with_allocator("",&out,controlled_alloc));CHECK(out!=NULL&&out[0]=='\0');free(out);""",
            "The allocation includes the terminator even when payload length is zero.",
        ),
        E(
            "Retain a normal case after failure",
            "Run one failing call followed by a successful call.",
            "The later call succeeds independently.",
            r"""char *out=NULL;fail_allocation=true;CHECK(!copy_with_allocator("x",&out,controlled_alloc));fail_allocation=false;CHECK(copy_with_allocator("x",&out,controlled_alloc));CHECK(strcmp(out,"x")==0);free(out);""",
            "Failure must not leave hidden component state that poisons the next invocation.",
        ),
        E(
            "Transfer a distinguishing content check",
            "Copy case-sensitive text and compare exact content.",
            "Red remains different from red.",
            r"""char *out=NULL;CHECK(copy_with_allocator("Red",&out,controlled_alloc));CHECK(strcmp(out,"Red")==0&&strcmp(out,"red")!=0);free(out);""",
            "A weak length-only check would accept the wrong letters. Choose an oracle strong enough to reject the relevant defect.",
        ),
    ],
    helper="""static bool fail_allocation=false;
static void *controlled_alloc(size_t size){return fail_allocation?NULL:malloc(size);}
static bool copy_with_allocator(const char *source,char **out,void *(*allocate)(size_t)){size_t n=strlen(source);if(n==SIZE_MAX)return false;char *copy=allocate(n+1);if(copy==NULL)return false;memcpy(copy,source,n+1);*out=copy;return true;}""",
)

add(
    "Headers, translation units and reproducible builds",
    """A multi-file C project separates declarations in headers from definitions in source files. Each source file is compiled independently, so a header is the shared contract the compiler uses at every call site. The linker later resolves external definitions. Defining a non-static global function in a header included by several files can create duplicate definitions. Omitting a required source object can create an unresolved symbol. Include guards prevent repeated declarations inside one translation unit, but do not fix incorrect cross-file ownership. A reproducible build records compiler mode, warnings, source dependencies and link libraries explicitly.""",
    """A header declares a function prototype under an include guard. One .c file defines that function, and a caller includes the header. Compile each source with -c to produce an object, then link the objects into one executable. Put libraries after the objects that reference them when the linker requires left-to-right resolution. The browser pad remains one main.c; the separate fixture demonstrates actual headers, source files, tests and a Makefile.""",
    [
        ("Declaration", "A statement describing a name and its type."),
        ("Definition", "The source that provides an object or function implementation."),
        ("Linkage", "The rules connecting declarations of the same entity across scopes or files."),
    ],
    [
        E(
            "Call a declared API",
            "Use the stats_sum prototype before its definition.",
            "Summing 2, 4, 6 returns 12.",
            r"""int values[]={2,4,6};CHECK(stats_sum(values,3)==12);""",
            "A compatible declaration lets the compiler validate the call independently of where the definition appears.",
        ),
        E(
            "Use an empty API contract",
            "Sum a zero-length view.",
            "The result is zero.",
            r"""CHECK(stats_sum(NULL,0)==0);""",
            "The interface explicitly permits this empty case and the implementation makes no pointer access.",
        ),
        E(
            "Compare two callers",
            "Call the same helper with two separate arrays.",
            "The results are 3 and 7.",
            r"""int a[]={1,2},b[]={3,4};CHECK(stats_sum(a,2)==3&&stats_sum(b,2)==7);""",
            "Reusable code should not depend on one caller-owned array or hidden previous state.",
        ),
        E(
            "Retain caller data",
            "Sum an array and inspect its elements afterward.",
            "The input remains unchanged.",
            r"""int values[]={2,4};(void)stats_sum(values,2);CHECK(values[0]==2&&values[1]==4);""",
            "The const-qualified input contract communicates read-only access through the API.",
        ),
        E(
            "Check a one-element boundary",
            "Sum one negative value.",
            "The result is -3.",
            r"""int values[]={-3};CHECK(stats_sum(values,1)==-3);""",
            "The API handles its stated signed data range; this small fixture avoids overflow.",
        ),
        E(
            "Transfer repeatable builds to repeatable behavior",
            "Call the pure helper twice on the same input.",
            "Both results equal 6.",
            r"""int values[]={1,2,3};int first=stats_sum(values,3),second=stats_sum(values,3);CHECK(first==6&&second==6);""",
            "Stable input and a pure function produce stable behavior. Reproducible binary bytes additionally depend on compiler and build-environment controls.",
        ),
    ],
    helper="""static int stats_sum(const int *values,size_t length);
static int stats_sum(const int *values,size_t length){int sum=0;for(size_t i=0;i<length;i++)sum+=values[i];return sum;}""",
    source="https://gcc.gnu.org/onlinedocs/gcc/Overall-Options.html",
    boundary="The real multi-file example is in courses/c/fixtures/stats-project/. It is a separately prepared contributor project with a header, implementation, executable and tests. The ordinary pad reference demonstrates the API contract in one file and does not claim that the pad accepts project archives or custom build scripts.",
)
