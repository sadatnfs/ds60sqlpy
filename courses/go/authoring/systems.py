"""Advanced application boundaries and Kubernetes control-plane reasoning."""

from render import add
from render import case as E

add(
    "Repository interfaces and transaction failure policy",
    """A repository boundary separates business operations from database mechanics. The application should describe the transaction it needs, while an adapter manages SQL parameters, context cancellation, row scanning and commit or rollback. In database/sql, a DB is a connection pool rather than one connection. A Tx reserves a transaction context whose operations must all use that Tx. Calling the outer DB halfway through a transaction can escape its atomicity. This lesson uses a small copy-on-write transactional model to test policy offline. It is explicitly not evidence about PostgreSQL isolation, driver behavior or network failure. Those require a prepared database integration test.""",
    """A callback receiving a transaction-local value can stage changes before committing them to the outer state. An error aborts the staged changes. In a real database/sql adapter, begin with BeginTx(ctx, options), defer Rollback, execute parameterized statements through tx, and inspect Commit errors. SQL syntax and placeholder conventions depend on the selected driver. Never construct SQL by interpolating untrusted values. A transaction whose commit outcome is unknown cannot safely be replayed without an idempotency contract.""",
    [
        ("Transaction", "A group of changes committed or rejected as one unit."),
        ("Repository boundary", "An application-facing data access contract."),
        ("Unknown outcome", "A state where failure to observe success does not prove work failed."),
    ],
    [
        E(
            "Commit a valid change",
            "Transfer 3 between balances 5 and 5 in a staged transaction.",
            "The committed balances are 2 and 8.",
            r"""s:=Balances{A:5,B:5};err:=transact(&s,func(t *Balances)error{t.A-=3;t.B+=3;return nil});check(err==nil&&s.A==2&&s.B==8,"commit")""",
            "The outer state changes only after the callback succeeds. This proves the local model policy, not database atomicity.",
        ),
        E(
            "Rollback an explicit failure",
            "Change staged state and return an error.",
            "The outer balances remain unchanged.",
            r"""s:=Balances{A:5,B:5};err:=transact(&s,func(t *Balances)error{t.A=0;return errors.New("reject")});check(err!=nil&&s.A==5,"rollback")""",
            "A staged mutation is not a committed mutation. The distinction is visible because the model uses a separate value copy.",
        ),
        E(
            "Reject invalid funds",
            "Attempt a transfer larger than available balance.",
            "The state remains 5 and 5.",
            r"""s:=Balances{A:5,B:5};err:=transact(&s,func(t *Balances)error{if t.A<8{return errors.New("insufficient")};t.A-=8;t.B+=8;return nil});check(err!=nil&&s.A==5&&s.B==5,"funds")""",
            "Validate the invariant in the same transaction that applies the change. A separate preflight read can become stale.",
        ),
        E(
            "Preserve total value",
            "Apply two successful transfers and inspect the combined balance.",
            "The total remains 10.",
            r"""s:=Balances{A:5,B:5};for i:=0;i<2;i++{check(transact(&s,func(t *Balances)error{t.A--;t.B++;return nil})==nil,"transfer")};check(s.A+s.B==10,"total")""",
            "The invariant relates both fields. Real isolation must prevent other transactions from observing or creating forbidden combinations.",
        ),
        E(
            "Keep a failed retry distinct",
            "Fail one transaction, then explicitly start a new valid transaction.",
            "Only the second change commits.",
            r"""s:=Balances{A:5,B:5};_ = transact(&s,func(t *Balances)error{t.A=99;return errors.New("fail")});check(transact(&s,func(t *Balances)error{t.A--;t.B++;return nil})==nil&&s.A==4,"retry")""",
            "This retry is safe because the first local model outcome is known. A lost database commit response requires stronger evidence.",
        ),
        E(
            "Transfer no-op semantics",
            "Run a transaction that changes nothing.",
            "The state is preserved and the operation succeeds.",
            r"""s:=Balances{A:5,B:5};err:=transact(&s,func(t *Balances)error{return nil});check(err==nil&&s.A==5&&s.B==5,"no-op")""",
            "Idempotent no-op behavior is useful, but it does not automatically make arbitrary external side effects replay-safe.",
        ),
    ],
    imports="errors",
    helper="""type Balances struct{A,B int}
func transact(s *Balances,f func(*Balances)error)error{copy:=*s;if err:=f(&copy);err!=nil{return err};*s=copy;return nil}""",
    source="https://go.dev/doc/database/execute-transactions",
    boundary="The ordinary pad executes a transactional policy model, not a database. A real project must select and pin a PostgreSQL driver, provision an explicitly disposable database, bind parameters, and run integration tests for rollback, constraints, isolation and unknown commit outcomes. Never reuse a learner or shared production database for destructive tests.",
)

add(
    "Build targets, containers and graceful process design",
    """An executable is built for a target operating system and architecture. Source portability does not imply one binary runs everywhere. Go can cross-compile many pure-Go programs by choosing GOOS and GOARCH, while cgo and platform-specific dependencies introduce additional constraints. Container images package the executable and its runtime files, but still depend on a compatible kernel and architecture. A small image is useful only if certificates, time-zone needs and diagnostic requirements remain satisfied. Production shutdown must stop accepting new work, cancel or drain owned tasks within a budget, and report incomplete work honestly.""",
    """runtime.GOOS and GOARCH describe the running binary target. Build configuration uses environment variables before compilation, not source-level guesses. A multi-stage Dockerfile can compile in a toolchain image and copy the binary into a runtime stage. CGO_ENABLED=0 is appropriate for this standard-library classroom profile; it is not a universal instruction for every dependency. Use an exec-form container entrypoint so the process receives termination signals directly.""",
    [
        ("Build target", "The operating system and architecture selected for a binary."),
        ("Multi-stage build", "A build separating toolchain and runtime filesystem stages."),
        (
            "Graceful shutdown",
            "A bounded transition from accepting work to releasing owned resources.",
        ),
    ],
    [
        E(
            "Inspect the current target",
            "Read runtime target identifiers.",
            "Both identifiers are nonempty.",
            r"""check(runtime.GOOS!=""&&runtime.GOARCH!="","target")""",
            "The values describe this executed binary. They do not establish compatibility with another platform.",
        ),
        E(
            "Validate a supported deployment tuple",
            "Check linux/amd64 and linux/arm64 against an explicit target set.",
            "Both tuples are admitted.",
            r"""allowed:=map[string]bool{"linux/amd64":true,"linux/arm64":true};check(allowed["linux/amd64"]&&allowed["linux/arm64"],"targets")""",
            "A declared target set is a configuration contract. Each image architecture still needs real build and execution evidence.",
        ),
        E(
            "Refuse an unsupported tuple",
            "Check an unrelated target against the same set.",
            "The unsupported target is rejected.",
            r"""allowed:=map[string]bool{"linux/amd64":true,"linux/arm64":true};check(!allowed["plan9/386"],"unsupported")""",
            "Explicit rejection is clearer than silently choosing an incompatible artifact.",
        ),
        E(
            "Model stop-accepting before drain",
            "Transition a service state from accepting to draining to stopped.",
            "No new work is admitted once draining begins.",
            r"""s:=ServiceState{Accepting:true,Active:2};s.Accepting=false;check(!s.Accepting&&s.Active==2,"drain start");s.Active=0;check(!s.Accepting&&s.Active==0,"stopped")""",
            "Stopping admission and completing in-flight work are different steps. A single stopped flag cannot explain partial shutdown.",
        ),
        E(
            "Retain unfinished work evidence",
            "Apply a shutdown budget that ends before two tasks finish.",
            "The remaining task count stays visible.",
            r"""s:=ServiceState{Accepting:false,Active:2};s.Active--;check(s.Active==1,"unfinished work")""",
            "A timeout must not manufacture completion. Real services should retain or report recoverable work according to their delivery guarantees.",
        ),
        E(
            "Transfer deterministic version metadata",
            "Format a version and source revision into a build label.",
            "The result is lesson/1.0 revision=abc123.",
            r"""label:=fmt.Sprintf("%s/%s revision=%s","lesson","1.0","abc123");check(label=="lesson/1.0 revision=abc123","version")""",
            "Version metadata connects an artifact with source provenance. It should not contain a developer host path or private identity.",
        ),
    ],
    imports="runtime",
    helper="type ServiceState struct{Accepting bool;Active int}",
    source="https://go.dev/doc/install/source#environment",
    boundary="The pad compiles and executes one file in Linux Docker. Real container-build and OS-signal exercises belong in the Docker module or an explicitly prepared project. The pad does not receive an engine socket, arbitrary process arguments or cgo support.",
)

add(
    "Kubernetes objects, metadata, spec and status",
    """Kubernetes exposes typed API resources through a declarative control plane. An object has an identity and metadata, desired configuration in spec, and observed information in status. A controller does not assume a successful API write means the requested real-world state already exists. metadata.uid distinguishes an object incarnation from a later object reusing the same name. generation tracks desired-state changes for resources that support that convention, while resourceVersion supports concurrency and watch semantics. Treat resourceVersion as opaque. This lesson decodes synthetic Deployment-shaped JSON to make these distinctions concrete without using credentials or contacting a cluster.""",
    """apiVersion identifies the API group and version; kind identifies an object kind. metadata.namespace plus name locates a namespaced object, while uid identifies its incarnation. Spec and status should have separate Go fields and responsibilities. Pointer fields can distinguish an omitted desired value from an explicit zero. JSON tags bind the Go representation to wire names. A struct here models only the selected fields and is not the full generated Kubernetes API type.""",
    [
        ("Desired state", "The configuration requested by a user or controller."),
        ("Observed state", "The state last reported by a controller."),
        ("Object UID", "A unique identity for one object incarnation."),
    ],
    [
        E(
            "Decode desired and observed replicas",
            "Decode a fixture requesting 3 replicas with 2 ready.",
            "Desired is 3 while ready is 2.",
            r"""var d Deployment;err:=json.Unmarshal([]byte(`{"apiVersion":"apps/v1","kind":"Deployment","metadata":{"name":"demo","namespace":"lesson","uid":"u1"},"spec":{"replicas":3},"status":{"readyReplicas":2}}`),&d);check(err==nil&&d.Spec.Replicas!=nil&&*d.Spec.Replicas==3&&d.Status.Ready==2,"spec status")""",
            "The accepted object and the observed rollout are different evidence. A controller must reconcile the gap.",
        ),
        E(
            "Distinguish omitted from explicit zero",
            "Decode one absent replicas field and one replicas zero.",
            "Only the explicit zero has a non-nil pointer.",
            r"""var a,b Deployment;check(json.Unmarshal([]byte(`{"spec":{}}`),&a)==nil,"decode");check(json.Unmarshal([]byte(`{"spec":{"replicas":0}}`),&b)==nil,"decode");check(a.Spec.Replicas==nil&&b.Spec.Replicas!=nil&&*b.Spec.Replicas==0,"presence")""",
            "Defaulting and an intentional scale-to-zero request have different meanings. A plain integer field would lose that distinction before validation.",
        ),
        E(
            "Separate name and incarnation",
            "Construct two objects sharing name but having different UIDs.",
            "Their names match but identities differ.",
            r"""a:=Metadata{Name:"demo",Namespace:"lesson",UID:"old"};b:=Metadata{Name:"demo",Namespace:"lesson",UID:"new"};check(a.Name==b.Name&&a.UID!=b.UID,"incarnation")""",
            "Cleanup based only on name can delete a replacement object that the operation never owned.",
        ),
        E(
            "Keep namespaces in a key",
            "Build keys for the same name in two namespaces.",
            "The keys are different.",
            r"""a,b:="alpha/demo","beta/demo";check(a!=b,"namespace key")""",
            "Names are unique within a namespaced resource scope, not across the whole cluster.",
        ),
        E(
            "Treat versions as opaque",
            "Store a nonnumeric resourceVersion token and compare it for equality.",
            "The exact token is retained.",
            r"""m:=Metadata{Version:"opaque-v7"};check(m.Version=="opaque-v7","opaque version")""",
            "Do not increment, subtract or numerically order resourceVersion. Its supported meaning is defined by API operations.",
        ),
        E(
            "Transfer readiness reasoning",
            "Compare desired 3 with ready 3 and then ready 2.",
            "Only the equal complete state satisfies this simplified predicate.",
            r"""wanted:=3;check(wanted==3&&3==wanted,"ready");check(2!=wanted,"not ready")""",
            "A real Deployment readiness check also considers generation and conditions. This count comparison is only one part of that contract.",
        ),
    ],
    imports="encoding/json",
    helper="""type Metadata struct{Name string `json:"name"`;Namespace string `json:"namespace"`;UID string `json:"uid"`;Version string `json:"resourceVersion"`}
type Deployment struct{APIVersion string `json:"apiVersion"`;Kind string `json:"kind"`;Metadata Metadata `json:"metadata"`;Spec struct{Replicas *int `json:"replicas"`} `json:"spec"`;Status struct{Ready int `json:"readyReplicas"`} `json:"status"`}""",
    source="https://kubernetes.io/docs/concepts/overview/working-with-objects/kubernetes-objects/",
    boundary="This is an offline wire-format model. It neither imports client-go nor proves cluster behavior. Use the owned Kubernetes classroom for live resources; never point a Go lesson at an ambient kubeconfig.",
)

add(
    "Labels, selectors and service membership",
    """Labels attach identity and grouping information to objects. A selector expresses a membership rule, not an ownership proof. A Service selects matching Pods and exposes a stable service abstraction while actual endpoints change. Pods with the same labels can still belong to different controllers, and a broad selector can unintentionally combine workloads. Namespace scope, readiness and EndpointSlice state also affect usable service endpoints. This lesson models equality selectors and readiness filtering with tiny records. It does not emulate kube-proxy, DNS or packet routing; those mechanisms are taught and exercised in the Kubernetes networking path.""",
    """A map of required label pairs represents an AND of equality tests in this small model. Missing and empty-valued labels must be distinguished with comma-ok. Kubernetes additionally supports set-based selectors and API-specific selector forms. Stable application identity should be separate from rollout-specific labels when a Service must survive Deployment replacement. Never use label matching alone as permission to delete an object.""",
    [
        ("Label", "A key/value pair used to organize and select objects."),
        ("Selector", "A predicate identifying matching objects."),
        ("Endpoint readiness", "Whether a selected backend is eligible to serve traffic."),
    ],
    [
        E(
            "Match all required labels",
            "Match app=web and tier=frontend against a Pod containing both.",
            "The selector matches.",
            r"""check(matches(map[string]string{"app":"web","tier":"frontend"},map[string]string{"app":"web","tier":"frontend"}),"match")""",
            "All selector pairs must match. Treating the requirements as OR would admit unintended workloads.",
        ),
        E(
            "Reject a missing label",
            "Require tier when the Pod has only app.",
            "The selector does not match.",
            r"""check(!matches(map[string]string{"app":"web"},map[string]string{"app":"web","tier":"frontend"}),"missing")""",
            "A missing required key is not a wildcard. Presence is part of the equality contract.",
        ),
        E(
            "Distinguish empty value from absence",
            "Require a present empty-valued label.",
            "A present empty label matches; absence does not.",
            r"""check(matches(map[string]string{"flag":""},map[string]string{"flag":""}),"empty present");check(!matches(map[string]string{},map[string]string{"flag":""}),"empty absent")""",
            "Reading only the map zero value would collapse absence into empty text and incorrectly match the second case.",
        ),
        E(
            "Filter readiness separately",
            "Select two matching Pods but admit only the ready one as usable.",
            "Exactly one usable backend remains.",
            r"""pods:=[]PodView{{Labels:map[string]string{"app":"web"},Ready:true},{Labels:map[string]string{"app":"web"},Ready:false}};count:=0;for _,p:=range pods{if matches(p.Labels,map[string]string{"app":"web"})&&p.Ready{count++}};check(count==1,"ready backends")""",
            "Selection and readiness answer different questions. An object can belong to the workload without being eligible for traffic.",
        ),
        E(
            "Inspect an overly broad selector",
            "Use an empty equality selector against two unrelated labels.",
            "Both match this mathematical predicate.",
            r"""check(matches(map[string]string{"app":"web"},nil)&&matches(map[string]string{"app":"db"},nil),"broad selector")""",
            "This local predicate treats an empty conjunction as true. Real API semantics vary by resource and field, so consult the relevant API before using an empty selector.",
        ),
        E(
            "Transfer rollout-stable identity",
            "Match app=web across two different rollout labels.",
            "Both versions match the stable app selector.",
            r"""selector:=map[string]string{"app":"web"};check(matches(map[string]string{"app":"web","revision":"a"},selector)&&matches(map[string]string{"app":"web","revision":"b"},selector),"rollout selector")""",
            "The stable selector allows replacement backends. Whether both should receive traffic depends on rollout and readiness policy, not just matching labels.",
        ),
    ],
    helper="""type PodView struct{Labels map[string]string;Ready bool}
func matches(labels,selector map[string]string)bool{for k,want:=range selector{got,ok:=labels[k];if !ok||got!=want{return false}};return true}""",
    source="https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/",
)

add(
    "Reconciliation as an idempotent control loop",
    """A controller repeatedly compares desired and observed state and takes a bounded step toward convergence. Reconciliation is level-based: it should ask what is true now rather than assume it received every historical event. Events are hints that work may be needed, not an exactly-once command log. A successful reconcile can be a no-op when the object already satisfies intent. Repeating it should not create duplicate side effects. Separate a pure decision function from the API adapter so planning can be tested deterministically. External operations need ownership, idempotency keys and explicit handling of uncertain outcomes.""",
    """Represent desired and observed state as small values, then return a typed action such as create, update or none. Avoid embedding API calls inside every conditional. The adapter performs an action, records evidence and schedules another observation. A real controller often converges over several reconciliations rather than blocking until every resource becomes ready. Status should describe observed facts, including the generation to which they apply.""",
    [
        ("Reconciliation", "Repeatedly moving observed state toward desired state."),
        (
            "Idempotence",
            "Repeating an operation has the same intended effect as performing it once.",
        ),
        ("Convergence", "Approaching a stable state satisfying declared intent."),
    ],
    [
        E(
            "Plan a missing child",
            "Observe no child for a desired replica count of 3.",
            "The action is create.",
            r"""check(plan(3,false,0)=="create","missing child")""",
            "The planner reports intent without performing a cluster mutation. The adapter still needs an exact owner identity.",
        ),
        E(
            "Plan a changed child",
            "Observe an existing child with count 2 while desired is 3.",
            "The action is update.",
            r"""check(plan(3,true,2)=="update","changed child")""",
            "The update is justified by a current difference, not by assuming a prior event was delivered once.",
        ),
        E(
            "Make convergence a no-op",
            "Observe an existing child already at count 3.",
            "The action is none.",
            r"""check(plan(3,true,3)=="none","converged")""",
            "A repeated event should not produce duplicate writes after convergence. No-op behavior also reduces control-plane load.",
        ),
        E(
            "Reject invalid desired state",
            "Supply a negative desired count.",
            "The planner returns invalid.",
            r"""check(plan(-1,true,2)=="invalid","invalid intent")""",
            "A persistent validation error should be surfaced to the user rather than retried forever as if it were a transient API outage.",
        ),
        E(
            "Simulate a converging step",
            "Start at count 1, apply the planned update to 3 and plan again.",
            "The next plan is none.",
            r"""current:=1;check(plan(3,true,current)=="update","first plan");current=3;check(plan(3,true,current)=="none","second plan")""",
            "The state transition shows convergence for this simple model. Distributed delays and conflicts belong to adapter-level integration tests.",
        ),
        E(
            "Transfer scale-to-zero",
            "Request zero for an existing child with count 2.",
            "The planner requests update, then converges at zero.",
            r"""check(plan(0,true,2)=="update"&&plan(0,true,0)=="none","zero scale")""",
            "Zero can be a valid desired value. Confusing it with absence would prevent a legitimate scale-to-zero operation.",
        ),
    ],
    helper='func plan(wanted int,exists bool,current int)string{if wanted<0{return "invalid"};if !exists{return "create"};if wanted!=current{return "update"};return "none"}',
    source="https://kubernetes.io/docs/concepts/architecture/controller/",
)

add(
    "Resource versions and optimistic concurrency",
    """Optimistic concurrency protects a write from silently overwriting a newer observation. A client reads an object with resourceVersion, prepares a change and submits the version it observed. If another writer changed the object, the API can reject the stale write with a conflict. The correct response is usually to reread current state, recompute the intended change and retry within a budget. Retrying the identical stale object cannot resolve the conflict. Resource versions are opaque tokens, not counters for client arithmetic. Server-side apply and patch operations have additional field-management contracts that should not be confused with unrestricted last-writer-wins replacement.""",
    """This fixture represents an object as value plus opaque version. update requires equality with the observed token and returns a new server-selected token. A conflict is a typed outcome distinct from invalid input or access denial. Recompute from the new read rather than blindly replacing fields owned by another controller. Keep retries bounded and preserve context cancellation.""",
    [
        ("Optimistic concurrency", "Rejecting a write when its observed version is stale."),
        ("Conflict", "Evidence that another state change invalidated a write assumption."),
        ("Field ownership", "Responsibility for a particular part of a shared object."),
    ],
    [
        E(
            "Accept a current version",
            "Update value 2 using its current token a.",
            "The value changes and token becomes b.",
            r"""s:=Versioned{Value:2,Version:"a"};err:=versionUpdate(&s,"a",3,"b");check(err==nil&&s.Value==3&&s.Version=="b","current update")""",
            "The new token is selected by the simulated server. A real client must not construct the next resourceVersion itself.",
        ),
        E(
            "Reject a stale version",
            "Attempt a write with old token a against current token b.",
            "Conflict is returned and value stays unchanged.",
            r"""s:=Versioned{Value:3,Version:"b"};err:=versionUpdate(&s,"a",9,"c");check(errors.Is(err,ErrConflict)&&s.Value==3,"conflict")""",
            "The failed write does not overwrite newer state. The error is useful evidence about the caller assumption.",
        ),
        E(
            "Reread before retry",
            "Read the current token after conflict and recompute an increment.",
            "The new value is based on current state.",
            r"""s:=Versioned{Value:4,Version:"b"};observed:=s;check(versionUpdate(&s,observed.Version,observed.Value+1,"c")==nil&&s.Value==5,"reread")""",
            "Recomputation preserves the intervening change. Replaying an old absolute value could erase it.",
        ),
        E(
            "Keep opaque tokens opaque",
            "Use token rv:opaque rather than an integer.",
            "Equality-based update succeeds.",
            r"""s:=Versioned{Value:1,Version:"rv:opaque"};check(versionUpdate(&s,"rv:opaque",2,"next:opaque")==nil,"opaque")""",
            "No parsing or arithmetic is needed. Treating tokens as numbers would add an unsupported assumption.",
        ),
        E(
            "Retain another field",
            "Change one scalar while keeping a separate owner label.",
            "The unrelated label is unchanged.",
            r"""labels:=map[string]string{"owner":"other"};s:=Versioned{Value:1,Version:"x"};check(versionUpdate(&s,"x",2,"y")==nil&&labels["owner"]=="other","field scope")""",
            "Real patches and apply operations should be scoped to fields the controller owns. This fixture makes that responsibility explicit without emulating field management.",
        ),
        E(
            "Transfer bounded conflict handling",
            "Try the same stale token twice and count conflicts.",
            "Both attempts conflict and neither changes state.",
            r"""s:=Versioned{Value:3,Version:"new"};conflicts:=0;for i:=0;i<2;i++{if errors.Is(versionUpdate(&s,"old",9,"unused"),ErrConflict){conflicts++}};check(conflicts==2&&s.Value==3,"stale retries")""",
            "The counterexample explains why automatic retry must reread. More attempts with the same invalid assumption do not create progress.",
        ),
    ],
    imports="errors",
    helper="""var ErrConflict=errors.New("conflict")
type Versioned struct{Value int;Version string}
func versionUpdate(s *Versioned,observed string,value int,next string)error{if s.Version!=observed{return ErrConflict};s.Value=value;s.Version=next;return nil}""",
    source="https://kubernetes.io/docs/reference/using-api/api-concepts/#resource-versions",
)

add(
    "List-watch continuity, bookmarks and expired history",
    """A watch streams changes after a chosen observation point, but it is not an infinite durable event log. A controller normally obtains a list snapshot and continues from its resourceVersion so the initial state and later events connect coherently. Connections end, history can expire, and clients must recover by relisting when the server cannot continue from an old version. Bookmarks can advance the known position without carrying an ordinary object mutation; they are not guaranteed periodic heartbeats. Treat events as prompts to reconcile current state. Never assume every intermediate transition is delivered exactly once or that a disconnected watch proves no changes occurred.""",
    """This offline reducer handles ADDED, MODIFIED, DELETED, BOOKMARK and an explicit expired-history signal. Ordinary events update a keyed cache; bookmarks only advance the token. Expiration invalidates continuity and requires a fresh list rather than fabricated incremental recovery. The real API uses Status errors and HTTP responses whose interpretation belongs to client-go or a carefully reviewed client.""",
    [
        ("List snapshot", "A collection observed at a defined API version point."),
        ("Watch bookmark", "A progress marker without an ordinary object update."),
        ("Expired history", "A watch position the server can no longer continue."),
    ],
    [
        E(
            "Apply an added object",
            "Apply ADDED for demo with value 2.",
            "The cache gains demo=2.",
            r"""s:=newWatch();check(applyWatch(&s,WatchEvent{Kind:"ADDED",Key:"demo",Value:2,Version:"a"})==nil&&s.Items["demo"]==2,"add")""",
            "The key identifies current state. Reconciliation should inspect that state rather than treat addition as an irreversible once-only command.",
        ),
        E(
            "Apply a modification",
            "Add then modify the same key.",
            "The cached value becomes 3.",
            r"""s:=newWatch();_ = applyWatch(&s,WatchEvent{Kind:"ADDED",Key:"demo",Value:2,Version:"a"});check(applyWatch(&s,WatchEvent{Kind:"MODIFIED",Key:"demo",Value:3,Version:"b"})==nil&&s.Items["demo"]==3,"modify")""",
            "The newest observed value replaces the prior value for this simplified cache. A production informer also manages resource typing and synchronization.",
        ),
        E(
            "Advance a bookmark",
            "Apply a bookmark without an object.",
            "The version advances and no item is created.",
            r"""s:=newWatch();check(applyWatch(&s,WatchEvent{Kind:"BOOKMARK",Version:"b"})==nil&&s.Version=="b"&&len(s.Items)==0,"bookmark")""",
            "A bookmark supplies continuity information, not an object named by an empty key.",
        ),
        E(
            "Invalidate expired continuity",
            "Apply an expired-history signal.",
            "The state requests a relist.",
            r"""s:=newWatch();err:=applyWatch(&s,WatchEvent{Kind:"EXPIRED"});check(err!=nil&&s.NeedsList,"expiry")""",
            "Continuing from an unavailable position can miss state changes. A fresh list reestablishes the baseline.",
        ),
        E(
            "Delete current membership",
            "Delete an existing key and then delete it again.",
            "The cache remains empty.",
            r"""s:=newWatch();s.Items["demo"]=2;_ = applyWatch(&s,WatchEvent{Kind:"DELETED",Key:"demo",Version:"c"});_ = applyWatch(&s,WatchEvent{Kind:"DELETED",Key:"demo",Version:"d"});check(len(s.Items)==0,"delete")""",
            "Idempotent removal tolerates repeated signals. Real cleanup still requires exact UID ownership before external deletion.",
        ),
        E(
            "Transfer unknown-event refusal",
            "Apply an unsupported event kind.",
            "An error is returned without accepting invented semantics.",
            r"""s:=newWatch();check(applyWatch(&s,WatchEvent{Kind:"MYSTERY"})!=nil,"unknown")""",
            "Unknown protocol data should not silently mutate the cache. Preserve diagnostic evidence and recover under an explicit policy.",
        ),
    ],
    imports="errors",
    helper="""type WatchEvent struct{Kind,Key,Version string;Value int}
type WatchState struct{Items map[string]int;Version string;NeedsList bool}
func newWatch()WatchState{return WatchState{Items:map[string]int{}}}
func applyWatch(s *WatchState,e WatchEvent)error{switch e.Kind{case "ADDED","MODIFIED":s.Items[e.Key]=e.Value;case "DELETED":delete(s.Items,e.Key);case "BOOKMARK":case "EXPIRED":s.NeedsList=true;return errors.New("relist required");default:return errors.New("unknown event")};s.Version=e.Version;return nil}""",
    source="https://kubernetes.io/docs/reference/using-api/api-concepts/#efficient-detection-of-changes",
)

add(
    "Work queues, retry budgets and error classification",
    """A controller queue decouples event ingestion from reconciliation. Repeated events for one key can be coalesced because reconciliation reads the latest state. A failing key should not spin in a tight loop or prevent unrelated keys from progressing. Rate-limited retry combines an increasing delay with a cap and often jitter; cancellation and a maximum work policy prevent unlimited resource use. Permanent invalid input differs from a transient API failure. Success should clear retry history so an old failure does not penalize a repaired object forever. This lesson models scheduling decisions without sleeping or claiming a full implementation of client-go workqueue semantics.""",
    """A queue key usually names a namespace and object name, not a pointer to a stale object. The worker gets a key, defers Done, reconciles and either Forget on success or schedules a rate-limited retry. The fixture uses integer delay units to test a capped exponential policy deterministically. Production jitter should be tested with an injected source rather than a fixed assumption about wall-clock timing.""",
    [
        ("Coalescing", "Combining repeated notifications for the same work key."),
        ("Backoff", "Increasing delay after repeated transient failures."),
        ("Retry budget", "A bound on attempts or elapsed work."),
    ],
    [
        E(
            "Calculate increasing delay",
            "Inspect attempts 0, 1 and 2.",
            "The delays are 1, 2 and 4 units.",
            r"""check(delay(0)==1&&delay(1)==2&&delay(2)==4,"growth")""",
            "The first attempt and retry numbering must be documented. Ambiguous numbering creates off-by-one operational behavior.",
        ),
        E(
            "Cap the delay",
            "Inspect attempts beyond the configured cap.",
            "The delay never exceeds 8 units.",
            r"""check(delay(3)==8&&delay(10)==8,"cap")""",
            "A cap prevents exponential growth from becoming impractical or overflowing. It does not replace a total retry budget.",
        ),
        E(
            "Coalesce duplicate keys",
            "Enqueue alpha twice and beta once in a set model.",
            "There are two pending identities.",
            r"""pending:=map[string]bool{};for _,key:=range []string{"alpha","alpha","beta"}{pending[key]=true};check(len(pending)==2,"coalesce")""",
            "This model demonstrates identity coalescing only. A real workqueue also handles dirty keys that change while already processing.",
        ),
        E(
            "Separate invalid from transient",
            "Classify a validation failure and a timeout-like failure.",
            "Only the transient class is retried.",
            r"""check(!retryable("invalid")&&retryable("transient"),"classification")""",
            "Blindly retrying invalid desired state wastes resources and delays useful feedback to the user.",
        ),
        E(
            "Reset successful history",
            "Clear a key after successful reconciliation.",
            "Its next failure starts at the first delay.",
            r"""attempts:=map[string]int{"demo":3};delete(attempts,"demo");check(delay(attempts["demo"])==1,"reset")""",
            "Success ends the current failure sequence. Retaining stale backoff can make a later unrelated event appear inexplicably slow.",
        ),
        E(
            "Transfer a total budget",
            "Allow at most three attempts and count admitted retries.",
            "Exactly three attempts are admitted.",
            r"""admitted:=0;for attempt:=0;attempt<5;attempt++{if attempt<3{admitted++}};check(admitted==3,"budget")""",
            "A delay cap bounds waiting per retry, while an attempt or elapsed-time budget bounds total work. Both are separate policies.",
        ),
    ],
    helper="""func delay(attempt int)int{if attempt<0{return 1};if attempt>=3{return 8};return 1<<attempt}
func retryable(class string)bool{return class=="transient"}""",
    source="https://pkg.go.dev/k8s.io/client-go/util/workqueue",
)

add(
    "A real client-go project and explicit cluster configuration",
    """client-go provides typed Kubernetes clients, discovery, watches, caches and work queues. It is a dependency project, not part of the Go standard library. Keep k8s.io/api, apimachinery and client-go on compatible release lines and review the documented compatibility matrix for the target cluster. Configuration carries authority: a kubeconfig can name a cluster, credentials and executable authentication plugins. Do not discover an ambient configuration for a teaching program that is supposed to use a disposable target. The ordinary pad below validates a deliberately constrained connection description and constructs a request without sending it. A separately prepared project fixture shows the actual typed client and explicit-context loading.""",
    """The prepared project uses clientcmd loading rules with one explicit kubeconfig path and a named context override, then kubernetes.NewForConfig. CoreV1().Pods(namespace).List(ctx, metav1.ListOptions{Limit:...}) invokes a typed resource client. Context and request timeout bound work; pagination must be handled rather than assuming one list is complete. The project is read-only and still requires exact disposable target identification, minimal RBAC and deliberate execution.""",
    [
        ("Clientset", "Typed clients for Kubernetes API resource groups."),
        ("Kubeconfig context", "A named selection of cluster, identity and namespace."),
        (
            "Dependency pin",
            "An explicit reviewed module version rather than an implicit latest version.",
        ),
    ],
    [
        E(
            "Accept explicit secure configuration",
            "Validate an HTTPS endpoint, lesson namespace and explicit context name.",
            "The configuration is accepted.",
            r"""check(validateTarget("https://cluster.invalid:6443","lesson","owned-lesson")==nil,"target")""",
            "The hostname is a nonresolving fixture and no request is sent. Real target ownership requires stronger runtime evidence than these syntax checks.",
        ),
        E(
            "Reject insecure transport",
            "Validate an HTTP endpoint.",
            "The configuration is rejected.",
            r"""check(validateTarget("http://cluster.invalid","lesson","owned-lesson")!=nil,"TLS")""",
            "TLS policy protects transport identity. Disabling certificate verification is not a reasonable response to a configuration error.",
        ),
        E(
            "Reject ambient context selection",
            "Omit the context name.",
            "Validation rejects the configuration.",
            r"""check(validateTarget("https://cluster.invalid","lesson","")!=nil,"explicit context")""",
            "An explicit context prevents silently inheriting whichever cluster happens to be current in a developer configuration.",
        ),
        E(
            "Constrain a namespace",
            "Attempt a namespace containing a slash.",
            "Validation rejects it.",
            r"""check(validateTarget("https://cluster.invalid","lesson/other","owned")!=nil,"namespace")""",
            "This small validator is deliberately conservative. Real Kubernetes names have a documented grammar and should use the appropriate library validation.",
        ),
        E(
            "Construct a bounded request",
            "Build an HTTPS list request with a live context without sending it.",
            "The method and URL path are correct.",
            r"""req,err:=http.NewRequestWithContext(context.Background(),"GET","https://cluster.invalid/api/v1/namespaces/lesson/pods?limit=20",nil);check(err==nil&&req.Method=="GET"&&req.URL.Path=="/api/v1/namespaces/lesson/pods","request")""",
            "Constructing a request proves neither authentication nor authorization nor API availability. It is useful local boundary evidence only.",
        ),
        E(
            "Transfer userinfo rejection",
            "Reject an endpoint embedding userinfo.",
            "The embedded credential form is rejected.",
            r"""target := url.URL{Scheme: "https", Host: "cluster.invalid", User: url.UserPassword("sample-user", "sample-value")}; check(validateTarget(target.String(),"lesson","owned")!=nil,"userinfo")""",
            "Credentials should not be hidden in endpoint strings that might be logged. The real client handles credentials through an explicit reviewed configuration path.",
        ),
    ],
    imports="net/url net/http context strings errors",
    helper="""func validateTarget(endpoint,namespace,contextName string)error{u,err:=url.Parse(endpoint);if err!=nil||u.Scheme!="https"||u.Host==""||u.User!=nil{return errors.New("explicit HTTPS endpoint required")};if namespace==""||strings.ContainsAny(namespace,"/\\\\ ")||contextName==""{return errors.New("explicit namespace and context required")};return nil}""",
    source="https://github.com/kubernetes/client-go",
    boundary="The separately prepared project lives in courses/go/fixtures/client-go-project/. Its README explains dependency preparation and explicit cluster selection. It is not executed by the ordinary single-source pad and does not inherit any classroom cluster credentials. Never run it against an unrelated current context.",
)

add(
    "Informer caches, stale reads and safe object copies",
    """An informer maintains a local view of API objects and supplies events that can enqueue reconciliation. Its cache improves efficiency but is eventually consistent: a successful write may not be visible in the cache immediately. Wait for initial cache synchronization before relying on its contents. Objects returned from shared caches must be treated as read-only. Mutating them in place can corrupt observations for other consumers without making any API change. DeepCopy before constructing an update, and use the API response or a fresh read when a particular consistency requirement demands it. A cache miss is evidence about that view, not always proof of server-side absence.""",
    """An informer factory starts shared controllers; WaitForCacheSync confirms initial synchronization or cancellation. Listers read cached objects. The fixture models a cache map and a defensive copy of nested labels. Copying only the outer struct still aliases its map. Event handlers should enqueue keys quickly instead of blocking on long reconciliation or retaining stale object pointers as authoritative state.""",
    [
        ("Informer", "A component maintaining a local watch-backed object cache."),
        ("Eventual consistency", "A view that can lag a completed remote update."),
        ("Deep copy", "A copy that separates mutable nested storage."),
    ],
    [
        E(
            "Copy before changing labels",
            "Copy a cached object and change its app label.",
            "The cache still contains the original label.",
            r"""cached:=Cached{Labels:map[string]string{"app":"web"},Version:"a"};copy:=copyCached(cached);copy.Labels["app"]="api";check(cached.Labels["app"]=="web"&&copy.Labels["app"]=="api","copy")""",
            "The copy duplicates the map as well as the struct. An outer assignment alone would still share mutable labels.",
        ),
        E(
            "Expose a shallow-copy defect safely",
            "Assign a struct containing a map and mutate the assigned map sequentially.",
            "The original observes the unintended change.",
            r"""cached:=Cached{Labels:map[string]string{"app":"web"}};shallow:=cached;shallow.Labels["app"]="bad";check(cached.Labels["app"]=="bad","shallow counterexample")""",
            "This is a deterministic sequential demonstration of aliasing. The real cache rule forbids such mutation, especially across concurrent consumers.",
        ),
        E(
            "Represent a stale view",
            "Keep cache version a while a server model has version b.",
            "The versions differ without implying a failed write.",
            r"""cache:=Cached{Version:"a"};server:=Cached{Version:"b"};check(cache.Version!=server.Version,"stale view")""",
            "A lagging cache and a successful server update can coexist. Immediate reread from the same cache is not a strong write-confirmation test.",
        ),
        E(
            "Gate on initial synchronization",
            "Inspect a false cache-synced flag before processing.",
            "The worker does not claim readiness.",
            r"""synced:=false;ready:=synced;check(!ready,"initial sync")""",
            "A started goroutine is not evidence that its initial list has completed. Production code waits on the actual synchronization function.",
        ),
        E(
            "Queue identities instead of objects",
            "Store a namespace/name key derived from a snapshot.",
            "The key remains usable after the object value changes.",
            r"""key:="lesson/demo";version:="a";version="b";check(key=="lesson/demo"&&version=="b","key identity")""",
            "The next reconciliation obtains current state for the key. Retaining an event object as permanent truth would preserve stale assumptions.",
        ),
        E(
            "Transfer nested-copy independence",
            "Add a new label to a copied object.",
            "The original label count is unchanged.",
            r"""cached:=Cached{Labels:map[string]string{"app":"web"}};copy:=copyCached(cached);copy.Labels["tier"]="frontend";check(len(cached.Labels)==1&&len(copy.Labels)==2,"nested copy")""",
            "Separate nested storage matters for insertion and deletion as well as replacement of an existing value.",
        ),
    ],
    helper="""type Cached struct{Labels map[string]string;Version string}
func copyCached(v Cached)Cached{out:=v;out.Labels=map[string]string{};for k,value:=range v.Labels{out.Labels[k]=value};return out}""",
    source="https://pkg.go.dev/k8s.io/client-go/tools/cache",
)

add(
    "Finalizers, deletion and exact ownership",
    """Deletion can require coordination with an external resource whose lifetime is not handled by Kubernetes garbage collection. A finalizer records that cleanup must complete before the API object is removed. Once deletionTimestamp is set, the controller performs its owned cleanup and removes only its own finalizer after success. Removing the finalizer first can orphan the external resource; retaining it forever can leave an object stuck terminating. Cleanup must be idempotent and identify the exact owned incarnation, not merely a reusable name. Owner references support Kubernetes garbage collection, but they are not a general substitute for finalizing resources outside the cluster.""",
    """A finalizer is a qualified string in metadata.finalizers. The state machine first ensures the finalizer exists during normal operation, then observes deletion, performs bounded cleanup and removes its own entry. Preserve other controllers' entries. An already absent external resource can count as successful cleanup only when the ownership check and absence observation are reliable. Never remove unrelated finalizers as a generic repair shortcut.""",
    [
        ("Finalizer", "A deletion gate requiring a controller to finish cleanup."),
        (
            "Deletion timestamp",
            "Evidence that deletion was requested and finalization may be underway.",
        ),
        ("Owned incarnation", "The exact UID-bound resource created by an operation."),
    ],
    [
        E(
            "Register cleanup responsibility",
            "Inspect a normal object without the controller finalizer.",
            "The next action is add-finalizer.",
            r"""check(finalAction(false,false,false,true)=="add-finalizer","register")""",
            "Register responsibility before creating an external resource that would otherwise be orphaned during deletion.",
        ),
        E(
            "Retain a healthy object",
            "Inspect a nondeleting object whose finalizer is present.",
            "The action is reconcile.",
            r"""check(finalAction(false,true,false,true)=="reconcile","normal")""",
            "A finalizer does not itself request deletion. Normal desired-state work continues while deletion has not begun.",
        ),
        E(
            "Clean before releasing deletion",
            "Inspect a deleting object with outstanding owned cleanup.",
            "The action is cleanup.",
            r"""check(finalAction(true,true,false,true)=="cleanup","cleanup")""",
            "Removing the gate before cleanup succeeds can lose the only durable reminder of the external responsibility.",
        ),
        E(
            "Remove only after success",
            "Inspect a deleting object with confirmed cleanup.",
            "The action is remove-own-finalizer.",
            r"""check(finalAction(true,true,true,true)=="remove-own-finalizer","release")""",
            "Successful cleanup and removal are separate durable steps. Retrying either must tolerate the previous step having already completed.",
        ),
        E(
            "Refuse ownership mismatch",
            "Inspect a resource whose observed UID no longer matches the owned UID.",
            "The action is ownership-error.",
            r"""check(finalAction(true,true,false,false)=="ownership-error","UID mismatch")""",
            "A replacement resource reusing a name is not owned merely because the name is familiar. Do not delete it to force progress.",
        ),
        E(
            "Transfer preservation of other finalizers",
            "Remove only lesson.example/cleanup from two entries.",
            "The unrelated entry remains.",
            r"""values:=[]string{"lesson.example/cleanup","other.example/retain"};out:=[]string{};for _,v:=range values{if v!="lesson.example/cleanup"{out=append(out,v)}};check(len(out)==1&&out[0]=="other.example/retain","preserve others")""",
            "Each controller owns its own finalizer entry. Editing the list must preserve responsibilities belonging to other components.",
        ),
    ],
    helper='func finalAction(deleting,hasFinalizer,cleaned,owned bool)string{if !owned{return "ownership-error"};if !deleting{if !hasFinalizer{return "add-finalizer"};return "reconcile"};if !hasFinalizer{return "done"};if !cleaned{return "cleanup"};return "remove-own-finalizer"}',
    source="https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/",
)

add(
    "Service accounts, RBAC and least-authority controllers",
    """Authentication establishes who is calling; authorization determines which operations that identity may perform. A ServiceAccount gives an in-cluster workload an identity, and RBAC binds subjects to rules over API groups, resources, verbs and sometimes resource names. A Role applies within a namespace; a ClusterRole can describe cluster-scoped permissions or be bound within a namespace. A RoleBinding and ClusterRoleBinding have different scopes. Avoid wildcard grants when a controller only needs a few resource operations. Read access to Secrets is sensitive even though it does not mutate objects. Network reachability and RBAC are separate gates: an allowed identity can still have a broken network path.""",
    """Rules name API resource plurals such as pods, and subresources such as deployments/status. get, list and watch are different verbs. A controller updating status needs the appropriate subresource permission rather than unrestricted object replacement. The fixture checks an explicitly limited rule model; Kubernetes authorization has richer semantics and additive bindings. Validate actual access using the owned cluster and intended identity rather than a privileged developer context.""",
    [
        ("Authentication", "Establishing the identity of a request."),
        ("Authorization", "Deciding whether that identity may perform an operation."),
        ("Least authority", "Granting only the permissions required for a task."),
    ],
    [
        E(
            "Admit a required read",
            "Allow get on pods in the lesson namespace.",
            "The request is admitted by the local rule model.",
            r"""rule:=Rule{Namespace:"lesson",Resource:"pods",Verbs:[]string{"get","list","watch"}};check(allowed(rule,"lesson","pods","get"),"read")""",
            "The rule expresses resource and namespace scope in addition to the verb. Matching only one component would overgrant access.",
        ),
        E(
            "Reject an unneeded mutation",
            "Try delete against the read-only rule.",
            "The request is rejected.",
            r"""rule:=Rule{Namespace:"lesson",Resource:"pods",Verbs:[]string{"get"}};check(!allowed(rule,"lesson","pods","delete"),"mutation")""",
            "A read-oriented controller should not inherit deletion authority merely for convenience.",
        ),
        E(
            "Reject cross-namespace access",
            "Use the lesson rule against another namespace.",
            "The local model rejects it.",
            r"""rule:=Rule{Namespace:"lesson",Resource:"pods",Verbs:[]string{"get"}};check(!allowed(rule,"other","pods","get"),"namespace")""",
            "Namespace boundaries should be explicit. A ClusterRoleBinding can widen scope and therefore deserves separate review.",
        ),
        E(
            "Separate resource and subresource",
            "Grant update on deployments/status but request update on deployments.",
            "The whole-object update is rejected.",
            r"""rule:=Rule{Namespace:"lesson",Resource:"deployments/status",Verbs:[]string{"update"}};check(allowed(rule,"lesson","deployments/status","update")&&!allowed(rule,"lesson","deployments","update"),"subresource")""",
            "Status reporting and desired-state mutation are different authorities. The controller should request only what its design needs.",
        ),
        E(
            "Treat secret reads as authority",
            "Check a pods-only rule against secrets.",
            "Secret read access is rejected.",
            r"""rule:=Rule{Namespace:"lesson",Resource:"pods",Verbs:[]string{"get"}};check(!allowed(rule,"lesson","secrets","get"),"secret boundary")""",
            "Read-only does not mean harmless. Confidential configuration can be exposed without any mutation.",
        ),
        E(
            "Transfer verb distinction",
            "Grant list but not watch and inspect both.",
            "Only list is admitted.",
            r"""rule:=Rule{Namespace:"lesson",Resource:"pods",Verbs:[]string{"list"}};check(allowed(rule,"lesson","pods","list")&&!allowed(rule,"lesson","pods","watch"),"verbs")""",
            "A list request and a long-lived watch have separate permission checks. Controller installation documentation should name both when needed.",
        ),
    ],
    helper="""type Rule struct{Namespace,Resource string;Verbs []string}
func allowed(r Rule,namespace,resource,verb string)bool{if r.Namespace!=namespace||r.Resource!=resource{return false};for _,v:=range r.Verbs{if v==verb{return true}};return false}""",
    source="https://kubernetes.io/docs/reference/access-authn-authz/rbac/",
)

add(
    "Leader election, leases and fencing limits",
    """Several controller replicas improve availability, but some operations need a single active coordinator. Leader election uses a lease-like coordination record so candidates can observe and renew leadership. It is not a magical exactly-once guarantee. A paused process can continue believing it is leader after another process takes over; external side effects may therefore need fencing tokens or idempotency controls at the destination. Time assumptions, renewal deadlines and shutdown behavior matter. The client-go leader-election package explicitly does not provide fencing by itself. This lesson uses a deterministic logical clock to examine lease policy without sleeping or contacting a cluster.""",
    """A lease model records holder and expiry. A current holder can renew, another candidate must wait until expiry, and a candidate must stop leader-only work when renewal is lost. Real lease acquisition requires optimistic concurrency at the API server, not a local map assignment. A monotonically enforced fencing token belongs at the protected external system; Kubernetes resourceVersion should not be repurposed as a numeric application token.""",
    [
        ("Lease", "A time-bounded claim to coordination authority."),
        ("Split brain", "Two participants acting as if each has exclusive authority."),
        ("Fencing", "The destination rejecting operations from an obsolete authority."),
    ],
    [
        E(
            "Acquire an empty lease",
            "Let candidate a acquire at logical time 10 for five units.",
            "Holder becomes a and expiry 15.",
            r"""l:=Lease{};check(acquire(&l,"a",10,5)&&l.Holder=="a"&&l.Expires==15,"acquire")""",
            "This local policy model does not implement distributed atomicity. A real update must be protected by the API concurrency contract.",
        ),
        E(
            "Reject a competing candidate",
            "Let b request an unexpired lease held by a.",
            "The request fails and a remains holder.",
            r"""l:=Lease{Holder:"a",Expires:15};check(!acquire(&l,"b",12,5)&&l.Holder=="a","contender")""",
            "The contender waits while the current claim remains valid under this model.",
        ),
        E(
            "Renew current leadership",
            "Let a renew its lease before expiry.",
            "Expiry advances to 18.",
            r"""l:=Lease{Holder:"a",Expires:15};check(acquire(&l,"a",13,5)&&l.Expires==18,"renew")""",
            "Renewal extends a claim; it does not prove a formerly paused process cannot still perform external work.",
        ),
        E(
            "Take over after expiry",
            "Let b acquire at the exact expiry boundary.",
            "Holder becomes b.",
            r"""l:=Lease{Holder:"a",Expires:15};check(acquire(&l,"b",15,5)&&l.Holder=="b","takeover")""",
            "The boundary policy is explicit. Real clock-skew and API latency assumptions require careful configuration and testing.",
        ),
        E(
            "Reject a stale fenced operation",
            "Compare an old authority token 4 with current token 5.",
            "Only token 5 is accepted by the destination model.",
            r"""current:=5;accept:=func(token int)bool{return token==current};check(!accept(4)&&accept(5),"fencing")""",
            "The protected destination enforces the token. Merely logging that leadership changed does not fence stale work.",
        ),
        E(
            "Transfer invalid-duration refusal",
            "Attempt a lease with a nonpositive duration.",
            "No lease is acquired.",
            r"""l:=Lease{};check(!acquire(&l,"a",10,0)&&l.Holder=="","duration")""",
            "Invalid timing configuration must fail before coordination starts. Silent fallback can create unpredictable failover behavior.",
        ),
    ],
    helper="""type Lease struct{Holder string;Expires int}
func acquire(l *Lease,candidate string,now,duration int)bool{if candidate==""||duration<=0{return false};if l.Holder!=""&&l.Holder!=candidate&&now<l.Expires{return false};l.Holder=candidate;l.Expires=now+duration;return true}""",
    source="https://pkg.go.dev/k8s.io/client-go/tools/leaderelection",
)

add(
    "Admission decisions, webhook contracts and failure policy",
    """Admission evaluates an API request after authentication and authorization and before persistence. Mutating admission can change an object; validating admission can accept or reject it. A webhook introduces a network dependency into control-plane writes, so latency, availability and failurePolicy have real consequences. Fail-open can preserve availability while allowing objects that were not checked; fail-closed can enforce policy while blocking writes during an outage. Choose deliberately and test recovery. AdmissionReview responses must correspond to the request UID and use the supported API version. A validation decision is not permission to perform unrelated side effects, especially for dry-run requests.""",
    """Separate the pure policy from the HTTP and AdmissionReview adapter. The fixture validates a replica range and preserves a synthetic request UID in its decision. A real adapter needs bounded body parsing, TLS, a configured timeout, correct response schema and no hidden external side effects. Rejection messages should identify the field and rule without exposing credentials or excessive source content.""",
    [
        ("Admission", "Policy evaluation before an API object is persisted."),
        ("Failure policy", "Whether a failed policy service permits or blocks the API request."),
        ("Dry run", "A request evaluated without persisting its intended change."),
    ],
    [
        E(
            "Accept a valid range",
            "Validate replica count 3 under maximum 5.",
            "The decision allows the request.",
            r"""d:=admit("r1",3,5,false);check(d.Allowed&&d.UID=="r1","allow")""",
            "The pure rule is independently testable. The HTTP adapter still needs protocol and transport validation.",
        ),
        E(
            "Reject a negative value",
            "Validate replica count -1.",
            "The decision denies it with a reason.",
            r"""d:=admit("r2",-1,5,false);check(!d.Allowed&&d.Reason!="","negative")""",
            "Field-specific validation gives an actionable failure instead of an unexplained generic denial.",
        ),
        E(
            "Check the exact upper boundary",
            "Validate counts 5 and 6 against maximum 5.",
            "Five is allowed and six is denied.",
            r"""check(admit("r3",5,5,false).Allowed&&!admit("r4",6,5,false).Allowed,"boundary")""",
            "The inclusive bound must be clear. Boundary tests catch a common off-by-one policy defect.",
        ),
        E(
            "Preserve request identity",
            "Validate a request and inspect the response UID.",
            "The exact request UID is copied.",
            r"""d:=admit("request-42",2,5,false);check(d.UID=="request-42","UID")""",
            "A response for another request must not be accepted as evidence for this one. Identity binding is part of the webhook protocol.",
        ),
        E(
            "Keep dry-run side effects absent",
            "Evaluate the same policy in dry-run mode.",
            "The decision is computed with zero external effects.",
            r"""d:=admit("r5",2,5,true);check(d.Allowed&&d.SideEffects==0,"dry run")""",
            "This pure validator has no external effects in either mode. Real webhooks must accurately declare and respect their side-effect contract.",
        ),
        E(
            "Transfer missing identity refusal",
            "Evaluate a request lacking its UID.",
            "The decision is denied.",
            r"""d:=admit("",2,5,false);check(!d.Allowed,"missing UID")""",
            "A valid numeric object is insufficient if the adapter cannot bind the response to a request. Protocol validation precedes domain success.",
        ),
    ],
    helper="""type Decision struct{UID string;Allowed bool;Reason string;SideEffects int}
func admit(uid string,replicas,maximum int,dryRun bool)Decision{d:=Decision{UID:uid};if uid==""{d.Reason="request UID required";return d};if replicas<0||replicas>maximum{d.Reason="replicas outside allowed range";return d};d.Allowed=true;return d}""",
    source="https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/",
)

add(
    "Controller tests from pure functions to owned clusters",
    """A controller needs several evidence layers. Pure tests check decision rules quickly. Fake-client tests check requested API interactions and local error handling but may omit server defaulting, validation, resourceVersion conflicts and admission behavior. API-server integration tests add those server contracts. An owned disposable cluster adds controllers, scheduling, networking and real cleanup behavior. Passing a fake test is not interchangeable with a successful rollout. Design fault injection around a specific uncertainty: conflict, cancellation, stale cache, forbidden access or unknown outcome. Keep source hashes, exact object identity and cleanup receipts so the evidence can be traced to the program that actually ran.""",
    """Use a narrow interface at the application boundary and inject a fake with explicit outcomes. Assert both the result and which calls were made. A forbidden error should not trigger an endless retry loop; a cancellation should stop new calls. For live tests, create a unique owned namespace, retain UIDs, bound all waits and verify cleanup without deleting resources identified only by a reusable name. Do not use production contexts as convenient fixtures.""",
    [
        ("Fake client", "An in-process substitute with deliberately limited server semantics."),
        ("Integration evidence", "Observed behavior across real component boundaries."),
        ("Fault injection", "Deliberately producing a specified failure to test recovery."),
    ],
    [
        E(
            "Verify one successful API call",
            "Run a fake client configured to return a value.",
            "The result is retained and exactly one call occurs.",
            r"""f:=&FakeReader{Value:3};v,err:=readOnce(context.Background(),f);check(err==nil&&v==3&&f.Calls==1,"success")""",
            "Call count is evidence about adapter behavior, while the returned value checks the consuming contract.",
        ),
        E(
            "Preserve a forbidden error",
            "Make the fake return ErrForbidden.",
            "The exact cause is visible and only one call occurs.",
            r"""f:=&FakeReader{Err:ErrForbidden};_,err:=readOnce(context.Background(),f);check(errors.Is(err,ErrForbidden)&&f.Calls==1,"forbidden")""",
            "Authorization failure is not repaired by repeating the same request. Surface the required permission or configuration diagnosis.",
        ),
        E(
            "Stop before a canceled call",
            "Cancel context before invoking the adapter.",
            "No API call is made.",
            r"""ctx,cancel:=context.WithCancel(context.Background());cancel();f:=&FakeReader{};_,err:=readOnce(ctx,f);check(errors.Is(err,context.Canceled)&&f.Calls==0,"cancel")""",
            "The test verifies absence of a side effect, not merely the final error text.",
        ),
        E(
            "Distinguish returned zero from failure",
            "Return a successful zero from the fake.",
            "The zero is accepted with nil error.",
            r"""f:=&FakeReader{Value:0};v,err:=readOnce(context.Background(),f);check(err==nil&&v==0,"zero success")""",
            "Result value and operation status are separate channels. A zero cannot stand in for every failure.",
        ),
        E(
            "Retain an unknown failure",
            "Return an unexpected error cause.",
            "The cause remains inspectable.",
            r"""cause:=errors.New("transport outcome unknown");f:=&FakeReader{Err:cause};_,err:=readOnce(context.Background(),f);check(errors.Is(err,cause),"unknown cause")""",
            "Preserving the cause supports diagnosis. A read retry policy differs from replaying a mutation whose outcome is uncertain.",
        ),
        E(
            "Transfer source-bound evidence",
            "Bind a synthetic receipt to its lesson ID and source digest label.",
            "Both identifiers survive comparison.",
            r"""receipt:=map[string]string{"lesson":"go-047","source":"reviewed-fixture"};check(receipt["lesson"]=="go-047"&&receipt["source"]=="reviewed-fixture","receipt identity")""",
            "This small metadata check illustrates binding, not a cryptographic receipt implementation. The classroom records actual source hashes separately.",
        ),
    ],
    imports="context errors",
    helper="""var ErrForbidden=errors.New("forbidden")
type FakeReader struct{Value,Calls int;Err error}
func(f *FakeReader)Read(ctx context.Context)(int,error){f.Calls++;return f.Value,f.Err}
type Reader interface{Read(context.Context)(int,error)}
func readOnce(ctx context.Context,r Reader)(int,error){if err:=ctx.Err();err!=nil{return 0,err};v,err:=r.Read(ctx);if err!=nil{return 0,fmt.Errorf("read object: %w",err)};return v,nil}""",
    source="https://github.com/kubernetes/client-go/tree/master/testing",
)

add(
    "Capstone: a reliable, resumable controller design",
    """The capstone combines desired-state validation, exact identity, idempotent planning, cancellation and durable observations. A controller is successful when repeated observations converge without duplicating effects or damaging resources it does not own. Begin with an explicit state diagram and classify each operation as pure, read-only, idempotent mutation or potentially uncertain external side effect. Record what an operation observed and what it requested, not an invented certainty that the whole system is ready. Production readiness also includes minimal RBAC, bounded queues, useful status, metrics, graceful shutdown and a recovery runbook. This offline capstone proves a small orchestration model; the prepared client-go project and owned Kubernetes module supply the separate real-system learning routes.""",
    """The model stores UID, desired count, current count and a write counter. reconcileCap first checks cancellation, then ownership, then input validity, and finally changes state only when needed. The ordering prevents invalid or unauthorized work from reaching mutation. A real adapter adds optimistic concurrency, API errors, status subresources and cleanup. Preserve these boundaries when replacing the in-memory store rather than moving all logic into one untestable function.""",
    [
        ("Control-loop invariant", "A property preserved across every reconcile attempt."),
        ("Resumability", "Recovering useful work from durable state after interruption."),
        (
            "Operational contract",
            "The documented behavior under startup, failure, recovery and shutdown.",
        ),
    ],
    [
        E(
            "Converge from a different state",
            "Reconcile owned UID u1 from count 1 to desired 3.",
            "The count becomes 3 with one write.",
            r"""s:=CapState{UID:"u1",Current:1};err:=reconcileCap(context.Background(),&s,"u1",3);check(err==nil&&s.Current==3&&s.Writes==1,"converge")""",
            "The mutation is justified by a current difference under a verified identity.",
        ),
        E(
            "Repeat without duplicate writes",
            "Run the same desired state twice.",
            "Only the first call writes.",
            r"""s:=CapState{UID:"u1",Current:1};check(reconcileCap(context.Background(),&s,"u1",3)==nil,"first");check(reconcileCap(context.Background(),&s,"u1",3)==nil&&s.Writes==1,"idempotent")""",
            "Repeated notification is normal. Converged state should remain a no-op.",
        ),
        E(
            "Refuse a replacement object",
            "Supply expected UID old while observed UID is new.",
            "No write occurs and an ownership error is returned.",
            r"""s:=CapState{UID:"new",Current:1};err:=reconcileCap(context.Background(),&s,"old",3);check(err!=nil&&s.Current==1&&s.Writes==0,"ownership")""",
            "A reusable name cannot authorize modification of a replacement incarnation.",
        ),
        E(
            "Preserve state on invalid intent",
            "Request a negative count.",
            "The operation fails without mutation.",
            r"""s:=CapState{UID:"u1",Current:1};err:=reconcileCap(context.Background(),&s,"u1",-1);check(err!=nil&&s.Current==1&&s.Writes==0,"invalid")""",
            "Validation occurs before state changes. A failure-shaped return after mutation would violate the transaction boundary.",
        ),
        E(
            "Cancel before new work",
            "Pass an already-canceled context.",
            "No write occurs and cancellation is retained.",
            r"""ctx,cancel:=context.WithCancel(context.Background());cancel();s:=CapState{UID:"u1",Current:1};err:=reconcileCap(ctx,&s,"u1",3);check(errors.Is(err,context.Canceled)&&s.Writes==0,"cancel")""",
            "The caller retains control of the work lifetime. Later external steps would need their own context-aware boundaries.",
        ),
        E(
            "Transfer restart reasoning",
            "Copy the converged durable state into a new controller invocation.",
            "The restarted invocation makes no additional write.",
            r"""s:=CapState{UID:"u1",Current:3,Writes:1};restored:=s;check(reconcileCap(context.Background(),&restored,"u1",3)==nil&&restored.Writes==1,"restart")""",
            "Recovery reads current durable state rather than replaying an assumed unfinished command. Real persistence and unknown API outcomes require integration evidence beyond this value-copy model.",
        ),
    ],
    imports="context errors",
    helper="""type CapState struct{UID string;Current,Writes int}
func reconcileCap(ctx context.Context,s *CapState,expectedUID string,wanted int)error{if err:=ctx.Err();err!=nil{return err};if s.UID!=expectedUID{return errors.New("ownership mismatch")};if wanted<0{return errors.New("invalid count")};if s.Current!=wanted{s.Current=wanted;s.Writes++};return nil}""",
    source="https://kubernetes.io/docs/concepts/architecture/controller/",
    boundary="For the full project, write a design note containing the desired-state schema, owned child identity, RBAC rules, reconciliation state diagram, status conditions, retry/cancellation policy, finalizer behavior, observability fields and failure-test matrix. Implement the actual API adapter only against an explicitly owned disposable target. The ordinary pad is intentionally the deterministic decision layer, not an autonomous cluster operator.",
)
