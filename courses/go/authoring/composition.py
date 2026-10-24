"""I/O, services and concurrency with deterministic, offline evidence."""

from render import add
from render import case as E

add(
    "Readers, writers and bounded streaming",
    """io.Reader and io.Writer describe data movement independently of where bytes are stored. A reader can return some bytes and an error together; process the bytes before deciding whether the error ends the stream. One Read call is not guaranteed to fill a buffer. io.ReadFull expresses a different contract: obtain exactly the requested length or report why that was impossible. Streaming avoids loading an entire input into memory, but it is only bounded when the caller limits input, buffering and output. A limit reached is not automatically valid end-of-document evidence. Keep transport completion separate from format validation.""",
    """Read receives a byte slice and returns n and err. Only the first n bytes contain this call's data. io.EOF means the stream has ended; io.ErrUnexpectedEOF means a fixed-size request ended after partial data. io.Copy repeatedly transfers data and returns a count plus error. io.LimitReader caps visible bytes. bytes.Buffer provides an in-memory reader/writer useful for deterministic tests.""",
    [
        ("Reader", "An interface supplying bytes incrementally."),
        ("Short read", "A successful read returning fewer bytes than requested."),
        ("Input budget", "The maximum amount of input an operation permits."),
    ],
    [
        E(
            "Copy a stream",
            "Copy alpha from a strings.Reader into bytes.Buffer.",
            "Five bytes are copied and output is alpha.",
            r"""var out bytes.Buffer; n,err:=io.Copy(&out,strings.NewReader("alpha")); check(err==nil&&n==5&&out.String()=="alpha","copy")""",
            "The consumer depends on Reader and Writer behavior rather than a particular file or socket implementation.",
        ),
        E(
            "Require a full record",
            "Read exactly four bytes from a two-byte source.",
            "Two bytes arrive and ErrUnexpectedEOF is returned.",
            r"""buf:=make([]byte,4); n,err:=io.ReadFull(strings.NewReader("ab"),buf); check(n==2&&err==io.ErrUnexpectedEOF,"partial record")""",
            "Partial data is useful evidence, but it is not a complete fixed-width record. Treating any positive n as completion would accept truncation.",
        ),
        E(
            "Bound visible input",
            "Read at most three bytes from abcdef.",
            "The visible result is abc.",
            r"""v,err:=io.ReadAll(io.LimitReader(strings.NewReader("abcdef"),3));check(err==nil&&string(v)=="abc","limit")""",
            "The limit controls resource use. It does not establish that the original source had only three bytes, so a format checker may need one extra byte to detect excess input.",
        ),
        E(
            "Detect excess data",
            "Read a four-byte budget for a three-byte maximum.",
            "A four-byte result proves the maximum was exceeded.",
            r"""v,err:=io.ReadAll(io.LimitReader(strings.NewReader("abcd"),4));check(err==nil&&len(v)>3,"excess input")""",
            "Reading maximum plus one distinguishes exactly-at-limit data from truncated over-limit input without unbounded allocation.",
        ),
        E(
            "Preserve an empty stream",
            "Copy an empty reader to a buffer.",
            "The count is zero and there is no error.",
            r"""var out bytes.Buffer;n,err:=io.Copy(&out,strings.NewReader(""));check(err==nil&&n==0&&out.Len()==0,"empty copy")""",
            "An empty stream can be valid transport input even when an application later requires at least one record.",
        ),
        E(
            "Transfer exact framing",
            "Read a two-byte header followed by a three-byte payload.",
            "The header is AB and payload is xyz.",
            r"""r:=strings.NewReader("ABxyz");h:=make([]byte,2);p:=make([]byte,3);_,e1:=io.ReadFull(r,h);_,e2:=io.ReadFull(r,p);check(e1==nil&&e2==nil&&string(h)=="AB"&&string(p)=="xyz","framing")""",
            "Explicit frame lengths prevent a reader from guessing where one logical object ends. Real formats also validate lengths before allocating.",
        ),
    ],
    imports="io strings bytes",
    source="https://pkg.go.dev/io",
)

add(
    "Filesystems, paths and owned cleanup",
    """A filesystem path is a name interpreted by a filesystem, not proof of ownership or permission. Logical path cleaning removes redundant components but does not prevent symlink escapes or authorize deletion. The io/fs interfaces let programs consume files without depending on a particular disk layout. A deterministic in-memory filesystem makes success, missing-file and malformed-path behavior easy to inspect. When real temporary files are needed, create a unique owned directory, defer its cleanup and never infer ownership from a familiar filename. Persistent learner work belongs in the classroom storage layer; a worker scratch file is temporary and should not be treated as saved progress.""",
    """fs.ReadFile accepts an fs.FS and a slash-separated relative path. fs.ValidPath rejects empty paths, leading slashes and dot-dot components under the logical contract. fstest.MapFS provides test files in memory. errors.Is(err, fs.ErrNotExist) detects a missing-file cause across wrapping. filepath.Clean alone is normalization, not a containment security boundary.""",
    [
        ("Filesystem interface", "An abstraction for relative file operations."),
        ("Path confinement", "Restricting access to an explicitly allowed tree."),
        ("Owned resource", "A resource whose creation and cleanup responsibility are known."),
    ],
    [
        E(
            "Read an in-memory file",
            "Read data/input.txt containing red and a newline.",
            "The bytes decode to red followed by a newline.",
            r"""files:=fstest.MapFS{"data/input.txt":&fstest.MapFile{Data:[]byte("red\n")}};v,err:=fs.ReadFile(files,"data/input.txt");check(err==nil&&string(v)=="red\n","file read")""",
            "The algorithm uses the same filesystem interface without reaching the host disk. That isolates content behavior from permissions and mount configuration.",
        ),
        E(
            "Observe a missing file",
            "Read absent.txt from an empty filesystem.",
            "The error matches fs.ErrNotExist.",
            r"""_,err:=fs.ReadFile(fstest.MapFS{},"absent.txt");check(errors.Is(err,fs.ErrNotExist),"missing file")""",
            "Preserving a typed cause lets a caller distinguish optional absence from unreadable or malformed content.",
        ),
        E(
            "Reject traversal syntax",
            "Validate ../private and data/input.txt.",
            "The traversal path is invalid and the relative data path is valid.",
            r"""check(!fs.ValidPath("../private")&&fs.ValidPath("data/input.txt"),"relative paths")""",
            "This validates the logical naming grammar. Real disk confinement still needs a filesystem API that safely handles symlinks and concurrent changes.",
        ),
        E(
            "Walk only owned entries",
            "Walk a two-file in-memory tree and count regular files.",
            "Exactly two files are observed.",
            r"""files:=fstest.MapFS{"a.txt":&fstest.MapFile{},"sub/b.txt":&fstest.MapFile{}};count:=0;err:=fs.WalkDir(files,".",func(p string,d fs.DirEntry,e error)error{if e!=nil{return e};if !d.IsDir(){count++};return nil});check(err==nil&&count==2,"walk")""",
            "The callback must handle the supplied error before dereferencing the entry. Traversal order should not become an accidental business rule.",
        ),
        E(
            "Separate empty content from absence",
            "Read an existing zero-byte file.",
            "Reading succeeds and returns zero bytes.",
            r"""v,err:=fs.ReadFile(fstest.MapFS{"empty":&fstest.MapFile{}},"empty");check(err==nil&&len(v)==0,"empty file")""",
            "An empty file and a missing file are different states. Collapsing both into an empty string loses evidence needed for diagnosis.",
        ),
        E(
            "Transfer a subtree boundary",
            "Create an fs.Sub rooted at data and read only its relative item.",
            "item.txt is readable within the logical subtree.",
            r"""files:=fstest.MapFS{"data/item.txt":&fstest.MapFile{Data:[]byte("7")}};sub,err:=fs.Sub(files,"data");check(err==nil,"sub root");v,err:=fs.ReadFile(sub,"item.txt");check(err==nil&&string(v)=="7","sub read")""",
            "A subtree abstraction simplifies names for a consumer. Its security properties depend on the underlying filesystem implementation, so do not equate every fs.Sub with a hardened sandbox.",
        ),
    ],
    imports="io/fs testing/fstest errors",
    source="https://pkg.go.dev/io/fs",
)

add(
    "JSON schemas, strict decoding and unknown input",
    """JSON is a serialization format, not a complete application schema. A syntactically valid object can still contain unknown fields, missing required values, invalid ranges or extra documents after the first value. Go struct tags define field names and omission rules. The decoder normally tolerates unknown fields, so strict APIs must request a stricter policy. Numeric JSON values decoded into any become floating values unless the decoder uses json.Number; large integers can lose precision. Decode transport syntax, validate domain meaning and reject trailing data as separate steps. Do not use the same structure blindly for external input, internal state and public output.""",
    """json:"name" maps a field to its wire name. json.Marshal returns bytes and an error. Decoder.DisallowUnknownFields rejects fields missing from a target struct. A second Decode should return io.EOF when exactly one JSON value is required. omitempty omits zero-like fields during encoding; it does not validate mandatory fields. Use pointers or explicit presence types when absent and zero differ.""",
    [
        ("Wire schema", "The fields and types accepted at a serialized boundary."),
        ("Unknown field", "A supplied property absent from the target structure."),
        ("Trailing value", "Additional serialized data after an expected document."),
    ],
    [
        E(
            "Decode a typed object",
            "Decode a name and count into Config.",
            "The fields become sample and 3.",
            r"""var c Config;err:=json.Unmarshal([]byte(`{"name":"sample","count":3}`),&c);check(err==nil&&c.Name=="sample"&&c.Count==3,"typed JSON")""",
            "Field names follow tags rather than an accidental presentation format. Parsing success still leaves count-range and name rules to domain validation.",
        ),
        E(
            "Reject an unknown property",
            "Use a strict decoder on an object with an unexpected extra field.",
            "Decoding returns an error.",
            r"""var c Config;d:=json.NewDecoder(strings.NewReader(`{"name":"x","extra":1}`));d.DisallowUnknownFields();check(d.Decode(&c)!=nil,"unknown field")""",
            "Strict rejection catches misspelled configuration keys instead of silently ignoring a learner or operator mistake.",
        ),
        E(
            "Detect a second document",
            "Decode two adjacent JSON objects and check whether another value exists.",
            "A second value is observable, so the single-document contract fails.",
            r"""d:=json.NewDecoder(strings.NewReader(`{} {}`));var a,b any;check(d.Decode(&a)==nil&&d.Decode(&b)==nil,"trailing document")""",
            "One successful Decode consumes one value. It does not prove the entire input contains only that value.",
        ),
        E(
            "Confirm exact completion",
            "Decode one object, then require EOF.",
            "The second decode returns io.EOF.",
            r"""d:=json.NewDecoder(strings.NewReader(`{"name":"x"}`));var c Config;check(d.Decode(&c)==nil,"first decode");var extra any;check(d.Decode(&extra)==io.EOF,"exact end")""",
            "The second read establishes the single-document boundary. Whitespace after the object is allowed by the decoder.",
        ),
        E(
            "Preserve a large integer token",
            "Use UseNumber while decoding 9007199254740993 into any.",
            "The exact decimal token is retained.",
            r"""d:=json.NewDecoder(strings.NewReader(`9007199254740993`));d.UseNumber();var v any;check(d.Decode(&v)==nil&&v.(json.Number).String()=="9007199254740993","number token")""",
            "Keeping the token avoids an early float64 conversion. The application still needs to choose a numeric range and handle conversion errors.",
        ),
        E(
            "Transfer domain validation",
            "Decode a negative count successfully, then reject it as a domain error.",
            "JSON syntax is valid but count validation fails.",
            r"""var c Config;err:=json.Unmarshal([]byte(`{"name":"x","count":-1}`),&c);check(err==nil&&c.Count<0,"domain invalid")""",
            "Separating syntax and semantics yields better diagnostics. A decoder cannot infer that this application forbids negative counts.",
        ),
    ],
    imports="encoding/json strings io",
    helper=r"""type Config struct { Name string `json:"name"`; Count int `json:"count"` }""",
    source="https://pkg.go.dev/encoding/json",
)

add(
    "CSV, record shape and data-quality contracts",
    """A CSV record is a sequence of fields with quoting rules. Splitting text on commas fails when a field itself contains a comma, newline or escaped quote. encoding/csv handles this syntax and can enforce a consistent field count. Parsing a record still does not establish its schema: headers, data types, missing values, duplicate keys and row grain need explicit validation. Streaming records supports bounded memory, but one record can be large, so upstream input budgets still matter. Keep original row numbers and field names in diagnostics without printing sensitive full records. An empty numeric field is not automatically zero.""",
    """csv.NewReader accepts an io.Reader. Read returns one record or an error; ReadAll is convenient only for explicitly bounded fixtures. FieldsPerRecord enforces shape, and a value of zero lets the first record establish the expected width. csv.Writer buffers output, so call Flush and inspect Error. Quoted commas remain part of one field rather than creating extra columns.""",
    [
        ("Record grain", "The entity represented by one row."),
        ("Quoted field", "A field whose delimiters or newlines are escaped by CSV syntax."),
        ("Schema validation", "Checking field meaning after transport parsing."),
    ],
    [
        E(
            "Parse a quoted comma",
            "Read name and city where the city is Springfield, West.",
            "The record contains two fields.",
            r"""r:=csv.NewReader(strings.NewReader("Ada,\"Springfield, West\"\n"));v,err:=r.Read();check(err==nil&&len(v)==2&&v[1]=="Springfield, West","quoted comma")""",
            "A comma inside quotes belongs to the field. strings.Split would incorrectly create three fields.",
        ),
        E(
            "Reject a ragged row",
            "Require two fields and read a three-field row.",
            "The reader reports a field-count error.",
            r"""r:=csv.NewReader(strings.NewReader("a,b,c\n"));r.FieldsPerRecord=2;_,err:=r.Read();check(err!=nil,"ragged row")""",
            "Rejecting inconsistent shape prevents silent column shifts that can corrupt downstream type interpretation.",
        ),
        E(
            "Decode a numeric field",
            "Parse the second field of item,12 as an integer.",
            "The numeric value is 12.",
            r"""r:=csv.NewReader(strings.NewReader("item,12\n"));v,err:=r.Read();check(err==nil,"record");n,err:=strconv.Atoi(v[1]);check(err==nil&&n==12,"numeric field")""",
            "CSV parsing returns strings. Numeric conversion is a separate fallible schema operation.",
        ),
        E(
            "Reject blank numeric content",
            "Attempt integer parsing of an empty field.",
            "The conversion fails rather than becoming zero.",
            r"""_,err:=strconv.Atoi("");check(err!=nil,"blank number")""",
            "Missingness requires a policy. Replacing every parse error with zero changes the data and hides the distinction between missing and measured zero.",
        ),
        E(
            "Round-trip a delimiter field",
            "Write a field containing a comma, flush, then read it back.",
            "The original field survives exactly.",
            r"""var b bytes.Buffer;w:=csv.NewWriter(&b);check(w.Write([]string{"a,b","3"})==nil,"write");w.Flush();check(w.Error()==nil,"flush");v,err:=csv.NewReader(&b).Read();check(err==nil&&v[0]=="a,b","round trip")""",
            "The writer chooses correct quoting. Hand-joining fields with commas cannot preserve this contract for arbitrary text.",
        ),
        E(
            "Transfer header validation",
            "Read the header name,count and compare its exact order.",
            "The schema order is name then count.",
            r"""v,err:=csv.NewReader(strings.NewReader("name,count\n")).Read();check(err==nil&&len(v)==2&&v[0]=="name"&&v[1]=="count","header contract")""",
            "Matching a set of names is insufficient when later code indexes by position. Either validate order or construct an explicit name-to-index map.",
        ),
    ],
    imports="encoding/csv strings strconv bytes",
    source="https://pkg.go.dev/encoding/csv",
)

add(
    "Command-line contracts and configuration precedence",
    """A command-line interface translates external strings into validated application configuration. Defaults, flags, environment and configuration files need an explicit precedence order; silently mixing them creates surprising deployments. Parse configuration once at the boundary and pass a typed value to the program. The browser pad has no arbitrary argument channel, so this lesson uses an isolated flag.FlagSet with synthetic argument slices. This exercises the real parser without changing the process global flags. A production CLI also needs clear help, stable exit codes, redacted diagnostics and a documented distinction between malformed input and runtime failure.""",
    """flag.NewFlagSet with ContinueOnError returns parse failures instead of exiting the process. IntVar binds a flag to storage, Parse accepts a []string and Args returns positional leftovers. SetOutput can redirect diagnostics to a buffer for tests. Do not call os.Exit from a library helper, because it prevents its caller from controlling cleanup and testing. Validate ranges after parsing: the parser can accept a negative integer even if the domain forbids it.""",
    [
        ("Precedence", "The declared order in which configuration sources override one another."),
        ("Flag set", "An isolated collection of command-line options."),
        (
            "Validation boundary",
            "The point where external input becomes trusted typed configuration.",
        ),
    ],
    [
        E(
            "Apply an explicit flag",
            "Parse -count=3 with a default of 1.",
            "The resulting count is 3.",
            r"""n,args,err:=parseArgs([]string{"-count=3"});check(err==nil&&n==3&&len(args)==0,"flag")""",
            "The synthetic argument slice tests the actual parser while remaining independent of the classroom process arguments.",
        ),
        E(
            "Retain a default",
            "Parse no arguments.",
            "The count remains 1.",
            r"""n,_,err:=parseArgs(nil);check(err==nil&&n==1,"default")""",
            "A default is an intentional contract, not an accidental zero value. Changing it can alter existing workflows even when parsing code is unchanged.",
        ),
        E(
            "Reject an unknown option",
            "Parse -mystery=2.",
            "Parsing returns an error.",
            r"""_,_,err:=parseArgs([]string{"-mystery=2"});check(err!=nil,"unknown option")""",
            "Unknown-flag rejection catches misspellings. Ignoring them would make users believe a setting was applied when it was not.",
        ),
        E(
            "Preserve positional arguments",
            "Parse a count flag followed by a filename.",
            "The remaining argument is input.csv.",
            r"""_,args,err:=parseArgs([]string{"-count=2","input.csv"});check(err==nil&&len(args)==1&&args[0]=="input.csv","positionals")""",
            "Flags and positional arguments have distinct roles. Validate their count and interpretation before opening any file.",
        ),
        E(
            "Reject a domain-invalid count",
            "Parse -count=-1 and perform range validation.",
            "The operation returns a domain error.",
            r"""_,_,err:=parseArgs([]string{"-count=-1"});check(err!=nil,"range")""",
            "Successful integer parsing does not imply an acceptable concurrency, retry or item-count budget.",
        ),
        E(
            "Transfer precedence",
            "Apply a flag override of 4 after a default value of 1.",
            "The explicit setting wins.",
            r"""n,_,err:=parseArgs([]string{"-count=4"});check(err==nil&&n==4,"precedence")""",
            "In a larger program, document whether flags override environment or files. Avoid repeated environment reads deep inside business logic.",
        ),
    ],
    imports="flag io errors",
    helper=r"""func parseArgs(args []string)(int,[]string,error){f:=flag.NewFlagSet("lesson",flag.ContinueOnError);f.SetOutput(io.Discard);n:=1;f.IntVar(&n,"count",1,"positive count");if err:=f.Parse(args);err!=nil{return 0,nil,err};if n<1{return 0,nil,errors.New("positive count required")};return n,f.Args(),nil}""",
    source="https://pkg.go.dev/flag",
)

add(
    "HTTP handlers and in-process service tests",
    """HTTP separates method, target, headers, status and body. A handler implements a protocol boundary, not merely a function that returns text. Validate the method and path before applying domain behavior. WriteHeader chooses a response status before the first body write; once a response starts, changing status may be too late. An in-process recorder can test routing and output without opening a socket. This is excellent unit evidence but does not establish real TLS, proxy, timeout or network behavior. Production servers also need bounded request bodies, explicit timeouts, graceful shutdown and safe logging.""",
    """http.HandlerFunc adapts a function with ResponseWriter and *Request parameters. httptest.NewRequest creates an inbound request, and httptest.NewRecorder captures status, headers and body. Header().Set changes response metadata before writing. http.Error writes an error response. A handler should return after rejecting a request so it does not accidentally continue into a success path.""",
    [
        ("Handler", "Code implementing the response to one HTTP request."),
        ("Status code", "A protocol-level classification of the response."),
        ("Response recorder", "An in-process test object capturing handler output."),
    ],
    [
        E(
            "Serve a health request",
            "Send GET /health to the handler.",
            "The status is 200 and the body is ok plus a newline.",
            r"""r:=httptest.NewRecorder();health(r,httptest.NewRequest("GET","/health",nil));check(r.Code==200&&r.Body.String()=="ok\n","health")""",
            "The recorder runs the handler directly. This proves the handler contract without making any network availability claim.",
        ),
        E(
            "Reject an unsupported method",
            "Send POST /health.",
            "The status is 405 and Allow is GET.",
            r"""r:=httptest.NewRecorder();health(r,httptest.NewRequest("POST","/health",nil));check(r.Code==405&&r.Header().Get("Allow")=="GET","method")""",
            "The method boundary is explicit. Returning after the error prevents success text from being appended to an already rejected response.",
        ),
        E(
            "Reject an unknown route",
            "Send GET /missing.",
            "The status is 404.",
            r"""r:=httptest.NewRecorder();health(r,httptest.NewRequest("GET","/missing",nil));check(r.Code==404,"route")""",
            "A catch-all success handler can conceal path mistakes and break monitoring assumptions.",
        ),
        E(
            "Check content metadata",
            "Inspect the successful response content type.",
            "The response declares text/plain with UTF-8.",
            r"""r:=httptest.NewRecorder();health(r,httptest.NewRequest("GET","/health",nil));check(r.Header().Get("Content-Type")=="text/plain; charset=utf-8","content type")""",
            "Representation metadata belongs to the response contract. The body alone does not describe how a client should interpret it.",
        ),
        E(
            "Repeat without shared mutation",
            "Run two independent health requests.",
            "Both responses succeed identically.",
            r"""for i:=0;i<2;i++{r:=httptest.NewRecorder();health(r,httptest.NewRequest("GET","/health",nil));check(r.Code==200&&r.Body.String()=="ok\n","repeat")}""",
            "The handler has no mutable request-global state. More complex handlers should keep per-request data separate from explicitly synchronized shared state.",
        ),
        E(
            "Transfer query independence",
            "Call /health with an unrelated query parameter.",
            "The path still matches and returns 200.",
            r"""r:=httptest.NewRecorder();health(r,httptest.NewRequest("GET","/health?probe=1",nil));check(r.Code==200,"query separation")""",
            "URL.Path excludes the query string. If query parameters influence behavior, validate them separately instead of matching the entire raw target.",
        ),
    ],
    imports="net/http net/http/httptest",
    helper=r"""func health(w http.ResponseWriter,r *http.Request){if r.URL.Path!="/health"{http.NotFound(w,r);return};if r.Method!="GET"{w.Header().Set("Allow","GET");http.Error(w,"method not allowed",http.StatusMethodNotAllowed);return};w.Header().Set("Content-Type","text/plain; charset=utf-8");w.WriteHeader(http.StatusOK);fmt.Fprintln(w,"ok")}""",
    source="https://pkg.go.dev/net/http/httptest",
)

add(
    "HTTP clients, cancellation and response ownership",
    """An HTTP client owns a request lifecycle that can fail before any response exists or return a valid HTTP response describing an application failure. A 404 is usually not a transport error. Callers must inspect status, bound response bodies and close every acquired response body. Context cancellation propagates an explicit stop signal, while a client timeout bounds the overall operation. Reuse clients and transports in real services rather than constructing an unbounded pool of connections. This lesson injects a RoundTripper fake so the real client logic can be exercised without DNS, ports or external services.""",
    """RoundTrip(*http.Request) returns a response or a transport error. A function adapter can implement that interface for tests. NewRequestWithContext binds a request to cancellation. Client.Do follows client policy, including status-independent transport success. Read at most limit+1 bytes to detect oversized bodies. A response body must be closed even when its status is not accepted.""",
    [
        ("Transport error", "Failure to obtain a valid HTTP response."),
        ("Response ownership", "The obligation to consume or close an acquired body."),
        ("Cancellation", "An explicit request to stop bounded work."),
    ],
    [
        E(
            "Read a successful response",
            "Use a fake transport returning status 200 and body ready.",
            "The client helper returns ready without error.",
            r"""v,err:=fetch(context.Background(),200,"ready",8);check(err==nil&&v=="ready","client success")""",
            "The fake isolates policy from the network. A live connection test would establish additional behavior and requires a separate owned target.",
        ),
        E(
            "Reject an HTTP failure status",
            "Return status 404 with a body.",
            "The helper returns an error despite transport success.",
            r"""_,err:=fetch(context.Background(),404,"missing",8);check(err!=nil,"HTTP status")""",
            "Client.Do does not classify every non-2xx response as a transport failure. Application status policy belongs in the consuming code.",
        ),
        E(
            "Detect an oversized body",
            "Return five bytes with a maximum of four.",
            "The helper rejects the response.",
            r"""_,err:=fetch(context.Background(),200,"abcde",4);check(err!=nil,"body limit")""",
            "Reading one extra byte makes the limit observable. Silently truncating to four would make an oversized response look like valid short content.",
        ),
        E(
            "Honor cancellation",
            "Cancel the context before invoking the fake transport.",
            "The returned error matches context.Canceled.",
            r"""ctx,cancel:=context.WithCancel(context.Background());cancel();_,err:=fetch(ctx,200,"ready",8);check(errors.Is(err,context.Canceled),"cancellation")""",
            "The fake explicitly honors the request context. This demonstrates the contract required from a cooperating transport, not a universal guarantee for arbitrary blocking code.",
        ),
        E(
            "Allow exact size",
            "Return four bytes with a maximum of four.",
            "The helper accepts all four bytes.",
            r"""v,err:=fetch(context.Background(),200,"abcd",4);check(err==nil&&v=="abcd","exact size")""",
            "An inclusive byte budget should accept exactly its maximum. This case distinguishes a correct greater-than check from an off-by-one rejection.",
        ),
        E(
            "Transfer an empty body",
            "Return 200 with an empty body under a positive budget.",
            "The transport helper returns an empty string successfully.",
            r"""v,err:=fetch(context.Background(),200,"",4);check(err==nil&&v=="","empty response")""",
            "Transport completion and domain validity are separate. A caller that requires JSON or a nonempty document should validate that after the bounded read.",
        ),
    ],
    imports="net/http context io strings errors",
    helper=r"""type roundTripFunc func(*http.Request)(*http.Response,error)
func (f roundTripFunc) RoundTrip(r *http.Request)(*http.Response,error){return f(r)}
func fetch(ctx context.Context,status int,body string,limit int64)(string,error){client:=&http.Client{Transport:roundTripFunc(func(r *http.Request)(*http.Response,error){if err:=r.Context().Err();err!=nil{return nil,err};return &http.Response{StatusCode:status,Header:make(http.Header),Body:io.NopCloser(strings.NewReader(body)),Request:r},nil})};req,err:=http.NewRequestWithContext(ctx,"GET","http://lesson.invalid/resource",nil);if err!=nil{return "",err};response,err:=client.Do(req);if err!=nil{return "",err};defer response.Body.Close();if response.StatusCode!=200{return "",fmt.Errorf("status %d",response.StatusCode)};data,err:=io.ReadAll(io.LimitReader(response.Body,limit+1));if err!=nil{return "",err};if int64(len(data))>limit{return "",errors.New("response too large")};return string(data),nil}""",
    source="https://pkg.go.dev/net/http",
)

add(
    "Goroutines and explicit completion",
    """A goroutine is a concurrently scheduled execution of a function. Starting one does not make the caller wait for it, and returning from main ends the program even if other goroutines still have work. Concurrency introduces partial ordering: some events must happen before others, while unrelated scheduling remains unspecified. Use communication or synchronization to establish the relationships required by the algorithm. A sleep is a delay, not proof that another goroutine has completed. Every started goroutine needs an owner responsible for its completion or cancellation, otherwise blocked tasks can leak resources and make shutdown unpredictable.""",
    """go function() starts a goroutine. A channel send and receive can transfer a result and establish an ordering relationship. sync.WaitGroup tracks a known set of tasks; Add must happen before a concurrent Wait can conclude. Defer Done inside each task. Do not write a shared ordinary variable concurrently merely because a later print appears to observe the expected value.""",
    [
        ("Goroutine", "An independently scheduled function execution."),
        ("Join", "Waiting for owned concurrent work to complete."),
        ("Happens-before", "A synchronization relationship that orders memory effects."),
    ],
    [
        E(
            "Join a produced result",
            "Start a goroutine computing 6 times 7 and receive its result.",
            "The received value is 42.",
            r"""result:=make(chan int);go func(){result<-6*7}();check(<-result==42,"goroutine result")""",
            "The receive waits for the send. The program does not assume the worker has completed merely because enough wall-clock time passed.",
        ),
        E(
            "Wait for several tasks",
            "Start three tasks that signal a buffered completion channel and wait for all of them.",
            "Exactly three completion markers are received.",
            r"""done:=make(chan struct{},3);var wg sync.WaitGroup;for i:=0;i<3;i++{wg.Add(1);go func(){defer wg.Done();done<-struct{}{}}()};wg.Wait();check(len(done)==3,"joined tasks")""",
            "The buffer avoids blocking completion before the parent reads. WaitGroup joins the tasks; the channel stores inspectable completion evidence.",
        ),
        E(
            "Keep state task-local",
            "Have two goroutines compute from explicit arguments.",
            "The results sum to 13.",
            r"""out:=make(chan int,2);for _,n:=range []int{2,3}{go func(x int){out<-x*x}(n)};a,b:=<-out,<-out;check(a+b==13,"local inputs")""",
            "The order of a and b is unspecified, so the assertion checks an order-independent property. Explicit arguments make each input ownership clear.",
        ),
        E(
            "Establish a start boundary",
            "Block a worker on a start channel, then release it.",
            "The worker returns ready only after release.",
            r"""start:=make(chan struct{});out:=make(chan string);go func(){<-start;out<-"ready"}();close(start);check(<-out=="ready","start boundary")""",
            "Closing a channel can broadcast a one-time event. It does not carry a payload, and ownership must ensure it is closed only once.",
        ),
        E(
            "Reject premature completion",
            "Keep a worker blocked behind a start channel and test whether its result is available before release.",
            "The result is unavailable before release and equals 1 afterward.",
            r"""start:=make(chan struct{});out:=make(chan int);go func(){<-start;out<-1}();premature:=false;select{case <-out:premature=true;default:};check(!premature,"premature completion");close(start);check(<-out==1,"released result")""",
            "The blocked worker cannot send before the start boundary. This negative case rejects the assumption that starting a goroutine means its work has already completed, without relying on a sleep.",
        ),
        E(
            "Transfer deterministic aggregation",
            "Collect squares from four workers and sum them in the receiving goroutine.",
            "The sum is 30.",
            r"""out:=make(chan int,4);for _,n:=range []int{1,2,3,4}{go func(x int){out<-x*x}(n)};sum:=0;for i:=0;i<4;i++{sum+=<-out};check(sum==30,"aggregation")""",
            "Only the receiver mutates sum, so no mutex is required for that accumulator. Channel result order is irrelevant to integer addition in this bounded example.",
        ),
    ],
    imports="sync",
    source="https://go.dev/doc/effective_go#concurrency",
)

add(
    "Channels, buffering and close ownership",
    """A channel connects producers and consumers with typed communication. An unbuffered send completes when a receiver participates; a buffered channel retains values up to its capacity. Buffering changes backpressure, not ownership of referenced objects sent through the channel. Closing means no more values will be sent. Receivers drain buffered values before observing closure. The producer that knows all sending is finished should own close. A receiver normally must not close the channel merely because it is done reading. Sending after close panics; an operation on a nil channel blocks unless a select chooses another ready case.""",
    """make(chan int, 2) creates a two-element buffer. value, ok := <-ch distinguishes a delivered value from the zero value after closure. range ch receives until closed and drained. chan<- int restricts a parameter to sending; <-chan int restricts it to receiving. len(ch) is a transient observation rather than a synchronization protocol.""",
    [
        ("Backpressure", "A producer slowing when a consumer cannot accept more."),
        ("Channel closure", "The declaration that no further sends will occur."),
        ("Directional channel", "A type restricting sending or receiving."),
    ],
    [
        E(
            "Drain before iteration ends",
            "Buffer 2 and 3, close and sum the channel.",
            "Both values arrive and the sum is 5.",
            r"""ch:=make(chan int,2);ch<-2;ch<-3;close(ch);sum:=0;for v:=range ch{sum+=v};check(sum==5,"drain")""",
            "Close does not erase buffered values. Iteration ends after those values have been received.",
        ),
        E(
            "Distinguish zero from closed",
            "Send zero, close, then receive twice with comma-ok.",
            "The first zero has ok true; the second has ok false.",
            r"""ch:=make(chan int,1);ch<-0;close(ch);a,okA:=<-ch;b,okB:=<-ch;check(a==0&&b==0&&okA&&!okB,"closed presence")""",
            "Value equality cannot distinguish a delivered zero from the post-closure zero. The boolean carries completion information.",
        ),
        E(
            "Use sender ownership",
            "Run a producer sending 1 and 2 before closing output.",
            "The consumer receives exactly two values.",
            r"""ch:=make(chan int);go produce(ch);count:=0;for range ch{count++};check(count==2,"producer close")""",
            "The producer knows all sends are finished. A receiver closing early could race with a later send.",
        ),
        E(
            "Inspect bounded buffering",
            "Fill a channel of capacity two without a receiver.",
            "Its buffered length is two.",
            r"""ch:=make(chan int,2);ch<-4;ch<-5;check(len(ch)==2&&cap(ch)==2,"buffer");<-ch;<-ch""",
            "This sequential fixture has an exact count. Concurrent length checks cannot prove a later send will be nonblocking.",
        ),
        E(
            "Disable a nil select arm",
            "Select between nil and a ready closed channel.",
            "Only the ready arm can proceed.",
            r"""var disabled <-chan int;ready:=make(chan struct{});close(ready);selected:=false;select{case <-disabled:panic("nil selected");case <-ready:selected=true};check(selected,"nil arm")""",
            "Nil can deliberately disable an unneeded select case. It does not signal completion like a closed channel.",
        ),
        E(
            "Transfer independent message storage",
            "Send a copied slice, then mutate its original.",
            "The received copy stays 1.",
            r"""original:=[]int{1};ch:=make(chan []int,1);ch<-append([]int(nil),original...);original[0]=9;received:=<-ch;check(received[0]==1,"copy")""",
            "A channel sends the slice descriptor. The explicit copy establishes independent storage before communication.",
        ),
    ],
    helper="func produce(out chan<- int){defer close(out);out<-1;out<-2}",
    source="https://go.dev/ref/spec#Channel_types",
)

add(
    "Select, contexts and cancellation trees",
    """Cancellation is cooperative: a context signals that work should stop, but does not forcibly interrupt every function. Pass context as the first parameter to work whose lifetime belongs to its caller. Derived contexts form a tree, so canceling a parent cancels descendants. Always call the returned cancel function when the owned operation ends, including early success, to release associated resources. A select can wait for work or cancellation, but if both cases are ready its choice is not a priority rule. Check required preconditions explicitly when already-canceled work must never begin.""",
    """context.WithCancel returns a child and cancel function. Done closes on cancellation; Err explains cancellation or deadline expiry. WithDeadline accepts a past time for deterministic testing. A select arm receiving from ctx.Done cooperates with cancellation. Context values carry request-scoped metadata, not optional function arguments, authentication guarantees or mutable application state.""",
    [
        ("Context tree", "Parent-child cancellation relationships."),
        ("Deadline", "An absolute time after which work is no longer wanted."),
        ("Cooperation", "An operation checking and respecting a stop signal."),
    ],
    [
        E(
            "Cancel a child",
            "Create a cancelable context and cancel it.",
            "Err returns context.Canceled.",
            r"""ctx,cancel:=context.WithCancel(context.Background());cancel();check(ctx.Err()==context.Canceled,"cancel")""",
            "Cancellation is visible through Err and the closed Done channel. Repeated cancel calls are safe.",
        ),
        E(
            "Propagate parent cancellation",
            "Derive a child and cancel its parent.",
            "Both contexts become canceled.",
            r"""parent,cancel:=context.WithCancel(context.Background());child,stop:=context.WithCancel(parent);defer stop();cancel();check(parent.Err()==context.Canceled&&child.Err()==context.Canceled,"tree")""",
            "A child cannot extend work beyond the lifetime requested by its parent.",
        ),
        E(
            "Keep child cancellation local",
            "Cancel a child of a live parent.",
            "The child is canceled; the parent is unchanged.",
            r"""parent:=context.Background();child,cancel:=context.WithCancel(parent);cancel();check(child.Err()!=nil&&parent.Err()==nil,"child")""",
            "Cancellation propagates downward. One sub-operation can end without canceling unrelated siblings.",
        ),
        E(
            "Test an expired deadline",
            "Construct a context with a deadline at Unix time zero.",
            "Err is context.DeadlineExceeded.",
            r"""ctx,cancel:=context.WithDeadline(context.Background(),time.Unix(0,0));defer cancel();check(ctx.Err()==context.DeadlineExceeded,"deadline")""",
            "The past deadline avoids flaky sleeps. Real work also needs a separate cleanup allowance after its budget expires.",
        ),
        E(
            "Refuse already canceled work",
            "Call a helper that checks its context before calculation.",
            "It returns cancellation without a result.",
            r"""ctx,cancel:=context.WithCancel(context.Background());cancel();v,err:=contextValue(ctx,4);check(v==0&&err==context.Canceled,"refusal")""",
            "A preflight check expresses the already-canceled policy. A later select alone cannot guarantee cancellation wins over another ready arm.",
        ),
        E(
            "Transfer successful work",
            "Use the same helper with a live context.",
            "It returns 8 without error.",
            r"""v,err:=contextValue(context.Background(),4);check(err==nil&&v==8,"live")""",
            "Long loops or I/O must cooperate during work as well. One entry check is sufficient only for this tiny immediate calculation.",
        ),
    ],
    imports="context time",
    helper="func contextValue(ctx context.Context,x int)(int,error){if err:=ctx.Err();err!=nil{return 0,err};return 2*x,nil}",
    source="https://pkg.go.dev/context",
)

add(
    "Mutexes, atomics and shared-state invariants",
    """A mutex protects a state invariant across several operations. Every relevant access must follow the same protocol: locking writes while reading without synchronization can still race. Atomic operations protect specific values and ordering relationships, but do not automatically make a multi-field transaction atomic. Prefer a mutex for a compound invariant that must be inspected and changed together. Never copy a mutex after use. Keep critical sections small, avoid calling unknown callbacks while holding a lock, and define lock ordering when several locks are unavoidable. A correct observed count is not by itself proof of correct synchronization.""",
    """sync.Mutex uses Lock and Unlock; defer Unlock after acquisition handles early returns. atomic.Int64 supplies typed Load, Store and Add. sync.Once runs one initialization function. Keep synchronized state in a pointer-owned holder so it is not copied accidentally. count++ on an ordinary shared integer is a read-modify-write sequence, not an atomic operation.""",
    [
        ("Critical section", "Code accessing state while holding its lock."),
        ("Compound invariant", "A relationship involving several state values."),
        ("Atomic operation", "An indivisible operation with synchronization semantics."),
    ],
    [
        E(
            "Protect a concurrent count",
            "Run four workers doing 100 protected increments each.",
            "The joined final count is 400.",
            r"""c:=&LockedCount{};var wg sync.WaitGroup;for i:=0;i<4;i++{wg.Add(1);go func(){defer wg.Done();for j:=0;j<100;j++{c.Inc()}}()};wg.Wait();check(c.Value()==400,"count")""",
            "Reads and writes use the same lock. The join establishes task completion before inspection.",
        ),
        E(
            "Use a typed atomic",
            "Add 3 and 4 through atomic.Int64.",
            "Load returns 7.",
            r"""var n atomic.Int64;n.Add(3);n.Add(4);check(n.Load()==7,"atomic")""",
            "Use the atomic access API consistently. Mixing it with ordinary conflicting accesses undermines the protocol.",
        ),
        E(
            "Protect a pair relationship",
            "Transfer 3 between two balances initially 5 and 5.",
            "The balances become 2 and 8; their sum remains 10.",
            r"""p:=&Pair{A:5,B:5};p.Transfer(3);a,b:=p.Snapshot();check(a==2&&b==8&&a+b==10,"pair")""",
            "One lock protects both fields. Independent updates could expose an intermediate state with the wrong total.",
        ),
        E(
            "Initialize once",
            "Call the same sync.Once initializer three times.",
            "Its body runs once.",
            r"""var once sync.Once;n:=0;for i:=0;i<3;i++{once.Do(func(){n++})};check(n==1,"once")""",
            "Once is not a retry mechanism. Fallible initialization requiring retries needs a separately designed state machine.",
        ),
        E(
            "Reject a stale atomic expectation",
            "Perform compare-and-swap twice using the original expected value.",
            "The first succeeds and the second fails.",
            r"""var n atomic.Int64;n.Store(2);check(n.CompareAndSwap(2,3),"CAS");check(!n.CompareAndSwap(2,4)&&n.Load()==3,"stale")""",
            "A stale expectation detects changed state. A single-value CAS does not validate unrelated fields.",
        ),
        E(
            "Transfer safe observation",
            "Read an unchanged protected pair twice.",
            "Both snapshots preserve total 10.",
            r"""p:=&Pair{A:4,B:6};a,b:=p.Snapshot();c,d:=p.Snapshot();check(a+b==10&&c+d==10,"snapshot")""",
            "An accessor hides locking without exposing mutable internals. Returning pointers to fields would bypass that boundary.",
        ),
    ],
    imports="sync sync/atomic",
    helper="""type LockedCount struct{mu sync.Mutex;n int}
func(c *LockedCount)Inc(){c.mu.Lock();defer c.mu.Unlock();c.n++}
func(c *LockedCount)Value()int{c.mu.Lock();defer c.mu.Unlock();return c.n}
type Pair struct{mu sync.Mutex;A,B int}
func(p *Pair)Transfer(n int){p.mu.Lock();defer p.mu.Unlock();p.A-=n;p.B+=n}
func(p *Pair)Snapshot()(int,int){p.mu.Lock();defer p.mu.Unlock();return p.A,p.B}""",
    source="https://pkg.go.dev/sync",
)

add(
    "Bounded worker pools and result ordering",
    """A worker pool limits active execution but does not create infinite capacity. Queues, in-flight tasks and result buffers all consume resources. Give each task an identity so completion order can differ from presentation order. A collector can place results by index to produce a deterministic final sequence. The producer owns input closure, workers process tasks, and a joiner closes results after all senders exit. Cancellation and partial failure need an explicit policy rather than silently losing tasks. This example performs bounded integer work and joins every goroutine. It illustrates coordination without claiming that more workers always make a program faster.""",
    """A jobs channel carries indexed tasks. Start a bounded number of workers, feed jobs and close input. A WaitGroup tracks workers; close results only after Wait completes. Assign each result to its input index. Reject zero workers before starting the pipeline, otherwise a producer may block forever with no consumer.""",
    [
        ("Concurrency bound", "The maximum number of active workers."),
        ("Task identity", "A stable key linking result and input."),
        ("Fan-in", "Combining results from multiple producers."),
    ],
    [
        E(
            "Preserve input order",
            "Square 3, 1 and 2 with two workers.",
            "The result is 9, 1, 4.",
            r"""v,err:=parallelSquares([]int{3,1,2},2);check(err==nil&&len(v)==3&&v[0]==9&&v[1]==1&&v[2]==4,"order")""",
            "Indices restore presentation order. Channel arrival order is not the input-order contract.",
        ),
        E(
            "Handle empty input",
            "Run the pool on an empty slice.",
            "It returns an empty result and terminates.",
            r"""v,err:=parallelSquares(nil,2);check(err==nil&&len(v)==0,"empty")""",
            "Every channel reaches its owned closure point even when no jobs exist.",
        ),
        E(
            "Reject absent capacity",
            "Request zero workers.",
            "The call returns an error immediately.",
            r"""_,err:=parallelSquares([]int{1},0);check(err!=nil,"zero workers")""",
            "Validation before goroutine creation prevents a deadlock instead of attempting to recover from it.",
        ),
        E(
            "Compare serial semantics",
            "Use one and three workers for the same three inputs.",
            "Both produce the same sequence.",
            r"""a,e1:=parallelSquares([]int{1,2,3},1);b,e2:=parallelSquares([]int{1,2,3},3);check(e1==nil&&e2==nil&&slices.Equal(a,b),"same semantics")""",
            "Scheduling changes while the calculation contract stays fixed. Timing claims require separate measurements.",
        ),
        E(
            "Retain duplicate tasks",
            "Process 2, 2 and 2.",
            "All three results are retained.",
            r"""v,err:=parallelSquares([]int{2,2,2},2);check(err==nil&&len(v)==3&&v[2]==4,"duplicates")""",
            "Positional task identity avoids accidentally deduplicating legitimate repeated work.",
        ),
        E(
            "Transfer idle-worker cleanup",
            "Use four workers for one input of 5.",
            "One result equals 25 and all workers exit.",
            r"""v,err:=parallelSquares([]int{5},4);check(err==nil&&len(v)==1&&v[0]==25,"idle workers")""",
            "Idle workers stop when input closes. Excess capacity still has an operational cost even when termination is correct.",
        ),
    ],
    imports="sync errors slices",
    helper="""type squareTask struct{Index,Value int}
func parallelSquares(items []int,workers int)([]int,error){if workers<1||workers>8{return nil,errors.New("workers must be 1 through 8")};jobs:=make(chan squareTask);results:=make(chan squareTask);var wg sync.WaitGroup;for i:=0;i<workers;i++{wg.Add(1);go func(){defer wg.Done();for task:=range jobs{task.Value*=task.Value;results<-task}}()};go func(){for i,v:=range items{jobs<-squareTask{i,v}};close(jobs)}();go func(){wg.Wait();close(results)}();out:=make([]int,len(items));for result:=range results{out[result.Index]=result.Value};return out,nil}""",
)

add(
    "The memory model, race diagnosis and publication",
    """A data race occurs when conflicting concurrent accesses include a write and lack synchronization. A program that prints the desired value once can still race. The memory model specifies ordering guarantees supplied by channels, mutexes and other primitives. Publish initialized state through such a boundary, then keep it immutable or protect future mutations. The race detector observes executed instrumented paths; a clean run is evidence rather than proof about every schedule. Do not intentionally execute racy examples in ordinary references. Prefer a design whose ownership and ordering can be explained before relying on a diagnostic tool.""",
    """A channel send synchronizes with its corresponding receive. Closing a channel synchronizes with a receive observing closure. An unlock synchronizes with a later lock on that mutex. atomic.Value can publish immutable snapshots. The ordinary pad has CGO disabled and does not claim race instrumentation; a prepared Linux development project with a compatible C toolchain can run go test -race ./....""",
    [
        ("Data race", "Conflicting unsynchronized concurrent memory access."),
        ("Publication", "Sharing initialized state through synchronization."),
        ("Immutable snapshot", "A shared value that is no longer mutated."),
    ],
    [
        E(
            "Publish through a channel",
            "Send an initialized record from a goroutine.",
            "The reader observes count 3 and ready true.",
            r"""ch:=make(chan Published);go func(){ch<-Published{Count:3,Ready:true}}();v:=<-ch;check(v.Ready&&v.Count==3,"publication")""",
            "The send and receive establish ordering without a timing guess.",
        ),
        E(
            "Publish through closure",
            "Write 7 before closing done, then read after receiving done.",
            "The reader observes 7.",
            r"""done:=make(chan struct{});n:=0;go func(){n=7;close(done)}();<-done;check(n==7,"close publication")""",
            "Removing this synchronization would make the ordinary shared variable unsafe. The proof uses ordering, not elapsed time.",
        ),
        E(
            "Publish an atomic value",
            "Store a complete record in atomic.Value.",
            "The loaded record has count 4.",
            r"""var current atomic.Value;current.Store(Published{Count:4,Ready:true});v:=current.Load().(Published);check(v.Count==4&&v.Ready,"atomic value")""",
            "Publishing a pointer does not make subsequent unsynchronized target mutation safe. This snapshot has scalar fields.",
        ),
        E(
            "Retain a previous snapshot",
            "Load a value, then replace the stored value.",
            "The old copy remains 4 and the current value is 5.",
            r"""var current atomic.Value;current.Store(Published{Count:4});old:=current.Load().(Published);current.Store(Published{Count:5});check(old.Count==4&&current.Load().(Published).Count==5,"replacement")""",
            "Value snapshots avoid shared mutable fields only when their contained values also have the intended ownership semantics.",
        ),
        E(
            "Copy reference-containing data",
            "Copy a slice before mutating the original.",
            "The snapshot retains its original first element.",
            r"""original:=[]int{1,2};snapshot:=append([]int(nil),original...);original[0]=9;check(snapshot[0]==1,"independent data")""",
            "Copying can eliminate shared mutable storage. Synchronization instead orders accesses to storage that remains shared.",
        ),
        E(
            "Transfer local construction",
            "Build a result string inside a worker and send the completed value.",
            "The reader receives ready:3.",
            r"""ch:=make(chan string);go func(){ch<-fmt.Sprintf("ready:%d",3)}();check(<-ch=="ready:3","result")""",
            "Keeping construction state local simplifies the argument compared with exposing several partially updated shared fields.",
        ),
    ],
    imports="sync/atomic",
    helper="type Published struct{Count int;Ready bool}",
    source="https://go.dev/ref/mem",
    boundary="Race detection is a separately prepared project workflow. The CGO-disabled ordinary worker executes these synchronized references, but does not run the race detector. Retain a regression test for each contested access and explain the synchronization change. Adding sleeps does not repair a data race.",
)

add(
    "Algorithms, benchmarks and allocation-aware design",
    """Performance work starts with a behavioral contract and representative input. Complexity predicts growth in work, while a benchmark measures a particular implementation and environment. A linear scan visits each item; binary search repeatedly narrows a sorted interval. Faster execution is useful only if it preserves the result and failure policy. Preallocating slice capacity can avoid growth allocations, but preallocating length creates real zero elements. Tiny timings are noisy. Separate setup from measurement, repeat a representative workload, record environment and check results outside the timing loop. A profile should answer a hypothesis about where time or allocations are spent.""",
    """sort.Search finds the first index where a monotone predicate becomes true, or n when none does. It does not sort or validate input. make([]int,0,n) reserves capacity with zero length; make([]int,n) creates n elements. Prepared project benchmarks use testing.B in _test.go files; pprof investigates CPU or allocation evidence rather than establishing a universal speed ranking.""",
    [
        ("Complexity", "How work grows with input size."),
        (
            "Monotone predicate",
            "A predicate changing from false to true at most once over ordered indices.",
        ),
        ("Preallocation", "Reserving storage before appending."),
    ],
    [
        E(
            "Find a lower boundary",
            "Find the first value at least 5 in 2, 4, 6, 8.",
            "The index is 2.",
            r"""items:=[]int{2,4,6,8};i:=sort.Search(len(items),func(i int)bool{return items[i]>=5});check(i==2,"boundary")""",
            "Sorting makes the predicate monotone. The same expression over unsorted input violates the algorithm precondition.",
        ),
        E(
            "Represent no match",
            "Search for a value at least 9 in the same data.",
            "The index equals the collection length.",
            r"""items:=[]int{2,4,6,8};i:=sort.Search(len(items),func(i int)bool{return items[i]>=9});check(i==len(items),"not found")""",
            "The sentinel is not a valid element index. Check it before indexing.",
        ),
        E(
            "Separate length and capacity",
            "Reserve capacity four, then append one value.",
            "Length is 1, capacity is 4.",
            r"""items:=make([]int,0,4);items=append(items,7);check(len(items)==1&&cap(items)==4&&items[0]==7,"capacity")""",
            "Starting with length four would create four logical zeros before the appended value.",
        ),
        E(
            "Count linear work",
            "Sum five values and count visits.",
            "There are five visits and the sum is 15.",
            r"""visits,sum:=0,0;for _,v:=range []int{1,2,3,4,5}{visits++;sum+=v};check(visits==5&&sum==15,"work")""",
            "Operation counting supplies structural evidence without inventing a universal wall-clock threshold.",
        ),
        E(
            "Handle empty search",
            "Search a zero-length interval.",
            "Index is 0 and the predicate is never called.",
            r"""calls:=0;i:=sort.Search(0,func(i int)bool{calls++;return true});check(i==0&&calls==0,"empty")""",
            "The empty interval has a valid insertion position without accessing any element.",
        ),
        E(
            "Transfer duplicate boundaries",
            "Find the first value at least 3 in 1, 3, 3, 5.",
            "The first duplicate has index 1.",
            r"""items:=[]int{1,3,3,5};i:=sort.Search(len(items),func(i int)bool{return items[i]>=3});check(i==1,"duplicates")""",
            "A lower bound is more precise than any matching index. That contract supports insertion and range queries.",
        ),
    ],
    imports="sort",
    source="https://pkg.go.dev/testing#hdr-Benchmarks",
)

add(
    "Structured logging and observable operations",
    """Logs describe events; stable fields let operators inspect them without parsing prose. A correlation ID connects related work, a level indicates severity and numeric counts support diagnosis. Logging does not replace returning an error or checking an invariant. Avoid credentials, raw tokens, complete user payloads and unbounded identifiers. Structured output can still leak data if its fields are chosen badly. Tests should control timestamps and parse records instead of comparing incidental field order. Metrics describe aggregates, logs describe events and traces connect distributed spans. Choose which evidence answers the question rather than emitting everything indiscriminately.""",
    """log/slog builds records from key/value attributes. JSONHandler writes to an io.Writer. HandlerOptions.ReplaceAttr can remove timestamps in deterministic tests. Logger.With attaches common attributes to a derived logger. A logged status is a report, while the actual operation and durable receipt remain separate evidence.""",
    [
        ("Structured attribute", "A named value attached to a log event."),
        ("Correlation ID", "A bounded identifier linking related events."),
        ("Redaction", "Removing sensitive values before output."),
    ],
    [
        E(
            "Emit a structured event",
            "Log processed with count 3 and parse its JSON.",
            "The record has message processed and numeric count 3.",
            r"""v:=logRecord("processed","count",3);check(v["msg"]=="processed"&&v["count"]==float64(3),"fields")""",
            "The check inspects meaning rather than serialized field order.",
        ),
        E(
            "Retain correlation",
            "Log request_id lesson-7.",
            "The ID is retained exactly.",
            r"""v:=logRecord("read","request_id","lesson-7");check(v["request_id"]=="lesson-7","correlation")""",
            "A bounded synthetic ID is sufficient. Secrets and complete payloads are inappropriate correlation fields.",
        ),
        E(
            "Control variable time",
            "Inspect the deterministic fixture record.",
            "The time attribute is absent.",
            r"""v:=logRecord("stable");_,present:=v["time"];check(!present,"time")""",
            "Production logs generally need time. The fixture deliberately controls a variable field instead of asserting the current clock.",
        ),
        E(
            "Keep status structured",
            "Log a failed status separately from its message.",
            "status equals failed.",
            r"""v:=logRecord("read finished","status","failed");check(v["status"]=="failed","status")""",
            "Filtering a structured status is more reliable than searching for a particular sentence.",
        ),
        E(
            "Redact before logging",
            "Replace a credential value with a fixed marker.",
            "Only [redacted] is present.",
            r"""v:=logRecord("configuration","credential","[redacted]");check(v["credential"]=="[redacted]","redaction")""",
            "Redaction at the producer boundary is easier to review than attempting to remove secrets after serialization.",
        ),
        E(
            "Transfer numeric evidence",
            "Log a byte count of 12.",
            "The parsed field remains numeric 12.",
            r"""v:=logRecord("read","bytes",12);check(v["bytes"]==float64(12),"numeric")""",
            "Numbers should remain numbers for aggregation. The test decoder represents JSON numbers as float64 by default.",
        ),
    ],
    imports="log/slog bytes encoding/json",
    helper="""func logRecord(message string,args ...any)map[string]any{var b bytes.Buffer;handler:=slog.NewJSONHandler(&b,&slog.HandlerOptions{ReplaceAttr:func(groups []string,a slog.Attr)slog.Attr{if a.Key==slog.TimeKey{return slog.Attr{}};return a}});slog.New(handler).Info(message,args...);var value map[string]any;if err:=json.Unmarshal(b.Bytes(),&value);err!=nil{panic(err)};return value}""",
    source="https://pkg.go.dev/log/slog",
)

add(
    "Security boundaries, escaping and input budgets",
    """Security starts by identifying untrusted inputs and operations carrying authority. Validation defines the accepted domain, while escaping protects the syntax of a particular output context. HTML escaping, URL encoding and SQL parameter binding solve different problems. They are not interchangeable. A string replacement is not an authorization policy. Bound input before expensive parsing, reject ambiguous forms and keep secrets out of diagnostics. These harmless examples expose boundary semantics; they do not establish that the local classroom is safe for hosting arbitrary untrusted tenants. Review authority and ownership before connecting code to real files, networks or services.""",
    """html/template escapes according to HTML context; text/template does not supply that protection. url.QueryEscape encodes one query value rather than an entire URL. filepath.IsLocal checks a lexical property but does not resolve symlinks. subtle.ConstantTimeCompare compares equal-length byte sequences without value-dependent comparison time. Protocol design must still handle length, storage and cryptographic choices.""",
    [
        ("Trust boundary", "A point where data from another authority enters an operation."),
        ("Contextual escaping", "Encoding data for the syntax where it will appear."),
        ("Allowlist", "A deliberately limited set of accepted values or operations."),
    ],
    [
        E(
            "Escape HTML data",
            "Render script-like text with html/template.",
            "Angle brackets become escaped text.",
            r"""var b bytes.Buffer;t:=template.Must(template.New("x").Parse("<p>{{.}}</p>"));check(t.Execute(&b,"<script>alert(1)</script>")==nil,"render");check(strings.Contains(b.String(),"&lt;script&gt;"),"escape")""",
            "Marking untrusted input as template.HTML would bypass this boundary. Keep data as data.",
        ),
        E(
            "Encode a query value",
            "Encode a value containing ampersand and equals characters.",
            "Decoding recovers the original string.",
            r"""original:="a&role=admin";encoded:=url.QueryEscape(original);decoded,err:=url.QueryUnescape(encoded);check(err==nil&&decoded==original&&encoded!=original,"query")""",
            "Encoding prevents data from being interpreted as new query syntax. It does not authorize the resulting request.",
        ),
        E(
            "Reject traversal grammar",
            "Compare ../outside with reports/item.txt.",
            "Only the second path is lexically local.",
            r"""check(!filepath.IsLocal("../outside")&&filepath.IsLocal("reports/item.txt"),"local path")""",
            "Symlinks and concurrent filesystem changes require a stronger access boundary than lexical checks alone.",
        ),
        E(
            "Apply a byte budget",
            "Compare three-byte and five-byte values against maximum four.",
            "Only the smaller value fits.",
            r"""check(len([]byte("abc"))<=4&&len([]byte("abcde"))>4,"budget")""",
            "Byte count matches encoded storage consumption. Rune count answers a different question.",
        ),
        E(
            "Compare fixed-size values",
            "Compare equal and unequal four-byte values.",
            "The helper returns 1 for equal and 0 for unequal.",
            r"""check(subtle.ConstantTimeCompare([]byte("abcd"),[]byte("abcd"))==1,"equal");check(subtle.ConstantTimeCompare([]byte("abcd"),[]byte("abce"))==0,"different")""",
            "This is an API demonstration with synthetic values. It is not a complete authentication design.",
        ),
        E(
            "Transfer a reviewed action set",
            "Allow read and list, then inspect read and exec.",
            "read is accepted and exec is rejected.",
            r"""allowed:=map[string]bool{"read":true,"list":true};check(allowed["read"]&&!allowed["exec"],"allowlist")""",
            "Map accepted names to reviewed behavior. Do not turn input strings into shell commands or arbitrary endpoints.",
        ),
    ],
    imports="html/template bytes strings net/url path/filepath crypto/subtle",
    source="https://pkg.go.dev/html/template",
)
