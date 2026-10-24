from author import author, hello, BASE
import copy, json, yaml


def save(name, value):
    (BASE / "fixtures" / name).write_text(json.dumps(value, indent=2) + "\n")


cr = {
    "apiVersion": "learning.ds60sqlpy/v1",
    "kind": "LessonReport",
    "metadata": {"name": "hello-report"},
    "spec": {"message": "hello", "replicas": 1},
}
crd = {
    "apiVersion": "apiextensions.k8s.io/v1",
    "kind": "CustomResourceDefinition",
    "metadata": {"name": "lessonreports.learning.ds60sqlpy"},
    "spec": {
        "group": "learning.ds60sqlpy",
        "scope": "Namespaced",
        "names": {"plural": "lessonreports", "singular": "lessonreport", "kind": "LessonReport"},
        "versions": [
            {
                "name": "v1",
                "served": True,
                "storage": True,
                "subresources": {"status": {}},
                "schema": {
                    "openAPIV3Schema": {
                        "type": "object",
                        "required": ["spec"],
                        "properties": {
                            "spec": {
                                "type": "object",
                                "required": ["message", "replicas"],
                                "properties": {
                                    "message": {"type": "string", "enum": ["hello", "reviewer"]},
                                    "replicas": {"type": "integer", "minimum": 1, "maximum": 2},
                                },
                            },
                            "status": {
                                "type": "object",
                                "properties": {
                                    "observedGeneration": {"type": "integer"},
                                    "ready": {"type": "boolean"},
                                    "reason": {"type": "string"},
                                },
                            },
                        },
                    }
                },
            }
        ],
    },
}
save("k8s-029-crd.json", crd)
author(
    29,
    """An API resource is a typed collection of objects, not necessarily a running process. A CustomResourceDefinition, abbreviated CRD, registers a new resource type with the API server. A custom resource is one instance of that type. Here the cluster-scoped registration is lessonreports.learning.ds60sqlpy, while hello-report is a namespaced LessonReport instance. Registering a schema does not install an operator or create a Deployment automatically.

The synthetic API describes a report application with message and replicas. A structural schema gives the server a typed shape it can validate and use for other API machinery. Our spec.message is one of two strings and spec.replicas is an integer from1 through2. These are deliberate course limits, not a generic configuration format. A desired instance can be valid yet remain unimplemented when no qualified controller observes it.

The normal module credential cannot register CRDs or create arbitrary custom resources. The live extension requires a separately provisioned advanced lease. Start by inspecting the complete registration in the linked fixture and the namespaced instance in the solution. Keep API registration, instance acceptance and application convergence as three separate evidence rows.""",
    [
        (
            "Read the registration from outside inward",
            """[The CRD fixture](../fixtures/k8s-029-crd.json) declares group learning.ds60sqlpy, plural lessonreports and kind LessonReport. The fully qualified API version in the instance combines group/version: learning.ds60sqlpy/v1. scope Namespaced means instances belong to a namespace; it does not make the CRD registration itself namespaced.

versions contains one entry with served true and storage true. Served means clients may use that version. Storage selects the representation persisted by the API server. Adding another served version later raises conversion and compatibility questions; changing a string without a migration plan is not an upgrade strategy. This chapter intentionally uses one version.

Under openAPIV3Schema, type object is followed by properties and required fields. Properties describe allowed shapes; required says which values must be present. A field being listed in properties does not by itself make it mandatory. Type validation also distinguishes an integer1 from the string "1". YAML convenience must not erase the API contract.""",
        ),
        (
            "Separate desired state, status and unknown fields",
            """spec records user intent. The status subresource is a separate write boundary for controller observations. Its observedGeneration should identify the spec generation actually reconciled. A learner-written ready:true is not a controller receipt, and a stale status describing an earlier generation cannot establish convergence for the current request.

Unknown-field handling needs an explicit test. Structural schemas can prune fields that are not preserved, and strict server-side field validation can reject unknown fields. Therefore the guaranteed negative controls here use a wrong type or out-of-range value. Do not claim every unknown field is rejected in every client mode. Read back the accepted object and record server behavior for the chosen request mode.

The offline checker only validates this tiny spec subset. It does not implement Kubernetes OpenAPI, admission, defaulting, authorization or conversion. Its purpose is to make the teaching values and boundary cases inspectable before a host-provisioned API test.""",
        ),
        (
            "Diagnose the correct layer",
            """A no-matches-for-kind error suggests registration or discovery/version trouble. Forbidden suggests credentials lack authorization. A schema validation error should name a field and constraint. An accepted instance with no child workload suggests missing or failing reconciliation. Those errors require different repairs.

Do not grant the learner cluster-admin to make the example work. The host owns registration and the lease must provide only the intended namespaced instance operations. Removing a CRD can remove its stored custom resources, so registration cleanup is a separate host responsibility after instance/controller cleanup.""",
        ),
    ],
    [
        (
            "Read a valid instance",
            "```yaml\n" + yaml.safe_dump(cr, sort_keys=False) + "```",
            "A namespaced LessonReport requests message hello and one replica; no Deployment follows from schema registration alone.",
        ),
        (
            "Trace two rejected variants",
            """Keep the same object identity, but first change replicas to the string "2", then to integer3. The first violates type; the second violates maximum. Compare those precise reasons with an unknown field named replcias, whose treatment also depends on field validation and pruning.""",
            "The two guaranteed invalid values fail different schema constraints. An unknown-field experiment must retain its actual rejection or readback behavior.",
        ),
    ],
    [
        (
            "Map the two scopes",
            "Identify the registration object and instance scope from the fixtures.",
            "CRD is cluster-scoped; hello-report is namespaced.",
            "scope applies to custom resource instances.",
            "The registration changes the API surface for the cluster. A namespaced instance is addressed under its own namespace. This difference explains why ordinary worker credentials cannot safely install a CRD as part of a learner submission.",
        ),
        (
            "Trace names and version",
            "Connect group, version, kind, plural and metadata.name.",
            "learning.ds60sqlpy/v1, LessonReport, lessonreports and hello-report are distinct fields.",
            "Plural is a collection name; metadata.name identifies one object.",
            "The mapping determines API discovery and object addressing. A typo in the kind or API version can fail before schema validation, while a different metadata.name creates a different instance rather than changing its type.",
        ),
        (
            "Predict schema negatives",
            "Compare replicas1, string2, integer3 and a missing message.",
            "Only integer1 with a present allowed message passes the stated complete spec.",
            "Check required, type and range separately.",
            "The valid object satisfies every constraint. A numeric-looking string is still the wrong type,3 exceeds maximum2, and absence of message violates required. These produce specific, explainable controls rather than one generic invalid example.",
        ),
        (
            "Inspect unknown-field handling",
            "Use the supplied replcias typo in a qualified server request and readback.",
            "Record validation mode and actual rejection or pruning; do not assume silently stored intent.",
            "Look at the returned object, not only the input file.",
            "Pruning can remove an unknown key while leaving an object that differs from the author intention. Strict validation may reject it instead. Either outcome should be documented, and the offline subset checker cannot establish that server behavior.",
        ),
        (
            "Separate status from intent",
            "Compare spec generation7 with status observedGeneration6 and ready true.",
            "Current generation7 is not yet proven reconciled by that status.",
            "Ask which request the condition describes.",
            "Status may still describe a previously successful configuration. A meaningful readiness gate joins the observed generation with child and application evidence rather than accepting a boolean without its temporal context.",
        ),
        (
            "Plan scoped teardown",
            "List which operations belong to learner instance cleanup and host API-registration cleanup.",
            "Instance UID cleanup is separate from CRD removal; no learner privilege widening.",
            "Deleting a type is broader than deleting one instance.",
            "The advanced lease owner should confirm controller/finalizer completion before deregistering the type. The handoff retains exact object identities and does not use registration deletion as a shortcut to bypass stuck resource cleanup.",
        ),
    ],
    [cr],
    """
def valid(spec):
    return isinstance(spec,dict) and set(spec)=={'message','replicas'} and spec['message'] in ('hello','reviewer') and type(spec['replicas']) is int and 1<=spec['replicas']<=2

def main():
    assert valid({'message':'hello','replicas':1})
    for value in ('2',3,True):assert not valid({'message':'hello','replicas':value})
    assert not valid({'replicas':1})
    assert not valid({'message':'hello','replicas':1,'replcias':2})
    assert 6!=7
    print('k8s-029 strict synthetic subset passed; server pruning and admission are not simulated')

if __name__ == "__main__":
    main()
""",
    capability="host-registered LessonReport CRD and narrowly scoped namespaced instance operations",
    refs=[
        "[Kubernetes custom resources](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/)",
        "[Structural schemas and CRDs](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/)",
    ],
)

author(
    30,
    """An operator combines a custom API with a controller that repeatedly moves observed state toward desired state. Reconciliation is level-driven: the controller reads the current state and decides the next bounded action. Events help schedule work, but they are not a reliable once-only transaction log. The same event can be delivered repeatedly, and a restart can require reconstructing the needed work from objects already present.

For LessonReport, imagine a qualified controller that owns one child Deployment and reports whether its requested message and replica count have converged. The first reconcile may create the child; a later reconcile with the same state should do nothing. A changed spec can update the intended child, but an unrelated child with the same name must not be adopted solely because its name matches.

This chapter supplies an executable pure-Python decision model and real custom-resource input. It does not ship or claim to run a production operator. Live work needs a reviewed, preloaded controller with a documented child contract and namespaced permissions. The model makes ownership, idempotence and status reasoning visible before that operation is available.""",
    [
        (
            "Trace a reconcile decision",
            """Read the parent UID, generation and desired spec. Then read the child. If the child is absent, propose create. If it is present with the expected controller owner UID and desired fields, propose no-op. If owned but different, propose a bounded update. If foreign, stop with a collision condition rather than replacing or deleting it.

Ownership is about identity, not just matching names or labels. A parent deleted and recreated as hello-report has a new UID. A child belonging to the old parent does not automatically belong to the new one. The controller must use owner references and its defined adoption policy, and cleanup must honor the same boundary.

After an update request is accepted, reconciliation is not complete merely because the call returned. The child controller and application must reach the intended state. The operator can requeue and publish an intermediate condition, then report observedGeneration only with a clearly defined meaning and evidence for the corresponding spec.""",
        ),
        (
            "Make retries safe",
            """Idempotence means repeated application of the intended operation does not accumulate unwanted effects. Setting replicas to2 is naturally closer to this property than incrementing replicas on every event. Creating a random new child on every retry would produce duplicates. External side effects need their own idempotency keys or reconciliation receipts; a Kubernetes owner reference cannot make an external payment or file upload exactly once.

A work queue should use bounded retry and backoff for temporary failures. A validation failure usually needs a corrected spec, while an unavailable API may be retried. Tight loops can overload the API and obscure the original error. Observe attempt count, last reason and next retry rather than assuming every repeated reconciliation is a defect.

A finalizer is a deletion handshake. Once deletionTimestamp is set, a controller with its finalizer performs its specific cleanup and removes only its own finalizer when that obligation is complete. Removing all finalizers to make deletion disappear can orphan external resources or bypass another controller's work.""",
        ),
        (
            "Avoid fake convergence",
            """A status field supplied by the learner or copied from a synthetic trace is not a live controller observation. A child Ready condition with an old observed generation is insufficient for a changed message. Compare parent generation, intended child fields, owned identities and application output.

Do not debug a stuck finalizer by indiscriminately clearing metadata.finalizers. Identify the responsible controller, its cleanup contract and the missing evidence. If the required controller is not provisioned, label the live activity unavailable rather than impersonating it with a sequence of manual creates.""",
        ),
    ],
    [
        (
            "Replay duplicate events",
            """Synthetic parent UID p1 requests replicas1. Read1 finds no child: create. Read2 finds child owned by p1 with replicas1: no-op. Read3 repeats the same event and same state: no-op. Only one child identity exists.""",
            "The trace is create,no-op,no-op. Duplicate scheduling does not justify duplicate children.",
        ),
        (
            "Reject a collision and handle deletion",
            """A child called hello exists with controller owner p2 while the current parent UID is p1. The decision is refuse, even if replicas match. Separately, a deleting p1 with finalizers [lesson.cleanup,other.cleanup] may remove lesson.cleanup only after its own cleanup succeeds.""",
            "Foreign ownership blocks mutation. Successful own cleanup leaves other.cleanup intact.",
        ),
    ],
    [
        (
            "Build the state table",
            "Classify absent, owned-equal, owned-different and foreign child states.",
            "create, no-op, update and refuse respectively.",
            "Compare identity before configuration.",
            "The table separates an allowed convergence action from a collision. Choosing update based only on a name would mutate a resource outside the parent ownership graph, even if the desired spec seems harmless.",
        ),
        (
            "Replay repeated reconciliation",
            "Apply the same desired state three times in the synthetic model.",
            "One create followed by two no-ops, with one child.",
            "Read current state after each step.",
            "A level-driven controller reconstructs the result from state. It does not need the event stream to prove which event was first. The stable child identity is evidence against a create-on-every-event bug.",
        ),
        (
            "Change desired replicas",
            "Move the owned desired count from1 to2 and inspect the next two decisions.",
            "update then no-op after observed state matches.",
            "An update request and eventual convergence are separate phases.",
            "The model demonstrates decision idempotence only. A live controller still needs to wait for Deployment observation, readiness and any required application gate before recording a successful changed generation.",
        ),
        (
            "Test replacement identity",
            "Replace the parent name with a new UID while the old child remains.",
            "The old child is foreign to the new parent under this contract.",
            "Names can be reused; UIDs identify lifetimes.",
            "The safe default is a collision report. Adoption would require an explicit separately reviewed policy. Automatic takeover could erase resources belonging to a different operation or a previous partially completed cleanup.",
        ),
        (
            "Review retry and status",
            "Classify temporary API unavailability versus an invalid desired value and stale generation status.",
            "Bounded backoff for transient failure; corrected intent for invalid input; stale readiness does not pass.",
            "Separate recoverable transport failure from unsupported state.",
            "A useful condition carries a reason tied to the current generation and retry state. Repeating a permanently invalid request without feedback wastes capacity, while treating every temporary failure as terminal prevents convergence.",
        ),
        (
            "Complete a finalizer obligation",
            "Remove only lesson.cleanup after synthetic external cleanup succeeds.",
            "other.cleanup remains; failed cleanup retains lesson.cleanup.",
            "A finalizer is a responsibility, not clutter.",
            "The controller must know its obligation completed before removing its marker. A bounded failure should surface the missing action and retain recoverable evidence. Clearing unrelated finalizers is outside this controller ownership.",
        ),
    ],
    [cr],
    """
def decide(parent_uid,desired,child):
    if child is None:return 'create'
    if child['owner_uid']!=parent_uid:return 'refuse'
    return 'no-op' if child['replicas']==desired else 'update'

def finish(finalizers,cleanup_ok):
    return [x for x in finalizers if x!='lesson.cleanup'] if cleanup_ok else list(finalizers)

def main():
    assert decide('p1',1,None)=='create'
    child={'owner_uid':'p1','replicas':1}
    assert [decide('p1',1,child) for _ in range(2)]==['no-op','no-op']
    assert decide('p1',2,child)=='update'
    assert decide('p2',1,child)=='refuse'
    fs=['lesson.cleanup','other.cleanup']
    assert finish(fs,True)==['other.cleanup'] and finish(fs,False)==fs
    print('k8s-030 decision model passed; no controller or external side effect executed')

if __name__ == "__main__":
    main()
""",
    capability="preloaded namespaced controller with reviewed child, status and finalizer contracts",
    refs=[
        "[Kubernetes operator pattern](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/)",
        "[Kubernetes finalizers](https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/)",
    ],
)

policy = {
    "apiVersion": "admissionregistration.k8s.io/v1",
    "kind": "ValidatingAdmissionPolicy",
    "metadata": {"name": "lesson-approved-image"},
    "spec": {
        "failurePolicy": "Fail",
        "matchConstraints": {
            "resourceRules": [
                {
                    "apiGroups": ["apps"],
                    "apiVersions": ["v1"],
                    "operations": ["CREATE", "UPDATE"],
                    "resources": ["deployments"],
                }
            ]
        },
        "validations": [
            {
                "expression": "object.spec.template.spec.containers.all(c, c.image == 'ds60sqlpy-k8s-fixture:0.2.0')",
                "message": "lesson requires the preloaded fixture 0.2.0 image",
            }
        ],
    },
}
binding = {
    "apiVersion": "admissionregistration.k8s.io/v1",
    "kind": "ValidatingAdmissionPolicyBinding",
    "metadata": {"name": "lesson-approved-image-owned"},
    "spec": {
        "policyName": "lesson-approved-image",
        "validationActions": ["Deny"],
        "matchResources": {
            "namespaceSelector": {"matchLabels": {"learning.ds60sqlpy/admission-demo": "true"}}
        },
    },
}
save("k8s-031-admission.json", {"apiVersion": "v1", "kind": "List", "items": [policy, binding]})
author(
    31,
    """API authorization answers whether an authenticated caller may attempt an action on a resource. Schema validation asks whether the object has a permitted shape. Admission can impose additional conditions on an otherwise authorized, well-formed request before it is persisted. A policy denial is therefore different from an image pull failure in a Pod that was already accepted.

The host-only fixture uses a ValidatingAdmissionPolicy with a CEL expression and a separate binding. CEL is a constrained expression language for evaluating data such as the proposed object. The expression requires every ordinary Deployment container image to equal the preloaded fixture tag. The binding selects only namespaces carrying a host-controlled lesson label and enforces Deny. The learner cannot add that label to unrelated namespaces or install policies.

This is a deliberately small demonstration. It does not validate init containers, image signatures, every workload kind or all security fields, and a mutable tag is not a publisher identity. The normal browser parser already rejects unapproved images locally. A browser refusal cannot prove that the API admission policy ran, so the advanced host test must retain an actual server denial and an allowed control.""",
    [
        (
            "Read policy and binding together",
            """[The admission fixture](../fixtures/k8s-031-admission.json) contains two cluster-scoped objects reserved for the host. matchConstraints targets CREATE and UPDATE of apps/v1 Deployments. The expression traverses spec.template.spec.containers and uses all(c, predicate), meaning every element must satisfy the image comparison. A direct Pod request is outside this example's resource match.

The binding connects policyName to the policy and narrows matching with namespaceSelector. Without an applicable binding, the policy definition alone does not establish this enforcement path. A host must verify the namespace label and policy status/type-checking before using the result as a control.

failurePolicy Fail specifies the treatment of applicable evaluation failures. It is not a substitute for writing a correct expression. A malformed or overbroad policy can block legitimate changes. Use an exclusive lesson scope, a known allowed object and a reversible host-managed lifecycle.""",
        ),
        (
            "Design a controlled denial",
            """Start with the unchanged approved Deployment and record acceptance in the intended namespace. Then change only its image to a clearly unapproved synthetic value while keeping the object valid. The admission denial should name the matching policy reason, and no workload with the rejected new spec should be persisted.

Compare three observations: a normal-worker local parser rejection, a server admission denial under the advanced lease, and an accepted object that later cannot pull an image. They may all prevent a useful Pod, but they establish different controls. A network timeout or generic403 is not evidence for this CEL predicate.

Finally restore the approved source and confirm the positive path. Test order and field isolation matter: if the negative request also contains invalid YAML or lacks authorization, it may never reach the intended admission decision. Retain the request identity and denied field without printing credentials.""",
        ),
        (
            "Keep policy claims narrow",
            """The expression protects only the resource and container list it names. A complete production policy would need a separately reviewed threat model, workload coverage, digest/provenance semantics and rollout strategy. Do not quietly broaden this teaching policy across the cluster.

A failed admission request should not be repaired by disabling safeguards globally. Correct the intended object or report that the requested behavior is outside the lesson. The host removes only its own policy and binding after all scoped evidence is captured.""",
        ),
    ],
    [
        (
            "Evaluate the CEL predicate",
            """Allowed images [ds60sqlpy-k8s-fixture:0.2.0] make all return true. A two-container list containing that value and unapproved:0 makes it false. The predicate is a universal condition over the matched Deployment container list.""",
            "One unapproved ordinary container is enough to deny a matched request.",
        ),
        (
            "Classify three failures",
            """Trace A: browser says source image is outside the allowlist before an API call. Trace B: server names lesson-approved-image and rejects the request. Trace C: Deployment persisted, Pod reports ImagePullBackOff.""",
            "A proves the local source boundary; B proves the scoped admission path; C is a post-acceptance runtime failure.",
        ),
    ],
    [
        (
            "Map the enforcement chain",
            "Place authentication, authorization, validation/admission and persistence in the request story.",
            "A rejected earlier boundary cannot prove a later policy ran.",
            "Follow the request until its actual stopping point.",
            "The exact server pipeline includes details beyond this sketch, but the evidence distinction is essential. A credential failure, invalid type or local parser refusal should not be counted as a successful test of an admission predicate.",
        ),
        (
            "Inspect policy scope",
            "Identify matched API group, version, resource, operations and namespace binding.",
            "apps/v1 Deployments on CREATE/UPDATE in the labeled owned namespace only.",
            "Read policy and binding as one configuration.",
            "The binding is what connects this policy to the intended lesson scope. The host should inspect its own namespace identity and label, because a correct expression applied to the wrong scope can still be operationally unsafe.",
        ),
        (
            "Evaluate all-container logic",
            "Compare approved-only with approved-plus-unapproved lists.",
            "True for approved-only and false for the mixed list.",
            "all is a universal quantifier.",
            "Checking only the first container would leave an obvious gap. This predicate handles every ordinary container in the named field, but it still does not imply coverage of init containers or other workload resource kinds.",
        ),
        (
            "Capture a real denial",
            "In the qualified host test, change only the image and record the server response.",
            "Policy-specific denial and no persisted rejected revision.",
            "A parser refusal or image-pull error is a different control.",
            "Holding all other fields constant makes the result attributable to the intended policy condition. A denied request can leave the previous valid revision in place, so readback should distinguish old state from the rejected candidate.",
        ),
        (
            "Restore the positive control",
            "Submit the approved source through the same scoped server path.",
            "Allowed request accepted and its application observation recorded separately.",
            "Admission success is not readiness.",
            "The positive control shows the policy is selective rather than simply blocking every request. Application checks still follow acceptance, because the policy cannot prove scheduling, startup or correct response content.",
        ),
        (
            "Document gaps and teardown",
            "Name uncovered fields and remove only the host-owned policy/binding.",
            "No claim of signature verification or universal workload enforcement.",
            "A tag equality rule has a small, explicit purpose.",
            "The result should state the exact match scope and trusted host configuration. Cleanup is a host responsibility with object identities and ownership checks, preserving any unrelated cluster policy.",
        ),
    ],
    hello(),
    """
APPROVED='ds60sqlpy-k8s-fixture:0.2.0'
def allowed(containers):return all(c['image']==APPROVED for c in containers)

def main():
    assert allowed([{'image':APPROVED}])
    assert not allowed([{'image':APPROVED},{'image':'unapproved:0'}])
    layers={'local rejection':'source parser','policy denial':'API admission','ImagePullBackOff':'runtime'}
    assert len(set(layers.values()))==3
    print('k8s-031 predicate examples passed; no CEL evaluator or API admission invoked')

if __name__ == "__main__":
    main()
""",
    capability="host-installed namespace-selected admission policy and server denial capture",
    refs=[
        "[ValidatingAdmissionPolicy](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/)",
        "[Kubernetes admission controllers](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/)",
    ],
)

pdb = {
    "apiVersion": "policy/v1",
    "kind": "PodDisruptionBudget",
    "metadata": {"name": "hello-budget"},
    "spec": {"minAvailable": 1, "selector": {"matchLabels": {"app": "hello"}}},
}
deployment = copy.deepcopy(hello()[0])
deployment["spec"]["replicas"] = 2
author(
    32,
    """A PodDisruptionBudget, abbreviated PDB, constrains supported voluntary evictions of a selected application. It helps coordinate maintenance with the application's available replicas. It does not stop a machine from failing, guarantee scheduling capacity or make a directly deleted Pod survive. The distinction matters because the same observed lost replica can result from very different control paths.

Our example selects app=hello and sets minAvailable1 while the Deployment desires two replicas. In a simplified healthy snapshot with both Pods available, one voluntary disruption can fit the budget. If only one is healthy, another disruption does not fit. The API status and eviction decision are authoritative for the actual moment, because readiness and in-progress disruptions can change between observations.

The normal browser run does not drain Nodes or issue learner-controlled eviction requests. This advanced lab needs an exclusive multi-node lease and a host operation restricted to one owned worker Node. The application remains namespaced, but Node maintenance is a separate host-level capability with a deadline, cancellation and restoration plan.""",
    [
        (
            "Read budget arithmetic and status",
            """minAvailable is the minimum healthy selected count the budget aims to preserve during supported voluntary disruption. maxUnavailable is an alternative expression; this fixture uses an integer minimum to avoid percentage rounding ambiguity. The selector must match the intended Pods, and an accidentally broad selector changes the application set being counted.

For the teaching trace, allowed=max(0,healthy-minimum). With healthy2 and minimum1, the result is1. After one Pod becomes unavailable, healthy1 yields0. Real PDB status also accounts for controller observation and already disrupted Pods. Do not use a stale handwritten subtraction as permission to evict.

Read currentHealthy, desiredHealthy, disruptionsAllowed and observedGeneration together. A budget with disruptionsAllowed0 is not necessarily broken: it may be correctly refusing maintenance because replacement capacity or readiness is missing. Diagnose the selected workload before weakening the budget.""",
        ),
        (
            "Separate eviction, deletion and node loss",
            """An eviction request uses the Eviction API and can be rejected when the disruption budget would be violated. A direct Pod delete is a different operation and can bypass that protection. A node outage is involuntary; the budget cannot prevent physical or virtual machine failure. Workload redundancy and placement address different parts of availability.

A host drain includes more than the arithmetic: it may make the Node unschedulable and handle several workload classes. The course operation must select one exact owned worker identity and exclude unrelated resources. The learner does not run a broad drain against the active context or add force/delete-data flags to overcome a refusal.

Recovery requires replacements to schedule and become ready on remaining capacity. A two-node label alone does not guarantee spare CPU, topology compatibility or volume attachment. Observe pending reasons and application responses, then restore the intended Node scheduling state through the host-owned operation.""",
        ),
        (
            "Interpret a maintenance refusal",
            """A blocked eviction is useful evidence of a protected boundary, not an invitation to delete the Pod directly. Record the budget, selected Pod UID, readiness and response reason. A successful eviction is also not enough: replacement readiness and application behavior must satisfy the end-to-end maintenance goal.

This small kind rehearsal does not establish production high availability, zone failure tolerance or durable storage resilience. Report the specific voluntary maintenance path, finite observations and untested failure modes.""",
        ),
    ],
    [
        (
            "Compute a snapshot budget",
            "```yaml\n"
            + yaml.safe_dump(pdb, sort_keys=False)
            + "```\nWith two selected healthy Pods, minimum1 leaves one potential disruption. With one healthy Pod, it leaves zero.",
            "The arithmetic predicts1 then0, subject to actual current PDB status and in-progress operations.",
        ),
        (
            "Compare protected and unprotected loss",
            """Trace A: Eviction API refuses the last healthy Pod. Trace B: a direct Pod delete removes it. Trace C: the hosting Node disappears. Only A demonstrates the budget enforcing its supported voluntary path.""",
            "The PDB is a coordination mechanism for eviction, not a universal prevention of Pod loss.",
        ),
    ],
    [
        (
            "Verify selector scope",
            "Compare app=hello selector against two hello Pods and one unrelated Pod.",
            "Exactly the two hello Pods contribute to this example.",
            "Count selected healthy Pods, not all Pods in the namespace.",
            "A budget label should match the application it protects. Including an unrelated healthy Pod could make the arithmetic look safer than the target application really is, while selecting none can leave the intended workload unprotected.",
        ),
        (
            "Predict healthy-count changes",
            "Evaluate healthy counts2,1 and0 with minimum1.",
            "Potential disruptions1,0,0 in the simplified model.",
            "Clamp the difference at zero.",
            "Negative capacity is represented as no allowed disruptions. The live status can include additional controller bookkeeping, so this calculation is a prediction to compare with observations rather than an authorization token.",
        ),
        (
            "Capture a denied eviction",
            "Use the host allowlisted operation when one selected Pod is healthy.",
            "Denial is tied to the intended PDB and Pod UID.",
            "Avoid substituting direct delete.",
            "The refusal demonstrates why the budget exists. Preserve the reason and state, then repair missing readiness or capacity if that is the actual problem. Bypassing the API would invalidate the maintenance exercise.",
        ),
        (
            "Observe a permitted maintenance path",
            "With the qualified two-replica state, request one bounded owned-worker maintenance operation.",
            "Allowed disruption, replacement readiness and finite application success are recorded.",
            "A successful eviction is only the start of recovery.",
            "The evidence should include before/after Pod identities and selected Node identity. A replacement that remains Pending means the maintenance goal is not complete, even if the initial eviction was legitimate.",
        ),
        (
            "Diagnose unavailable replacement capacity",
            "Interpret Pending due to requests, affinity or volume placement.",
            "A specific scheduling/storage cause is named without weakening unrelated policy.",
            "Read events and the requested resources.",
            "PDBs cannot create spare resources. The appropriate repair depends on the observed constraint and the qualified host environment. Increasing replicas repeatedly without addressing the constraint may only add Pending Pods.",
        ),
        (
            "State protection limits and restore",
            "Compare eviction with direct delete/node loss and restore host scheduling state.",
            "Only the tested voluntary path is claimed; owned Node state is restored.",
            "Availability has multiple failure boundaries.",
            "The final review should explain what the PDB enforced and what redundancy, placement and storage would need to handle separately. Exact owned cleanup and Node restoration remain part of the maintenance contract.",
        ),
    ],
    [deployment, pdb],
    """
def budget(healthy,minimum):return max(0,healthy-minimum)

def main():
    assert [budget(n,1) for n in (2,1,0)]==[1,0,0]
    pods=[{'app':'hello','ready':True},{'app':'hello','ready':True},{'app':'other','ready':True}]
    assert sum(p['ready'] for p in pods if p['app']=='hello')==2
    protected={'eviction':True,'direct-delete':False,'node-loss':False}
    assert protected['eviction'] and not protected['node-loss']
    print('k8s-032 synthetic budget passed; no eviction or drain performed')

if __name__ == "__main__":
    main()
""",
    capability="exclusive multi-node lease and host-allowlisted owned-worker eviction/drain",
    refs=[
        "[Configure a PodDisruptionBudget](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)",
        "[Kubernetes disruptions](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)",
    ],
)
