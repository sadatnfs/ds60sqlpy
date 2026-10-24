from author import author, fixture, hello, BASE
import copy, json, yaml, base64

startup = fixture("hello-startup.yaml")
author(
    15,
    """Startup,readiness and liveness probes answer different questions. Startup asks whether initialization has completed. Readiness asks whether this container should currently receive normal Service traffic. Liveness asks whether the container should be restarted after repeated failed checks. One endpoint can be used for several probes,but that does not make their control effects identical.

The contract-2 fixture exposes /startup,/ready and /live as separate fixed paths. A synthetic three-second startup delay makes /startup temporarily return503 while the process exists. Once a configured startup probe succeeds,the kubelet begins the normal liveness/readiness behavior. The healthy browser source is a bounded initial-state demonstration; detailed restart-count and transient-unreadiness comparisons require stateful host observations.

A probe is an operational policy about recovery and traffic. An expensive or dependency-sensitive liveness check can restart a healthy process during a downstream outage. A readiness check can remove traffic without restarting the container. Choose the intended effect before choosing a URL.""",
    [
        (
            "Trace probe control effects",
            """When a startup probe is configured,its success gates the other probe types. It can protect slow initialization from an aggressive liveness policy. The allowed source uses /startup with period1 and failureThreshold10 for the fixed delay3 case. This is a nominal probe budget,not a promise of an exact wall-clock transition because scheduling and request duration also matter.

A failed readiness check changes readiness and endpoint eligibility. It does not directly restart the container. Repeated liveness failure triggers a container restart according to the Pod\'s restart policy;the Pod UID can remain the same while restartCount increases. A Pod replacement is a different event with a new UID.

The fixture\'s /live route reports process health independently of its synthetic startup delay. Its /ready route retains the legacy response. Kubernetes\'s startup gating is therefore part of the lesson,not a property invented by changing every server endpoint to fail together.""",
        ),
        (
            "Interpret thresholds with actual observations",
            """Record configured period,timeout/failure policy,container state,restartCount,Ready condition and endpoint eligibility. A sample with Ready=False and unchanged restartCount is consistent with readiness removal;an increasing restartCount after liveness failures shows a different control action. Events and timestamps help link the cause to the observed transition.

The current one-shot verifier establishes a bounded healthy baseline and application response. It does not automatically grade every transient or long-running failure scenario. A wrong /missing liveness or startup path is an admitted fixed negative configuration,but the report must describe what was actually observed within the operation window rather than assume one exact restart sequence.

Use the smallest startup allowance justified by measured initialization with margin. Making thresholds huge can hide a broken service,and making them tiny can create a restart loop. The synthetic delay is a teaching fixture,not a production tuning recommendation.""",
        ),
        (
            "Avoid coupled failure policies",
            """Do not use a remote dependency check as liveness merely because it is convenient:restarting every caller may amplify the dependency outage. Do not call a Running Pod ready or assume a successful startup probe means all future requests succeed. A startup success is an initial milestone;readiness and liveness continue to have distinct roles.

A source change alone is not evidence that the kubelet used the intended probe. Observe the current Pod template and identity,then the relevant conditions/events/restart counts. Preserve the bounded cleanup result even for an intentionally unhealthy configuration.""",
        ),
    ],
    [
        (
            "Read the healthy startup budget",
            """The source uses startup /startup,period1,failureThreshold10 and delay value3. The server may be Running while startup is still failing503.""",
            "The configured startup gate protects the declared slow-start fixture;actual transition time must be observed.",
        ),
        (
            "Compare two synthetic failures",
            """Case A:Ready=False,restartCount0,endpoint eligible false. Case B:liveness failures followed by restartCount1 with the same Pod UID.""",
            "A removes traffic without a direct restart;B records a container restart,not necessarily a new Pod.",
        ),
    ],
    [
        (
            "Name each question",
            "Explain the decision made by startup,readiness and liveness.",
            "Initialization gate,traffic eligibility and restart policy are distinguished.",
            "Describe the control action,not only the HTTP path.",
            "The same HTTP status can trigger different effects depending on which probe consumed it. The lesson is about those controller/kubelet policies rather than treating health as one undifferentiated Boolean.",
        ),
        (
            "Run the healthy delayed fixture",
            "Use the admitted source and record its actual bounded healthy result.",
            "Startup delay is configured3;controller/backend/client checks eventually establish the observed healthy baseline.",
            "Keep configured timing separate from observed timing.",
            "The fixture and probe are deliberately finite. A successful initial run supports that observed startup/readiness path under the qualified environment,but not a universal initialization duration or all later liveness behavior.",
        ),
        (
            "Trace readiness removal",
            "Analyze case A and identify what additional evidence would show recovery.",
            "No direct restart claim;new Ready/endpoint/client observations are required after repair.",
            "Restart count and Pod UID should remain explicit.",
            "A readiness failure can stop normal Service selection while the process remains alive. Recovery should be shown at the routing/application boundary,not inferred from the fact that the container never exited.",
        ),
        (
            "Trace liveness restart",
            "Analyze case B and distinguish restart from replacement.",
            "Same Pod UID with increased container restartCount.",
            "Compare both UID and restart count.",
            "Liveness can restart a container inside an existing Pod. Its ephemeral volumes may therefore have different lifetime behavior from a new Pod,which the next chapter examines.",
        ),
        (
            "Predict a wrong fixed path",
            "Compare /startup or /live with /missing in a scratch admitted configuration.",
            "The wrong path returns404;the actual bounded result and cleanup must be recorded rather than inventing a fixed timing.",
            "Use the same image and change only the path.",
            "The source remains inside the allowlist but requests a deliberately failing check. Depending on the observed window,the operation can show waiting,restarts or failure;the evidence should identify the phase and not overclaim a deterministic schedule.",
        ),
        (
            "Choose a production probe policy",
            "Explain why a downstream outage should not automatically restart every caller.",
            "A concrete design separates process-deadlock detection from traffic readiness and dependency behavior.",
            "Ask whether restarting can repair the failed condition.",
            "A liveness policy should target failures restart can plausibly resolve. Readiness can withhold traffic while preserving the process. The correct policy depends on application behavior and measured recovery evidence,not this fixture's three-second value.",
        ),
    ],
    startup,
    """
def main():
    readiness={'uid':'pod-a','ready':False,'restarts':0,'eligible':False}
    liveness={'uid':'pod-a','ready':False,'restarts':1,'eligible':False}
    assert readiness['uid']==liveness['uid'] and liveness['restarts']>readiness['restarts']
    assert not readiness['eligible'] and readiness['restarts']==0
    assert 3<1*10
    print('k8s-015 synthetic probe-policy checks passed; timing is not a live receipt')

if __name__ == "__main__":
    main()
""",
    browser=True,
    capability="fixed startup/liveness baseline plus separate stateful probe observations",
    refs=[
        "[Kubernetes probe semantics](https://kubernetes.io/docs/concepts/workloads/pods/probes/)"
    ],
)

pod = copy.deepcopy(hello()[0]["spec"]["template"]["spec"])
container = pod["containers"][0]
pod["securityContext"]["fsGroup"] = 65532
pod["restartPolicy"] = "OnFailure"
pod["activeDeadlineSeconds"] = 60
pod["volumes"] = [{"name": "work", "emptyDir": {"sizeLimit": "1Mi"}}]
base_container = {
    k: copy.deepcopy(v)
    for k, v in container.items()
    if k in {"image", "imagePullPolicy", "resources", "securityContext"}
}
init = {
    **copy.deepcopy(base_container),
    "name": "prepare",
    "command": [
        "python",
        "-c",
        "from pathlib import Path; import os; Path('/work/marker').write_text(os.environ['POD_UID'])",
    ],
    "env": [{"name": "POD_UID", "valueFrom": {"fieldRef": {"fieldPath": "metadata.uid"}}}],
    "volumeMounts": [{"name": "work", "mountPath": "/work"}],
}
app = {
    **copy.deepcopy(base_container),
    "name": "read",
    "command": [
        "python",
        "-c",
        "from pathlib import Path; p=Path('/work/attempt'); print(Path('/work/marker').read_text(),flush=True); first=not p.exists(); p.write_text('seen'); raise SystemExit(2 if first else 0)",
    ],
    "volumeMounts": [{"name": "work", "mountPath": "/work"}],
}
pod["initContainers"] = [init]
pod["containers"] = [app]
init_manifest = {
    "apiVersion": "v1",
    "kind": "Pod",
    "metadata": {"name": "init-demo", "labels": {"app": "init-demo"}},
    "spec": pod,
}
author(
    16,
    """An ordinary init container completes before the application containers start. It can prepare a synthetic file or validate a prerequisite. An emptyDir volume belongs to the Pod lifetime and can be shared by its containers. Restarting an application container normally preserves that volume,while replacing the Pod creates a different emptyDir.

The supplied real Pod manifest is an explicit host-lab example. The browser adapter does not admit initContainers,emptyDir or arbitrary command bodies. A teacher must review the exact fixed commands and provide the owned capability before live use. The finite example writes the Pod UID into a marker,then deliberately makes the reader fail once and succeed on its next container attempt.

The marker makes lifetime observable:it matches the same Pod UID across the application restart and changes when a new Pod is created. A constant hello marker alone would be weaker evidence because a new init container could recreate identical bytes after replacement.""",
    [
        (
            "Trace initialization and shared-volume ownership",
            """The init container prepare mounts work at /work and writes marker using the downward-API POD_UID value. The application read mounts the same Pod volume. fsGroup65532 gives the nonroot process the intended volume access in the scoped fixture;readOnlyRootFilesystem still protects the image filesystem but does not make every mounted volume read-only.

restartPolicy OnFailure allows the deliberately failing application container to restart. The first attempt writes an attempt flag and exits2;the next sees that flag and exits0. The completed ordinary init container is not rerun merely because that application container restarts. The Pod active deadline60 bounds the host experiment.

Do not confuse this ordinary init sequence with a restartable sidecar-style init container,which has different lifecycle semantics. The manifest intentionally uses a finite ordinary init command and no external network or real data.""",
        ),
        (
            "Observe container restart versus Pod replacement",
            """Record Pod UID,init termination state,application restart count and the marker printed by each attempt. Within one Pod,the marker should remain that Pod UID and the attempt flag should survive. A new Pod has a new UID and a fresh volume;its init step creates a new marker and its application begins the finite sequence again.

A Pod name can be reused after deletion,so name equality is not evidence of volume continuity. A Deployment replacement also creates a new Pod even if its template is unchanged. This is why emptyDir is appropriate for scratch/shared per-Pod work,not durable data that must survive replacement.

The host must delete only the exact recorded Pod UID and observe completion/cleanup within its deadline. No broad hostPath or personal directory is mounted. The example\'s write access is confined to a small synthetic emptyDir.""",
        ),
        (
            "Diagnose ordering and permission failures",
            """If the init container fails,the application may never start;inspect initContainerStatuses rather than expecting application logs. If the marker cannot be written,inspect the volume mount and nonroot permissions before relaxing the security context globally. A missing file in the application can indicate a different mount name or path.

The offline script checks a lifetime model only. A live claim needs the actual UID and restart/log evidence. Neither a persisted marker in emptyDir nor a successful Pod restart is a backup or proof of PVC behavior.""",
        ),
    ],
    [
        (
            "Read a finite init/app sequence",
            """The JSON example uses an init writer and an application reader sharing /work. The writer stores metadata.uid;the reader records one attempt flag,exits2 once and then exits0.""",
            "Application start follows successful initialization;the marker and attempt flag are confined to the Pod volume.",
        ),
        (
            "Compare lifetime traces",
            """Synthetic Pod UID pod-a prints marker pod-a before and after one application restart. Replacement Pod UID pod-b prints marker pod-b and begins with a fresh attempt flag.""",
            "Container restart preserves the same Pod volume;Pod replacement creates a different volume lifetime.",
        ),
    ],
    [
        (
            "Draw container order",
            "Identify init completion as a prerequisite for the application reader.",
            "prepare completes before read starts.",
            "Inspect initContainerStatuses separately from application statuses.",
            "The init container supplies the file dependency. If it never completes successfully,the application cannot demonstrate the read path. The ordering is a Kubernetes lifecycle contract,not a sleep inserted into application code.",
        ),
        (
            "Trace the shared volume",
            "Match volume name work across Pod,init and application mounts.",
            "Both containers access the same /work emptyDir within one Pod.",
            "Volume identity is separate from container filesystem identity.",
            "The mount links the containers to one Pod-owned volume. Read-only root filesystems do not prohibit a separately admitted writable volume. The scope is still synthetic and bounded,with no host personal path.",
        ),
        (
            "Observe one application restart",
            "Use the exact teacher-provided finite fixture and retain UID,marker and restart count.",
            "Same Pod UID/marker across the failed first and successful next application attempt.",
            "The attempt flag is evidence that the volume survived the container restart.",
            "The first application exit2 triggers OnFailure restart. Its marker and flag remain in the Pod volume,so the next attempt can distinguish itself. Actual timing and status must be observed rather than copied from this trace.",
        ),
        (
            "Compare a new Pod",
            "Replace only the recorded owned Pod under the host capability.",
            "New Pod UID,new marker and fresh attempt sequence.",
            "A reused name does not preserve emptyDir.",
            "The init step writes the new UID,which differentiates recreated bytes from persistent storage. This avoids falsely claiming that a constant marker survived when it was merely generated again.",
        ),
        (
            "Diagnose an init failure",
            "Review a missing mount or denied write in prepare.",
            "Application absence is explained by init failure;the smallest mount/permission repair is identified.",
            "Do not begin with application readiness or loosen all privileges.",
            "The first failed stage is initialization. Correct the declared shared path or intended nonroot access in the owned fixture,then verify the init exit and application output. Broad privilege changes are not a justified diagnosis.",
        ),
        (
            "State the storage limit",
            "Explain why this marker is neither persistent storage nor a backup.",
            "emptyDir lifetime is tied to the Pod;durability and independent recovery require later storage/backup contracts.",
            "Ask what happens when the Pod object is replaced.",
            "A successful container restart proves only continuity within that Pod lifetime. A backup must survive the relevant failure independently and be restored/verified. The example intentionally stops short of that claim.",
        ),
    ],
    [init_manifest],
    """
def main():
    volume={'marker':'pod-a','attempt':'seen'}
    after_restart=volume
    assert after_restart['marker']=='pod-a' and after_restart['attempt']=='seen'
    replacement={'marker':'pod-b'}
    assert replacement['marker']!=volume['marker'] and 'attempt' not in replacement
    states=['init-complete','app-exit-2','app-restart','app-exit-0']
    assert states.index('init-complete')<states.index('app-restart')
    print('k8s-016 synthetic init/emptyDir lifetime checks passed; no Pod created')

if __name__ == "__main__":
    main()
""",
    capability="reviewed finite init/emptyDir Pod host lab",
    refs=[
        "[Kubernetes init containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)",
        "[Kubernetes volumes](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir)",
    ],
)

author(
    17,
    """A container security context describes requested process and filesystem restrictions. Running as a nonroot UID,dropping capabilities,disallowing privilege escalation and using a read-only root filesystem reduce different risks. Pod Security admission is a separate policy that can reject workloads not meeting a chosen standard. Neither a namespace name nor one security field creates complete isolation by itself.

The allowed browser workload uses runAsUser65532,runAsNonRoot true,RuntimeDefault seccomp,allowPrivilegeEscalation false,readOnlyRootFilesystem true and capabilities.drop ALL. Service-account token mounting is disabled. The parser rejects attempts to replace these values or add host namespaces,privileged mode and unapproved mounts.

This lesson distinguishes source checks,admission decisions and actual runtime identity. The configured UID is desired process identity;an observed runtime UID requires a qualified fixture or host observation. The current app\'s admitted baseline and ownership checks do not automatically prove every host/kernel security property.""",
    [
        (
            "Separate controls by mechanism",
            """runAsUser selects a numeric process UID. runAsNonRoot requests a nonroot requirement. allowPrivilegeEscalation false controls whether execution can gain additional privileges through mechanisms such as setuid. Dropped capabilities remove specific privileged kernel operations. Seccomp filters system-call behavior according to the selected profile. Read-only root filesystem protects the image layer but mounted volumes have their own access modes.

These fields interact with the image and node runtime. A nonroot application still needs appropriate access to any admitted writable volume. A source that asks for a UID does not prove that every external service or data path is authorized. Keep application permissions and Kubernetes API permissions as separate concerns.

The course\'s strict allowlist is narrower than general Kubernetes. An unsupported field can be rejected by the broker before Pod Security admission ever evaluates it. Report that phase accurately.""",
        ),
        (
            "Understand Pod Security admission evidence",
            """A host can label the owned namespace with a chosen Pod Security enforcement level and version. That is a host preparation decision,not something the learner worker may change. A rejected privileged Pod should include an admission reason tied to the policy. A parser refusal is useful protection but is not proof that the API server\'s admission plugin enforced the same rule.

Compare an allowed restricted-compatible fixture with negative privileged/hostPath/hostNetwork examples only in the declared disposable scope. Preserve the exact source change and rejection phase. Do not create a privileged workload simply to inspect it after acceptance;the intended negative case should fail before execution.

The normal browser source provides a positive fixed workload. Host admission tests need their own receipt identifying policy configuration and observed allow/deny results.""",
        ),
        (
            "Avoid security overclaims",
            """A read-only filesystem is not a ban on all writes when writable volumes exist. Nonroot is not an authorization policy for another namespace. RBAC does not govern every packet sent by a workload. A container shares a node kernel and is not automatically a separate virtual machine.

State which control rejects which behavior and what remains untested. If a negative source is refused locally,do not claim that a kernel-level action was attempted or blocked at runtime. The evidence level is part of the security explanation.""",
        ),
    ],
    [
        (
            "Read the fixed context",
            "```yaml\n"
            + yaml.safe_dump(
                hello()[0]["spec"]["template"]["spec"]["securityContext"], sort_keys=False
            )
            + "```",
            "The requested process identity is nonroot UID65532 with RuntimeDefault seccomp.",
        ),
        (
            "Classify two denials",
            """Case A:broker rejects privileged:true before API create. Case B:an explicitly prepared host admission policy rejects a privileged Pod request with a policy reason.""",
            "Both protect a boundary,but only B is evidence of server-side admission enforcement.",
        ),
    ],
    [
        (
            "Map each control",
            "Explain UID,capabilities,privilege escalation,seccomp and root filesystem fields.",
            "Each field is connected to its specific mechanism rather than one generic secure label.",
            "Separate process identity,syscalls,privilege transitions and storage access.",
            "The controls reduce different attack or error surfaces. Understanding their roles helps diagnose a legitimate application permission issue without removing every restriction.",
        ),
        (
            "Run the allowed baseline",
            "Use the fixed nonroot source in a qualified operation.",
            "Accepted source,observed workload readiness and owned cleanup are recorded.",
            "Keep configured UID and observed runtime identity as separate evidence.",
            "The app proves its bounded workload checks. A runtime UID claim needs a dedicated observed field or fixed fixture result,not merely the YAML value. Do not broaden that receipt into a host-isolation guarantee.",
        ),
        (
            "Reject a privileged mutation",
            "Change allowPrivilegeEscalation or add privileged:true in a scratch source.",
            "Parser refusal before cluster mutation.",
            "Inspect the allowlist error and absence of a create receipt.",
            "The course protects the operation at source admission. This is a valid negative result even though no privileged process ran. Preserve the phase rather than inventing a server rejection event.",
        ),
        (
            "Reject host access",
            "Review hostPath,hostNetwork and hostPID variants.",
            "All are outside the admitted browser contract.",
            "Look for Pod-level fields as well as container security fields.",
            "A secure-looking container context does not neutralize a host namespace or mount. The parser rejects those requests rather than trusting a learner to choose a harmless path.",
        ),
        (
            "Observe a host policy separately",
            "With a policy-qualified host fixture,compare allowed and denied API requests.",
            "Policy version,namespace UID and actual admission reason accompany the result.",
            "Do not equate a local parser with the server's policy engine.",
            "The host capability must establish the admission configuration. A successful or denied API request then provides evidence about that policy under the current target. The worker receives no permission to relabel the namespace or install policy.",
        ),
        (
            "Write a bounded threat statement",
            "Describe what the fixed controls address and one remaining boundary requiring another control.",
            "For example,RBAC controls API access while network policy or application auth addresses different paths.",
            "Avoid calling one field a complete sandbox.",
            "A useful security explanation names mechanisms and limits. It should distinguish desired configuration,admission,container runtime behavior and application authorization rather than collapse them into an unsupported safe/unsafe binary.",
        ),
    ],
    hello(),
    """
def main():
    pod={'runAsNonRoot':True,'runAsUser':65532,'seccompProfile':{'type':'RuntimeDefault'}}
    container={'allowPrivilegeEscalation':False,'readOnlyRootFilesystem':True,'capabilities':{'drop':['ALL']}}
    assert pod['runAsUser']!=0 and pod['runAsNonRoot']
    assert not container['allowPrivilegeEscalation'] and container['capabilities']['drop']==['ALL']
    assert {'hostPath','hostNetwork','hostPID'}.isdisjoint({'containers','securityContext'})
    print('k8s-017 synthetic security-control checks passed; runtime identity is separate evidence')

if __name__ == "__main__":
    main()
""",
    browser=True,
    capability="fixed restricted-compatible workload; separate host admission/runtime identity checks",
    refs=[
        "[Kubernetes security context](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)",
        "[Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)",
    ],
)

reader_role = {
    "apiVersion": "rbac.authorization.k8s.io/v1",
    "kind": "Role",
    "metadata": {"name": "lesson-pod-reader"},
    "rules": [{"apiGroups": [""], "resources": ["pods"], "verbs": ["get", "list"]}],
}
binding = {
    "apiVersion": "rbac.authorization.k8s.io/v1",
    "kind": "RoleBinding",
    "metadata": {"name": "lesson-pod-reader"},
    "subjects": [{"kind": "ServiceAccount", "name": "lesson-reader", "namespace": "lesson-auth"}],
    "roleRef": {
        "apiGroup": "rbac.authorization.k8s.io",
        "kind": "Role",
        "name": "lesson-pod-reader",
    },
}
author(
    18,
    """A ServiceAccount is a Kubernetes workload identity,not a human login name and not a secret value. A RoleBinding grants that identity a defined set of API actions in a scope. A token authenticates the identity;it does not by itself define what the identity is authorized to do.

The course worker uses a short-lived scoped credential held outside learner storage. Workload Pods have automatic service-account token mounting disabled because the synthetic application does not need Kubernetes API access. The worker\'s own permission to create a fixed workload is separate from any permission granted to the workload process.

This reading/host-observation lesson inspects a real Role and RoleBinding example and a positive/negative authorization matrix. The normal learner identity cannot create arbitrary RBAC objects,read Secrets or widen its own privileges. The manifest example illustrates the relationship;it is not a command to install a new grant through the browser.""",
    [
        (
            "Read subject,role and binding scope",
            """The Role permits get/list on Pods. The RoleBinding references that Role and names a ServiceAccount subject. The binding\'s namespace determines where the Role grant applies;the subject namespace identifies where that ServiceAccount identity exists. Those two namespaces need not be the same in a general design,and confusing them can grant the wrong identity access.

The literal lesson-auth subject namespace in the synthetic example is an explanatory fixture,not the current private worker namespace. A live host preparation must substitute and verify its own exact identity receipt. The learner does not choose a different namespace to escape a refusal.

RBAC is additive,and effective privileges can come from multiple bindings. The example lacks secrets,roles,clusterroles and exec permissions. Confirm actual effective actions with the owned identity rather than assuming this one file is the entire policy universe.""",
        ),
        (
            "Handle credentials and TokenRequest lifetimes",
            """A TokenRequest can issue a bounded service-account token for a specified audience and expiration. The course preparation checks the returned expiration and stores the scoped kubeconfig privately. Token bytes,client keys and full kubeconfig contents do not belong in progress,examples or screenshots.

Prepare the owned session immediately before running the lab,after images and tools are ready. Its credential lasts fifteen minutes in the current course setup. An expired lease or one lacking work-plus-cleanup reserve should be refused. Release only the exact recorded owned session and prepare a fresh one through the host workflow;do not extend access by falling back to ambient credentials.

A mounted workload token would increase what the application can attempt. Keeping automountServiceAccountToken:false removes an unnecessary default credential path for this fixture. It does not replace application authentication or network controls.""",
        ),
        (
            "Interpret authorization checks carefully",
            """A yes/no self-authorization result describes a requested action for an identity at a point in time. It does not prove that a later API request will pass every admission or object-state check. Conversely,a denied Secret read is expected in this lab and should not trigger a broader Role.

Use nonsecret request tuples and results in the worksheet. Do not impersonate a more privileged user,print tokens or copy a real Secret to demonstrate that access is absent. The offline matrix is a model of the intended policy,not a live control-plane response.""",
        ),
    ],
    [
        (
            "Read a binding relationship",
            "```yaml\n" + yaml.safe_dump(binding, sort_keys=False) + "```",
            "The named ServiceAccount subject receives the referenced Role only through the binding's actual namespace scope.",
        ),
        (
            "Compare intended effective actions",
            """Synthetic matrix:own-namespace get Pod=yes;other-namespace get Pod=no;get Secret=no;create Role=no;create ClusterRole=no. No token value is included.""",
            "The matrix expresses least-privilege expectations to verify with the actual owned identity.",
        ),
    ],
    [
        (
            "Identify the ServiceAccount",
            "Separate identity name/namespace from token contents and Role rules.",
            "A nonsecret identity record is distinct from credential bytes and permissions.",
            "Authentication and authorization answer different questions.",
            "A token proves possession of an identity credential under the server's validation rules. The RoleBindings determine what that identity may do. Recording the identity does not require exposing the token.",
        ),
        (
            "Trace the binding scope",
            "Explain the subject namespace versus the RoleBinding namespace.",
            "Subject identifies the ServiceAccount;binding scope determines the namespaced grant.",
            "Draw both sides of roleRef and subjects.",
            "The fields are easy to confuse because both can contain namespace names. A live setup must use exact provisioned identities and verify effective behavior. The synthetic lesson-auth name is not an ambient target.",
        ),
        (
            "Predict allowed and denied requests",
            "Fill the five-action authorization matrix.",
            "Only the intended own-namespace Pod reads are allowed;Secrets and privilege changes denied.",
            "Read resource,verb and namespace for every row.",
            "A narrow role does not grant adjacent actions by implication. The negative checks are part of the successful access-boundary demonstration,not errors to fix by adding wildcard permissions.",
        ),
        (
            "Protect workload credentials",
            "Inspect automountServiceAccountToken:false in the application source.",
            "The synthetic workload does not receive an automatic API token mount.",
            "The worker and the application are different identities/process boundaries.",
            "The host worker needs scoped API access to manage the fixture. The application itself does not,so mounting a token would be unnecessary exposure. This control does not prove all possible credential paths are absent in arbitrary workloads.",
        ),
        (
            "Rehearse expiry handling",
            "Explain the sequence when a prepared fifteen-minute lease expires before Run.",
            "Guard refuses;exact owned session is released and a fresh session is prepared immediately before use.",
            "Build/download before preparing the short-lived lease.",
            "The refusal preserves the identity and cleanup budget. An operational retry should not modify the runtime to ignore expiry. Keep release bounded to the recorded cluster/container/namespace identity and preserve learner source.",
        ),
        (
            "Record live effective evidence",
            "With the named host capability,retain positive/negative self-authorization outcomes without credentials.",
            "Identity,target,verb/resource,result and time are recorded;token/kubeconfig contents are excluded.",
            "A static Role prediction and a server answer are different artifacts.",
            "The live result supports the effective policy claim for that target and moment. It does not authorize future operations beyond the lease or prove that all admission/runtime checks will succeed.",
        ),
    ],
    [reader_role, binding],
    """
def main():
    grants={('own','pods','get'),('own','pods','list')}
    assert ('own','pods','get') in grants
    for request in [('other','pods','get'),('own','secrets','get'),('own','roles','create'),('cluster','clusterroles','create')]:assert request not in grants
    workload={'automountServiceAccountToken':False}
    assert workload['automountServiceAccountToken'] is False
    assert 900>60+15+5 and 30<60+15+5
    print('k8s-018 synthetic RBAC/expiry checks passed; no token or API response exposed')

if __name__ == "__main__":
    main()
""",
    capability="scoped ServiceAccount authorization observation",
    refs=[
        "[Kubernetes ServiceAccounts](https://kubernetes.io/docs/concepts/security/service-accounts/)",
        "[Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)",
    ],
)

dummy = "DUMMY_LESSON_ONLY"
secret = {
    "apiVersion": "v1",
    "kind": "Secret",
    "metadata": {"name": "synthetic-message"},
    "type": "Opaque",
    "data": {"lesson-message": base64.b64encode(dummy.encode()).decode()},
}
author(
    19,
    """A Secret is a Kubernetes object for data that requires restricted handling. Its data field uses base64 encoding,which is a reversible representation rather than encryption. Access control,encryption-at-rest configuration,transport security and application handling are separate controls. Verify those actual controls instead of inferring confidentiality from the object kind.

This lesson uses only the public markers DUMMY_LESSON_ONLY and DUMMY_LESSON_ROTATED. The current browser worker has no Secret permission and does not accept Secret manifests or Secret references. Live mount behavior is available only through a teacher-provided synthetic fixture in a separate scoped host capability. No real credential is needed or should be collected.

Configuration lifetime still matters. A Secret-derived environment value is captured when a process starts. A projected Secret file can refresh asynchronously,but application reload behavior determines when the process uses new bytes. Encoding does not change those lifecycle semantics.""",
    [
        (
            "Decode an explicitly synthetic value",
            """The example Opaque Secret has one key,lesson-message. Decoding its data recovers the exact dummy string. That exercise demonstrates encoding only. It does not show that a real Secret is safe to print,export or place in a Git repository.

General Kubernetes also supports stringData as a convenience input,with different server-side handling. Regardless of representation,the value needs an access and retention policy. The course deliberately keeps the normal worker unable to read Secrets,so an authorization denial is the expected boundary.

A manifest containing dummy data can be reviewed offline. A teacher must own any live synthetic Secret and its cleanup. Do not replace the dummy value with a personal token to make the example feel realistic.""",
        ),
        (
            "Separate API exposure,mount and application reload",
            """Who can read a Secret API object is different from who can create a Pod that mounts it. Pod-creation privileges can expose data indirectly in some namespace designs,so a complete access review cannot look only at get secrets. The course\'s fixed manifest allowlist prevents arbitrary Secret mounts as well as denying direct Secret reads.

For a projected file,the kubelet can update the mounted content after a source change. A subPath mount has different update behavior,and a process may cache the old contents. Environment variables require a new process to consume a changed value. A live experiment should record API version,file observation and application use separately.

The synthetic fixture should avoid putting values in command-line arguments or routine logs. Evidence can record an equality result or a hash of an explicitly nonsecret marker rather than copy sensitive bytes. A hash of a low-entropy real secret is not automatically safe disclosure,so that shortcut is not generalized here.""",
        ),
        (
            "Observe a real consuming application",
            """The [teacher fixture](../fixtures/secret-observer/README.md) contains a complete Python observer, a generated Secret/ConfigMap/Deployment manifest and a bounded teacher runner. Its program reads the environment once, opens the projected file on each observation and changes its in-memory cache only after POST /reload. It returns labels initial or rotated, never marker bytes. The projected volume mounts the whole directory without subPath, so a later path open can see a refreshed projection.

The expected sequence is initial/initial/initial, then initial/rotated/initial after actual file observation, then initial/rotated/rotated after explicit reload. Deleting the exact recorded Pod UID allows its controller to create a replacement whose environment/file/cache are all rotated. Pod UID and a process boot ID distinguish a replacement from a same-Pod container restart. These are predictions until the teacher records the actual responses.

The fixed runner requires an explicit fresh owned session and separately uses its private teacher context. It checks namespace UID, object nonce and the Deployment to ReplicaSet to Pod owner chain; refuses preexisting names; tests Secret UID and resourceVersion before rotation; and cleans only recorded object UIDs. No ordinary worker Role or browser capability is widened. The fixture README provides POSIX and PowerShell commands, bounded waits, troubleshooting and cleanup evidence. A successful HTTP response without identity checks would not establish that the intended process was observed.""",
        ),
        (
            "Avoid confusing encoding with protection",
            """Base64 decoding is intentionally easy. A successful round trip proves representation fidelity,not confidentiality. A mounted file\'s restrictive mode does not establish server-side encryption,and an encrypted data store does not repair excessive API permissions.

The offline check makes no Secret API request. The normal browser refusal must not be bypassed through another namespace,exec command or ambient administrator context. Keep the synthetic host-lab capability and its observations explicit.""",
        ),
    ],
    [
        (
            "Inspect the dummy Secret",
            "```yaml\n" + yaml.safe_dump(secret, sort_keys=False) + "```",
            "Decoding lesson-message yields exactly DUMMY_LESSON_ONLY;the bytes are intentionally synthetic.",
        ),
        (
            "Trace a projected update",
            """Synthetic sequence:source value A changes to B;existing environment remains A;projected file is later observed as B;application still returns A until its reload path is invoked.""",
            "Projection and application consumption are separate stages,and no exact refresh second is implied.",
        ),
        (
            "Read the actual three-channel response",
            """The observer response has five fields: pod_uid, boot_id, environment, projected_file and application_cache. Suppose the first response is Pod P1, boot B1 and initial/initial/initial. After the Secret patch, the teacher polls the file label rather than assuming a fixed delay. A later response P1/B1 with initial/rotated/initial proves that this process has observed the new projection while retaining both its original environment and cached value. POST /reload returns P1/B1 with initial/rotated/rotated. Finally a replacement P2/B2 reports rotated/rotated/rotated. The exact JSON comes from the real fixture, while these P1/B1 names are explanatory placeholders.

Follow the [complete fixture workflow](../fixtures/secret-observer/README.md) only when the separately provisioned teacher capability exists. Retain evidence.json with all four stages, source hashes and cleanup_confirmed. The normal browser pad continues to refuse this manifest. The local fixture tests use temporary files and a loopback server, so they do not establish real kubelet projection.""",
            "The same-process stages retain both identities; replacement changes both. Label changes and cleanup are independently checked.",
        ),
    ],
    [
        (
            "Decode the authored marker",
            "Base64-decode only the supplied lesson-message value.",
            "Exact DUMMY_LESSON_ONLY round trip.",
            "Use the encoded fixture,not a real Secret API read.",
            "The result demonstrates that base64 is reversible. It should not be described as decryption or as proof of a security boundary. The literal marker is intentionally harmless teaching data.",
        ),
        (
            "Name the security controls",
            "Separate encoding,RBAC,encryption at rest,transport and application handling.",
            "Five distinct mechanisms and their evidence are described.",
            "Ask what threat each control addresses.",
            "A representation format cannot replace authorization or storage protection. The actual cluster configuration and permitted identities determine exposure. The worksheet should not infer unobserved controls from the Secret kind.",
        ),
        (
            "Verify the normal-worker denial",
            "Review direct Secret access and arbitrary Secret mount attempts against the current worker contract.",
            "Both are outside the normal operation;no privilege broadening or real-value collection occurs.",
            "Creation of a consuming Pod can be an indirect access path in general Kubernetes.",
            "The broker combines scoped RBAC with a closed workload schema. This prevents treating denied API read as sufficient while allowing an arbitrary mounting workload. A host synthetic fixture is a separately provisioned teaching capability.",
        ),
        (
            "Compare environment and projected file",
            "Predict the update trace for an existing process.",
            "Environment A persists;file may become B after observed projection;application use depends on reload.",
            "Do not collapse source update and process observation.",
            "The same lifecycle distinction as ConfigMaps applies. A process-start snapshot is not rewritten,and a refreshed file can remain unused by a caching application. Report actual observations or label the trace synthetic.",
        ),
        (
            "Design nonsecret evidence",
            "Specify what to retain from a synthetic mount test without copying real credentials.",
            "Source/Pod identity,access outcome,reload behavior and synthetic equality evidence.",
            "A real secret value is not required to prove the mechanism.",
            "The record should support the lifecycle and access claim while minimizing exposure. Do not generalize a dummy-marker hash into a safe way to publish low-entropy real secrets.",
        ),
        (
            "Clean up the synthetic fixture",
            "Describe exact owned Secret/workload cleanup under the host capability.",
            "Only recorded synthetic object UIDs are removed;normal worker permissions remain unchanged.",
            "Names can be reused and host capability is separate.",
            "The host owns the temporary fixture and its data-retention policy. Cleanup must preserve replacements and unrelated objects. A missing worksheet or stopped browser is not evidence that the Secret was deleted.",
        ),
    ],
    json.loads((BASE / "fixtures/secret-observer/manifest.json").read_text())["items"],
    """
import base64

def main():
    dummy='DUMMY_LESSON_ONLY';encoded=base64.b64encode(dummy.encode()).decode()
    assert base64.b64decode(encoded,validate=True).decode()==dummy
    before={'environment':'A','file':'A','application':'A'}
    projected={**before,'file':'B'}
    assert projected['environment']=='A' and projected['application']=='A' and projected['file']=='B'
    print('k8s-019 synthetic encoding/lifetime checks passed; no Secret API access')

if __name__ == "__main__":
    main()
""",
    capability="teacher-owned synthetic Secret mount observation, unavailable to normal worker",
    refs=["[Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)"],
)

author(
    20,
    """Network diagnosis should proceed through distinct layers:the client\'s namespace/DNS context,name resolution,Service selection and port mapping,transport connection,and application response. A failure at one layer can produce a similar user-visible symptom to another,but the evidence needed to distinguish them differs.

The browser\'s positive fixture uses an in-cluster client to reach hello on port8080 and request /version. It does not publish a host port or depend on an external network service. Wrong-port,DNS and arbitrary-route experiments are separate scoped host fixtures because the browser client command and Service port are fixed.

A successful HTTP404 already shows that some HTTP server answered;it is not a DNS failure. A timeout after name resolution leaves several transport/backend possibilities and should not be labeled NetworkPolicy denial without enforcement evidence. Use the most specific observation available and retain uncertainty where the evidence does not identify a unique cause.""",
    [
        (
            "Follow the Service name and backend path",
            """A short Service name is interpreted in the client\'s namespace context. A fully qualified cluster name includes Service,namespace and cluster domain,whose actual value belongs to the environment configuration. Do not assume a name from another namespace resolves to the intended object.

After resolution,the Service\'s selector and EndpointSlices identify eligible backends. Its client-facing port maps to a target port on those Pods. DNS can succeed while the backend set is empty or the port is wrong. The owned verifier therefore compares identities and uses a fresh application request.

The fixture client has a bounded timeout and a small response-size limit. It accepts only the local synthetic hostname/path contract,so it cannot be repurposed to probe arbitrary external hosts. A source refusal for an unsupported URL is different from an observed network timeout.""",
        ),
        (
            "Classify a layered evidence table",
            """Synthetic case A returns NXDOMAIN before a connection attempt. Case B resolves an address but cannot establish a connection within its budget. Case C returns HTTP404. Case D returns HTTP200 with the wrong version body. These correspond to name-resolution failure,an unresolved transport/backend problem,route mismatch and application-contract mismatch respectively.

For case B,inspect Service ports,ready endpoint identities and the declared network-policy capability before choosing a cause. A refused connection and a timeout can have different immediate meanings,but neither alone proves a specific CNI policy. For case C,compare the requested path with the application\'s documented routes.

A response from an unrelated endpoint is not success. Keep the source/Service/Pod identities and exact expected body in the packet so a stale or wrong service cannot satisfy a generic HTTP200 check.""",
        ),
        (
            "Use bounded local evidence",
            """Do not scan unrelated addresses or use an external endpoint to test a local lesson. A host port-forward is another host capability with its own scope and lifecycle;it is not implied by a ClusterIP Service. The current browser path uses the in-cluster client instead.

A positive one-shot request establishes only its observed path and payload. Production availability,network isolation and DNS reliability require broader evidence. A negative case should remain within a finite timeout and cleanup scope.""",
        ),
    ],
    [
        (
            "Trace the positive local path",
            """Client in the leased namespace resolves hello,connects to8080,routes through the Service to an owned Ready Pod and receives ds60-fixture-v1 from /version.""",
            "Name,routing and exact application response are separate observed checks in one bounded path.",
        ),
        (
            "Compare404 and wrong payload",
            """A404 from /missing proves an HTTP server responded but not the desired route. A200 with another version proves transport but fails the application identity contract.""",
            "Neither should be called successful version verification or a DNS failure.",
        ),
    ],
    [
        (
            "Name the layers",
            "Draw client namespace,DNS,Service,EndpointSlice,Pod port and HTTP route.",
            "Each layer has a distinct observation and possible failure.",
            "Start before the request reaches the application.",
            "The layered model prevents changing application code for a name-resolution failure or blaming DNS for a returned404. It also identifies which evidence is still missing when a timeout is ambiguous.",
        ),
        (
            "Verify the allowed path",
            "Run the fixed Deployment/Service source under a qualified lease.",
            "Owned backend identity and exact /version response pass,with cleanup.",
            "A generic HTTP200 is weaker than the fixed version contract.",
            "The client checks the intended local fixture route independently of readiness. The observed result is bounded to that source and target and does not establish arbitrary network connectivity.",
        ),
        (
            "Classify NXDOMAIN",
            "Interpret a host-provided failed name-resolution trace.",
            "Investigate name,namespace and DNS context before backend application state.",
            "No resolved destination means later layers were not established.",
            "The trace should include the requested name and client context. A typo or namespace mismatch differs from DNS infrastructure failure,so retain the actual response rather than assuming the broadest cause.",
        ),
        (
            "Classify a transport failure",
            "Interpret resolution success followed by a bounded connection failure.",
            "Inspect ports,eligible endpoints and qualified policy evidence;cause remains conditional until discriminated.",
            "Do not infer a NetworkPolicy from timeout alone.",
            "Several mechanisms can produce the symptom. The next check should distinguish them within the owned target,not widen the scan or disable controls. Policy enforcement needs its own positive/negative traffic comparison.",
        ),
        (
            "Classify HTTP failures",
            "Compare404 at /missing and200 with a wrong version.",
            "Route mismatch versus application-contract mismatch.",
            "The response proves some earlier layers succeeded.",
            "A returned status and body provide more specific evidence than a generic unavailable report. The correct repair depends on whether the requested route or the responding application identity is wrong.",
        ),
        (
            "Design a finite host transfer",
            "Specify a wrong-port or cross-namespace test only under a named host capability.",
            "Explicit target,allowed client,timeout,expected layer failure and cleanup are recorded.",
            "The browser fixed client is not an arbitrary network tool.",
            "A transfer exercise can broaden understanding without broadening the worker allowlist. It needs an owned scope and actual observations;the worksheet should leave execution unavailable when that capability is absent.",
        ),
    ],
    hello(True),
    """
def classify(trace):
    if trace.get('dns')=='NXDOMAIN':return 'name-resolution'
    if trace.get('connected') is False:return 'transport-or-backend-unresolved'
    if trace.get('http')==404:return 'route'
    if trace.get('http')==200 and trace.get('body')!='ds60-fixture-v1':return 'application-contract'
    return 'insufficient-evidence'

def main():
    traces=[{'dns':'NXDOMAIN'},{'dns':'resolved','connected':False},{'http':404},{'http':200,'body':'wrong'}]
    assert [classify(x) for x in traces]==['name-resolution','transport-or-backend-unresolved','route','application-contract']
    print('k8s-020 synthetic layered-diagnosis checks passed; no network probes performed')

if __name__ == "__main__":
    main()
""",
    browser=True,
    capability="fixed internal version-client path; separate bounded DNS/port host probes",
    refs=[
        "[Kubernetes Service DNS](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)",
        "[Kubernetes Services](https://kubernetes.io/docs/concepts/services-networking/service/)",
    ],
)
