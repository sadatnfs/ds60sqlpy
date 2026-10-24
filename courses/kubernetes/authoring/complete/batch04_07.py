from author import author, hello
import yaml

role = {
    "apiVersion": "rbac.authorization.k8s.io/v1",
    "kind": "Role",
    "metadata": {"name": "lesson-reader"},
    "rules": [
        {
            "apiGroups": ["apps"],
            "resources": ["deployments"],
            "resourceNames": ["hello"],
            "verbs": ["get"],
        }
    ],
}
author(
    4,
    """A Kubernetes request has a caller identity, a target API server, a resource scope and an action. Authentication establishes who the caller is. Authorization decides whether that identity may perform the requested verb on the resource. A namespace is a scope for many objects, not a complete security boundary by itself. Cluster-scoped objects such as Nodes and namespaces require separate permissions.

The course uses a private lease for one disposable cluster and namespace. Its namespace name, UID, owner marker and expiry must agree with fresh readback. A familiar name or a selected terminal context is not enough. Names can be reused after deletion, and an ambient kubeconfig can point somewhere unrelated.

This lesson is a reading and explicitly targeted host-observation worksheet. The browser can run a fixed workload under its lease, but it does not accept arbitrary authorization commands or Role manifests. The supplied Role is a real namespaced API example for inspection; it does not grant the learner permission to create roles.""",
    [
        (
            "Read identity and RBAC without confusing scopes",
            """A Role lists allowed verbs, API groups and resources inside a namespace. A RoleBinding connects that Role to a user, group or ServiceAccount. A ClusterRole can describe cluster-scoped permissions or be bound into a namespace, while a ClusterRoleBinding grants its described scope across the cluster. These are different relationships, not synonyms for administrator access.

The example Role permits only get on the Deployment named hello. It does not permit listing every Deployment, creating a Deployment, reading Secrets or creating a namespace. Kubernetes authorization is additive: another binding could grant more, so a single Role file is not a complete proof of effective permissions. Inspect the actual identity and a self-authorization result in the owned environment.

A resourceNames restriction can constrain named get/delete requests. Creating a resource normally targets a collection before a name is available to authorization, so a resourceNames rule does not generally constrain create in the same way. The broker therefore combines namespace-scoped creation permission with a separate fixed-name manifest validator.""",
        ),
        (
            "Follow an explicit target receipt",
            """Before a host observation, obtain the private kubeconfig path, context and namespace from the owned receipt. Use all three explicit flags on every kubectl call and fail if any is missing. The shared host-lab guide provides POSIX and PowerShell syntax. Never switch a default context to make the exercise work.

The namespace UID distinguishes the leased object from a same-name replacement. Compare it together with the owner marker before a mutation or cleanup. Lease expiry is another independent boundary: a valid-looking file does not authorize a run beyond its lifetime. The worker checks that the lease covers both work and cleanup reserve.

Credentials stay outside source, progress and exported evidence. Record nonsecret identity fields and the yes/no result of an authorization check, not the token or kubeconfig contents. A denied namespace creation or Secret read is expected least-privilege evidence in this course.""",
        ),
        (
            "Diagnose a refusal before broadening access",
            """Separate missing authentication, an expired lease, a wrong target UID and an authorization denial. They have different repairs. Retrying with an ambient administrator context would change the experiment and bypass the intended boundary. A successful own-namespace read does not prove cluster-wide permission, and a Role YAML file does not prove the server loaded that policy.

The offline checker models only the explicit permission matrix and receipt equality. It makes no API request. A live claim requires the actual owned identity, a fresh namespace readback and positive/negative authorization observations.""",
        ),
    ],
    [
        (
            "Read a narrow Role",
            "```yaml\n" + yaml.safe_dump(role, sort_keys=False) + "```",
            "The only listed action is get on apps/Deployment hello in the binding namespace.",
        ),
        (
            "Reject a same-name replacement",
            """Synthetic receipt: namespace lesson-a, UID ns-1, owner owner-a. Fresh observation: namespace lesson-a, UID ns-2, owner owner-a. The name and label match, but the UID does not.""",
            "The target identity is not established; no mutation or cleanup is authorized by this receipt.",
        ),
    ],
    [
        (
            "Identify the request tuple",
            "Write the caller,namespace,API group,resource,name and verb for an owned hello Deployment read.",
            "A six-field request includes apps/deployments,hello,get and the explicit leased namespace.",
            "Separate the resource kind from its API plural and caller identity.",
            "The API authorizes a specific action against a resource scope. An object name without namespace and caller information is incomplete. The learner record should identify the private context by its nonsecret name while keeping credential contents private.",
        ),
        (
            "Read the Role grant",
            "Compare get hello with list deployments and create namespaces under the example Role.",
            "Only get hello is granted by this Role; list and namespace creation are absent.",
            "Look at verbs,resourceNames and scope independently.",
            "The Role contains one named read permission. It does not imply list or create rights, and namespace creation is cluster-scoped. Other bindings could add permissions, so this static inspection is a prediction to confirm with the actual owned identity.",
        ),
        (
            "Check namespace identity",
            "Compare the ns-1 receipt with the ns-2 readback.",
            "Refuse despite the matching namespace name and owner label.",
            "A name can be reused; the UID identifies this object instance.",
            "Deleting and recreating a namespace creates a new identity. Continuing with an old receipt could act on an unrelated replacement. The UID mismatch is therefore a decisive boundary, not a warning to ignore because the visible name looks familiar.",
        ),
        (
            "Observe least privilege",
            "With an explicitly provisioned lease, record an own-namespace permitted action and a denied cluster/Secret action.",
            "Actual allow/deny results are recorded separately from source policy; no credentials enter the worksheet.",
            "Use the host guide targeting flags and a self-authorization check.",
            "The live observation establishes effective policy for that identity and time. It should include the requested verb/resource and nonsecret target. A denied action is a successful negative check when the curriculum intends the identity to lack that permission.",
        ),
        (
            "Inspect expiry and cleanup reserve",
            "Evaluate a synthetic lease expiring in30seconds for60seconds of work plus15seconds cleanup and5seconds margin.",
            "Refuse because30<80.",
            "Add the full work,cleanup and margin budget before comparing expiry.",
            "The worker must retain enough credential lifetime to clean up after interruption. A lease that covers only nominal work can fail at the recovery boundary. The calculation is synthetic; a real run uses observed current time and the private receipt expiry.",
        ),
        (
            "Explain additive authorization",
            "Describe why one narrow Role file cannot prove that no other privilege exists.",
            "A written answer includes other RoleBindings/ClusterRoleBindings and actual effective authorization evidence.",
            "RBAC grants combine; absence from one file is not a global denial proof.",
            "A complete access claim must account for the identity's other bindings and admission/runtime controls where relevant. The course avoids relying on a visual policy snippet alone and keeps the private session scoped and short-lived.",
        ),
    ],
    [role],
    """
def main():
    allowed={('apps','deployments','hello','get')}
    assert ('apps','deployments','hello','get') in allowed
    assert ('apps','deployments','hello','list') not in allowed
    assert ('','namespaces','new','create') not in allowed
    receipt={'namespace':'lesson-a','uid':'ns-1','owner':'owner-a'}
    observed={'namespace':'lesson-a','uid':'ns-2','owner':'owner-a'}
    assert receipt['namespace']==observed['namespace'] and receipt['uid']!=observed['uid']
    assert 30<60+15+5
    print('k8s-004 synthetic permission and identity calculations passed; no API calls made')

if __name__ == "__main__":
    main()
""",
    capability="effective-authorization and explicit-target host observation",
    refs=[
        "[Kubernetes RBAC authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)"
    ],
)

author(
    5,
    """A Pod is Kubernetes\'s scheduling and lifecycle unit for one or more containers that share certain resources. A container is a running process environment created from an image. An image is packaged filesystem/configuration content, while a tag is a name that can move unless its identity is pinned or independently recorded. The course preloads a reviewed local image and uses imagePullPolicy Never so Run does not fetch an arbitrary replacement.

Pod phase is a broad lifecycle summary. Running does not mean every container is ready to serve the application, and a container can restart while the Pod keeps the same UID. Readiness is a separate condition used by Service routing. Logs describe process output, while API status and ownership describe which process/object you are inspecting.

The browser source creates the fixed hello Deployment so the controller produces the Pod. It does not accept arbitrary Pod names or missing-image tags. A host-provided missing-image negative case belongs to a separate owned observation, and a broker rejection before create must not be mislabeled as a kubelet image failure.""",
    [
        (
            "Trace image selection to process observation",
            """The manifest selects ds60sqlpy-k8s-fixture:0.2.0 and Never. The host qualification receipt must record the actual image identity and preload on each eligible node. If the image is absent under Never, the kubelet reports an image-availability failure instead of automatically pulling it. A locally present tag alone is weaker evidence than a recorded content identity.

The fixed command starts the fixture server on container port8080. Declaring containerPort documents the port; it does not publish a host port or create a Service. The Pod has no service-account token mount, runs as a fixed nonroot UID and has a read-only root filesystem with dropped capabilities. Those settings are part of the admitted workload contract.

The browser waits for controller and Ready Pod identities and then cleans up. A Deployment-only Run does not include the separate in-cluster Service client. Record that distinction when interpreting success.""",
        ),
        (
            "Inspect status and bounded logs",
            """Container state can be Waiting, Running or Terminated, with reason fields such as ErrImageNeverPull or an exit code. Pod phase and Ready conditions summarize different aspects. A waiting container may have no application logs because the process never started. Looking for a missing log line is therefore not the best first diagnostic for an image failure.

For a running container, inspect logs only from the named owned Pod and container with a bounded tail/byte budget. Keep Pod UID and container restart count with the excerpt. Otherwise a line from a previous container instance can be mistaken for the current process. The course fixture intentionally produces no real customer data or credentials.

The synthetic example Running plus Ready=False has no eligible ready Service backend under the standard selector/readiness contract. A successful GET /version from a fresh client is additional application evidence, not a consequence of the phase string alone.""",
        ),
        (
            "Common misleading shortcuts",
            """Do not infer readiness from phase Running, infer a successful image pull from a tag name, or infer current process identity from a reused Pod name. An old saved image0.1 source receives an explicit broker version refusal; that is a source-admission result, not an observed node pull failure.

Use the narrowest discriminating field: Waiting.reason for image availability, container termination state for exit behavior, Ready condition for routing eligibility and a client response for the application. A source review or synthetic trace is labeled as such until an actual owned observation exists.""",
        ),
    ],
    [
        (
            "Separate phase from readiness",
            """Synthetic Pod status: phase Running; container state Running; Ready condition False; restartCount0. The process exists but the readiness check has not passed.""",
            "Running process evidence does not establish a ready backend or successful application request.",
        ),
        (
            "Read a missing-image failure",
            """A teacher-provided owned Pod uses imagePullPolicy Never with an intentionally absent synthetic image. The useful observation is Waiting.reason=ErrImageNeverPull, with no successful application start. The normal browser source rejects unapproved image names before this step.""",
            "Distinguish an actual kubelet image-absence condition from a pre-API broker refusal.",
        ),
    ],
    [
        (
            "Identify image and process contract",
            "Read the source image,pull policy,command and named port.",
            "Image0.2.0,Never,fixed fixture server,port8080 named http.",
            "Read each field rather than inferring it from the filename.",
            "The source describes the requested image and process. Actual preload and runtime behavior require a host/image receipt and observed Pod. The port declaration alone does not create routing or host exposure.",
        ),
        (
            "Trace broad and precise state",
            "Classify the synthetic Running/Ready=False record.",
            "Process running,readiness unproved,no ready-routing claim.",
            "Read the condition separately from phase.",
            "Pod phase is intentionally broad. Readiness controls whether the application is considered eligible for normal Service traffic, while process liveness and client correctness are separate questions.",
        ),
        (
            "Diagnose the image boundary",
            "Compare unapproved-image broker rejection with ErrImageNeverPull from a scoped host fixture.",
            "Two different failure phases are named; neither is described as an application crash.",
            "Ask whether an API object and container process were ever created.",
            "The broker may reject source before the cluster sees it. A kubelet image-absence reason implies an accepted Pod reached node image handling. Preserving the phase prevents ineffective repairs such as changing application code for an image that never started.",
        ),
        (
            "Read logs with identity",
            "Record a bounded synthetic log excerpt with Pod UID,container name and restart count.",
            "An evidence record ties the line to the exact observed process instance.",
            "Use explicit targeting and bounded log options from the host procedure.",
            "A reused name or previous container log can mislead diagnosis. UID and restart context explain which execution produced the line. No real secret or unrelated workload output belongs in the learner evidence packet.",
        ),
        (
            "Distinguish restart from replacement",
            "Compare same Pod UID with restartCount1 against a new Pod UID with restartCount0.",
            "First is a container restart; second is a different Pod instance.",
            "Names and counts alone do not establish identity.",
            "A Deployment can replace a Pod, while the kubelet can restart a container inside an existing Pod. These events have different lifetime implications for ephemeral storage and owner relationships, developed in later chapters.",
        ),
        (
            "Prove the bounded baseline",
            "Run the allowed source under a qualified lease and state what its result does and does not observe.",
            "Controller/Ready Pod identities and owned cleanup are observed; Deployment-only run has no Service-client proof.",
            "Compare the result check names with the actual source resource set.",
            "The evidence should match the operation that ran. Do not copy a Service success claim from another lesson when this source contains no Service. Keep runtime qualification and the six-task explanation separate from a successful process status.",
        ),
    ],
    hello(),
    """
def main():
    status={'phase':'Running','ready':False,'restart_count':0,'uid':'pod-a'}
    assert status['phase']=='Running' and not status['ready']
    restarted={**status,'restart_count':1}
    replaced={**status,'uid':'pod-b'}
    assert restarted['uid']==status['uid'] and restarted['restart_count']==1
    assert replaced['uid']!=status['uid']
    assert {'waiting_reason':'ErrImageNeverPull'}['waiting_reason']!='CrashLoopBackOff'
    print('k8s-005 synthetic lifecycle distinctions passed; no cluster observation inferred')

if __name__ == "__main__":
    main()
""",
    browser=True,
    capability="fixed Deployment baseline plus scoped host image/log observations",
    refs=[
        "[Kubernetes Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)"
    ],
)

author(
    6,
    """A Deployment describes desired application replicas and manages ReplicaSets that in turn manage Pods. A controller repeatedly compares desired and observed state and acts to reduce the difference. This reconciliation loop is why deleting one controlled Pod can lead to a replacement without editing the Deployment manifest.

The objects have distinct identities. The Deployment UID identifies the controller object, the ReplicaSet UID identifies a particular template revision\'s replica controller, and each Pod has its own UID. Counting two Pods without tracing ownership can accidentally include an unrelated workload. A replacement Pod can reuse a similar generated name but must have a new UID.

The browser source can establish a fresh two-replica baseline and clean it up. The deliberate Pod-deletion experiment needs a separate stateful owned host operation because the one-shot browser Run does not leave a workload behind for arbitrary later mutation. The normal worker identity does not gain Pod-delete permission from this lesson.""",
    [
        (
            "Follow the controller chain",
            """The Deployment selector app=hello must match its Pod-template labels. The Deployment creates or adopts the appropriate ReplicaSet according to its controller rules; Pods reference the ReplicaSet as controller owner. A verifier should connect those UIDs back to the intended Deployment rather than only count labels.

spec.replicas=2 is intent. status.observedGeneration indicates which generation the controller has processed, while updatedReplicas,readyReplicas and availableReplicas describe different observed states. The desired count can be accepted before the controller creates Pods, before scheduling succeeds or before readiness passes. Bounded waiting should report which step has not converged.

Changing Pod-template content generally creates a new revision/ReplicaSet. Deleting a Pod does not by itself change the Deployment spec or its generation. This distinction prevents a replacement event from being mislabeled as a rollout.""",
        ),
        (
            "Trace a replacement without inventing a receipt",
            """The synthetic baseline has Deployment UID dep-a,ReplicaSet UID rs-a and Pod UIDs pod-1,pod-2. After a controlled deletion of pod-1, the observed Pod set becomes pod-2,pod-3. Deployment UID and desired replicas remain unchanged. The new Pod is linked through rs-a to dep-a.

A live deletion must target the exact owned Pod UID with an API precondition and the authorized stateful capability. A name-only delete after reading a stale list can remove a replacement. The course host procedure requires identity checks and a bounded recovery wait. Do not use a broad label-selector delete as a shortcut.

Recovery evidence includes a fresh ownership graph, two Ready Pod UIDs and relevant generation/count fields. It does not establish an availability guarantee during the replacement, which would require client observations over the interval.""",
        ),
        (
            "Diagnose count and identity mismatches",
            """Two Running Pods can both be unready, and a matching label can belong to a different controller. A stale status count can describe an older generation. Inspect ownerReferences and UIDs before interpreting counts, and preserve a negative fixture with a foreign Pod UID so a count-only checker is visibly inadequate.

A one-shot Run\'s final cleanup is separate from the deliberate replacement exercise. Do not claim that a Pod observed in a later Run is the replacement of a Pod from an already cleaned-up earlier Run; the Deployment itself may also be a new object.""",
        ),
    ],
    [
        (
            "Read desired and observed counts",
            """Synthetic desired replicas2,metadata.generation4,status.observedGeneration3,readyReplicas2. The count looks healthy, but the controller has not yet observed the latest desired generation.""",
            "The latest change is not proved converged despite two ready replicas.",
        ),
        (
            "Track a replacement graph",
            """Before: dep-a -> rs-a -> {pod-1,pod-2}. After an owned delete: dep-a -> rs-a -> {pod-2,pod-3}. Desired replicas remain2 and the Deployment generation is unchanged.""",
            "One new Pod UID appears,one old UID disappears,and the controller identity remains dep-a.",
        ),
    ],
    [
        (
            "Draw ownership",
            "Trace Deployment,ReplicaSet and Pod controller references for the baseline.",
            "A UID-linked graph connects exactly two owned Pods to the intended Deployment.",
            "Follow controller=true owner references rather than labels alone.",
            "Labels select sets but do not prove controller ownership. The graph distinguishes the application replicas from unrelated Pods that happen to share a label. Each link should come from actual readback in a live exercise or be labeled synthetic here.",
        ),
        (
            "Compare generation evidence",
            "Interpret generation4 with observedGeneration3 and readyReplicas2.",
            "Latest desired state not yet confirmed observed.",
            "Ready count and generation answer different questions.",
            "The controller can report a healthy prior state while a new spec is waiting to reconcile. A verifier should require the relevant generation relationship and updated counts before claiming the current change succeeded.",
        ),
        (
            "Establish a fresh baseline",
            "Use the allowed two-replica source in a qualified browser operation.",
            "Two Ready owned Pod UIDs and cleanup evidence,with a new Run identity.",
            "Record the actual result rather than reusing the synthetic UID names.",
            "The browser creates a new bounded baseline and then cleans it. Its receipt supports the checks it performed. The human explanation must not replace actual server-assigned UIDs with the fixture's illustrative identifiers.",
        ),
        (
            "Rehearse scoped Pod replacement",
            "With a stateful owned host capability,delete only the recorded Pod UID and wait for replacement.",
            "Pod set changes from{pod-1,pod-2} to{pod-2,pod-3} in the synthetic trace; live names/UIDs are recorded separately.",
            "Keep Deployment UID and generation in the before/after packet.",
            "The replacement is caused by the ReplicaSet restoring desired replicas. It is not a new Deployment or necessarily a new template revision. The operation must use UID-aware targeting and preserve unrelated objects.",
        ),
        (
            "Reject a count-only shortcut",
            "Add a foreign-controller Pod to a synthetic list while removing one owned Pod.",
            "Raw count2 but owned Ready count1,so acceptance fails.",
            "Filter by the verified ownership chain before counting.",
            "An unrelated Pod cannot satisfy this Deployment's desired replica contract. This negative case demonstrates why counting labels or phase values without ownership can produce a false success.",
        ),
        (
            "Separate recovery from availability",
            "Explain which additional observations would show whether clients remained served during replacement.",
            "A bounded client timeline and error counts are required beyond final Ready replicas.",
            "Final state does not describe every intermediate request.",
            "The control loop may restore the final desired count after a period of reduced capacity. A client trace can establish observed continuity for its sampled requests, while a final Pod snapshot cannot. Finite samples still do not prove a universal SLA.",
        ),
    ],
    hello(),
    """
def main():
    before={'deployment':'dep-a','replicaset':'rs-a','pods':{'pod-1','pod-2'},'generation':1}
    after={**before,'pods':{'pod-2','pod-3'}}
    assert before['deployment']==after['deployment'] and before['generation']==after['generation']
    assert after['pods']-before['pods']=={'pod-3'} and before['pods']-after['pods']=={'pod-1'}
    assert not (3>=4)
    pods=[{'uid':'owned','controller':'rs-a','ready':True},{'uid':'foreign','controller':'rs-other','ready':True}]
    assert len(pods)==2 and sum(p['controller']=='rs-a' and p['ready'] for p in pods)==1
    print('k8s-006 synthetic reconciliation and ownership checks passed')

if __name__ == "__main__":
    main()
""",
    browser=True,
    capability="fixed Deployment baseline; separate UID-scoped stateful Pod replacement",
    refs=[
        "[Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)"
    ],
)

author(
    7,
    """Labels are key-value metadata used to select sets of objects. A Service uses a selector to identify backing Pods and provides a stable network abstraction over their changing identities. The Service object, its selected Pods and its EndpointSlices are separate resources whose relationships must be observed.

A ClusterIP Service does not publish an external address or prove that an application is healthy. Its port is the port clients use on the Service, while targetPort identifies the destination port on backing Pods. A named targetPort such as http resolves through the container port declaration. A mismatch can break traffic even when the Service object exists.

The current browser operation supports the fixed hello Deployment and hello Service. It checks Ready Pod UIDs,unique eligible EndpointSlice Pod UIDs and a new in-cluster version client,then cleans only owned resources. It deliberately permits a wrong selector value as a bounded negative case,which should fail to establish backends rather than silently succeed.""",
    [
        (
            "Follow selection and port mapping",
            """The Deployment template labels Pods app=hello. The Service selector app=hello selects those labels; changing it to app=wrong selects a different set,usually empty in this owned fixture. The selector is not an owner reference and does not create Pods. The Deployment and Service can therefore be accepted independently while routing is still wrong.

The admitted Service exposes port8080 and targetPort http. The container declares name http at containerPort8080. All three pieces must agree with the actual server listener. A port name is a lookup key,not a second network port. The fixed adapter refuses arbitrary host exposure,NodePort,external endpoints and unbounded port choices.

DNS resolves the Service name inside the appropriate cluster/namespace context. That resolution does not prove the selected application responds correctly. A complete test separates name resolution,routing,backend eligibility and the HTTP payload.""",
        ),
        (
            "Compare identities rather than raw endpoint counts",
            """EndpointSlices can represent multiple addresses or IP families for the same Pod. Counting raw endpoint entries can double-count one backend. The verifier collects eligible ready targetRef Pod UIDs and compares their set with the owned Ready Pod set. An endpoint for an unrelated Pod cannot satisfy the contract even if its IP responds.

The synthetic example has owned Ready UIDs {pod-a,pod-b} and two slices each listing both UIDs. There are four entries but only two unique backends. A second example replaces pod-b with foreign-c;the raw count is still two but the identity set is wrong.

The client Job is independent of readiness:it requests /version and checks the exact expected payload. A probe path can be healthy while the application route or Service selection is incorrect. The course uses a fresh owned client rather than inferring HTTP success from a status field.""",
        ),
        (
            "Diagnose routing failures at the correct layer",
            """A Service with no endpoints is different from a Service with ready endpoints but a wrong application response. A wrong selector is not repaired by changing the container image without evidence. A named-port mismatch is not a DNS failure. Record the discriminating field or client result before choosing a repair.

The browser source uses only its fixed port contract. Experiments with a second Service or arbitrary ports require a separate scoped host capability. Do not claim that the one-shot operation executed those transfer cases,or that finite client success proves long-term traffic availability.""",
        ),
    ],
    [
        (
            "Trace a named port",
            "```yaml\n" + yaml.safe_dump(hello(True)[1], sort_keys=False) + "```",
            "Service port8080 routes to the Pod container port named http,which the fixture declares as8080.",
        ),
        (
            "Deduplicate a dual-family observation",
            """Synthetic slices contain [pod-a,pod-b] and [pod-a,pod-b]. The owned Ready Pod set is {pod-a,pod-b}. Four endpoint entries represent two unique eligible Pod identities.""",
            "Deduplicated UID sets match;raw entry count4 is not replica count4.",
        ),
    ],
    [
        (
            "Trace selector equality",
            "Compare Deployment template app=hello with Service selector app=hello and app=wrong.",
            "Matching selector finds the intended set;wrong selector has no intended backends.",
            "Compare both label key and value.",
            "A selector is a set query over labels. It does not establish ownership by itself and it does not create missing Pods. The owned-controller UID check remains necessary after selection.",
        ),
        (
            "Resolve the port chain",
            "Read Service port,targetPort and container port name/number.",
            "Client8080 -> targetPort http -> container8080.",
            "A named target is resolved against the Pod's declared port name.",
            "The chain connects client-facing and backend ports. A Service object can exist even if this mapping is wrong,so object creation alone is insufficient routing evidence.",
        ),
        (
            "Count unique backends",
            "Deduplicate the four synthetic EndpointSlice entries.",
            "Exactly two unique Pod UIDs matching the owned Ready set.",
            "Use targetRef identity rather than entry count or address alone.",
            "Multiple slices or IP families can repeat a Pod identity. Set comparison avoids inflated backend counts and also detects an unrelated endpoint with the wrong UID.",
        ),
        (
            "Run a selector negative case",
            "Change only the allowed Service selector to app=wrong in an owned Run,then restore it.",
            "No matching ready backends;bounded failure and cleanup;restored source can pass separately.",
            "Preserve source change and failure phase in the record.",
            "The negative case tests the connection between selection and routing. A later successful Run is a fresh operation with its own UIDs,not evidence that the earlier Service persisted and was patched.",
        ),
        (
            "Verify an independent client",
            "Inspect the fresh client Job and exact /version result after backend checks.",
            "Job/Pod ownership and exit0 accompany the expected ds60-fixture-v1 payload contract.",
            "Do not substitute /ready for the application version route.",
            "The independent request establishes that the Service path reaches the expected fixture response. Job completion alone is tied to owned Pod identity and the fixed checker behavior;the result remains bounded to the observed request.",
        ),
        (
            "Design a second-Service transfer",
            "Explain a scoped host experiment using another Service without touching unrelated objects.",
            "A separate capability,unique owned resource receipt,selector/port/backend/client checks and UID-aware cleanup are specified.",
            "The browser owns only the fixed hello name.",
            "Generalizing the mechanism requires a deliberate new resource scope,not changing the browser validator to accept arbitrary names. The same evidence chain applies,but actual execution remains unavailable until the host capability is provided.",
        ),
    ],
    hello(True),
    """
def main():
    labels={'app':'hello'}
    assert all(labels.get(k)==v for k,v in {'app':'hello'}.items())
    assert not all(labels.get(k)==v for k,v in {'app':'wrong'}.items())
    ready={'pod-a','pod-b'};slices=[['pod-a','pod-b'],['pod-a','pod-b']]
    endpoints={uid for group in slices for uid in group}
    assert sum(map(len,slices))==4 and len(endpoints)==2 and endpoints==ready
    assert {'pod-a','foreign-c'}!=ready
    ports={'http':8080};assert ports['http']==8080
    print('k8s-007 synthetic selector,port and endpoint-identity checks passed')

if __name__ == "__main__":
    main()
""",
    browser=True,
    capability="fixed Deployment/Service baseline and selector negative case",
    refs=[
        "[Kubernetes Services](https://kubernetes.io/docs/concepts/services-networking/service/)"
    ],
)
