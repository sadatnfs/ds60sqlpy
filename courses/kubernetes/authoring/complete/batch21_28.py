from author import author,hello,fixture,BASE
import copy,json,yaml

np_deny={'apiVersion':'networking.k8s.io/v1','kind':'NetworkPolicy','metadata':{'name':'hello-deny-ingress'},'spec':{'podSelector':{'matchLabels':{'app':'hello'}},'policyTypes':['Ingress']}}
np_allow={'apiVersion':'networking.k8s.io/v1','kind':'NetworkPolicy','metadata':{'name':'hello-allow-client'},'spec':{'podSelector':{'matchLabels':{'app':'hello'}},'policyTypes':['Ingress'],'ingress':[{'from':[{'podSelector':{'matchLabels':{'role':'lesson-client'}}}],'ports':[{'protocol':'TCP','port':8080}]}]}}
author(21,
'''A NetworkPolicy describes allowed traffic relationships for selected Pods when the cluster networking implementation enforces it. Creating the API object is not evidence that packets are filtered. The course therefore requires a separately qualified policy-capable CNI and before/after client observations for this host lab.

The example isolates ingress to app=hello and then allows TCP8080 from same-namespace Pods labeled role=lesson-client. Policies are additive:the allowed traffic is the union of applicable allow rules. A deny-all ingress policy plus a matching allow policy does not mean the deny rule overrides the allow. Egress isolation is a separate direction and is not enabled by this ingress-only example.

The normal browser adapter does not admit NetworkPolicy or arbitrary client labels. Its basic hello success cannot establish isolation. This worksheet uses real policy manifests and a synthetic traffic matrix until an exclusive policy-enabled lease supplies the required live capability.''',
[
('Read selectors and rule composition','''spec.podSelector chooses destination Pods governed by this policy. In an ingress peer,a podSelector without a namespaceSelector refers to Pods in the policy\'s namespace. A peer containing both namespaceSelector and podSelector combines them,while separate entries in the from list are alternatives. Confusing those shapes can allow more traffic than intended.

policyTypes declares which traffic directions are isolated. An empty ingress list for selected Pods allows no ingress through this policy,but other applicable policies can still allow traffic. Both source egress and destination ingress policies may need to permit a connection when both ends are isolated.

The port rule is TCP8080,matching the application path. DNS egress is not blocked by this ingress-only example. Do not copy a generic default-deny-both-directions manifest and assume name resolution will remain available without an explicit design.'''),
('Prove enforcement with paired controls','''Before policy application,both synthetic clients should reach the same healthy backend. After isolation and the explicit allow,only the labeled permitted client should succeed;the other should fail within a bounded timeout. The allowed path is a control showing that the service did not simply stop working for everyone.

If both still succeed,investigate policy support,selectors and direction. If both fail,inspect application readiness,ports and the allow rule before declaring enforcement successful. Retain CNI identity/capability,policy UID and actual client results. A timeout alone does not uniquely identify policy denial.

Use only approved local client/server fixtures in the owned namespace. The host provides the CNI capability;the learner does not install a plugin,modify node networking or test unrelated tenants.'''),
('Keep the isolation claim specific','''NetworkPolicy governs supported network behavior under the implementation\'s semantics. It is not application authentication,Secret authorization or a virtual-machine boundary. Host/node traffic and implementation-specific behavior need separate understanding.

A passed two-client test proves the observed allowed/denied paths,not every possible protocol or source. Report the exact labels,port,direction and target identities. Leave the live row unavailable when the CNI has not been qualified.''')],
[
('Combine deny and allow','```yaml\n'+yaml.safe_dump_all([np_deny,np_allow],sort_keys=False)+'```','Selected hello Pods allow same-namespace lesson-client TCP8080 traffic under the combined ingress rules.'),
('Interpret a traffic matrix','''Synthetic before:allowed client success,other client success. After:allowed client success,other client bounded failure. Both target the same healthy Service and exact version route.''','The paired change supports the intended observed enforcement path;API object existence alone would not.')],
[
('Identify destination scope','Read the selected Pod label and policy direction.','app=hello destinations,Ingress only.','Do not confuse destination podSelector with from peers.','The policy applies to selected destination Pods in its namespace. It does not automatically isolate all namespace egress or unrelated applications.'),
('Explain additive rules','Combine the deny-ingress and allow-client policies.','The explicit matching allow remains effective;there is no ordered deny override.','Take the union of applicable allows.','NetworkPolicy is not a first-match firewall rule list. The empty ingress policy establishes isolation,but another matching policy can add allowed traffic. The source structure should be reviewed as a set.'),
('Check peer selector logic','Compare one peer containing namespace+Pod selectors with two separate peers.','One peer means conjunction;separate entries mean alternatives.','Read YAML nesting as logical structure.','A formatting change can broaden the eligible sources. This is a concrete reason to inspect rendered manifests and test a denied control client rather than trust a policy name.'),
('Establish pre-policy controls','Observe both approved clients against a healthy backend before enforcement.','Both paths succeed with the expected payload and target receipt.','A later failure is interpretable only if the path worked initially.','The baseline distinguishes policy effects from an already broken service or wrong port. Use bounded requests and retain actual identities rather than copying the synthetic matrix.'),
('Verify the allowed/denied change','Repeat both paths after the reviewed policies in a qualified CNI lease.','Permitted path succeeds;other path fails within its deadline.','If both results match,investigate capability or selectors.','The paired control supports the intended traffic boundary. A policy object with no enforcement or an application outage affecting both clients does not satisfy the contract.'),
('State limits and cleanup','Record exact policy/client UIDs and the scope of the isolation claim.','Only owned policy resources are cleaned;protocols,hosts and capabilities outside the test remain unclaimed.','Network policy does not replace RBAC or application authentication.','The handoff should identify the CNI and tested traffic tuple. Cleanup must preserve unrelated policies and namespace settings,and a finite result should not be generalized into complete multitenant isolation.')],
[np_deny,np_allow],
'''
def allowed(labels,port):return labels.get('role')=='lesson-client' and port==8080

def main():
    assert allowed({'role':'lesson-client'},8080)
    assert not allowed({'role':'other'},8080) and not allowed({'role':'lesson-client'},9999)
    before={'allowed':True,'other':True};after={'allowed':True,'other':False}
    assert before['other'] and not after['other'] and after['allowed']
    print('k8s-021 synthetic policy logic passed; CNI enforcement requires live evidence')

if __name__ == "__main__":
    main()
''',capability='exclusive policy-capable CNI lease with paired clients',refs=['[Kubernetes NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/)'])

headless={'apiVersion':'v1','kind':'Service','metadata':{'name':'store-headless'},'spec':{'clusterIP':'None','selector':{'app':'store'},'ports':[{'name':'http','port':8080,'targetPort':'http'}]}}
store_template=copy.deepcopy(hello()[0]['spec']['template']);store_template['metadata']['labels']={'app':'store'}
store_template['spec']['securityContext']['fsGroup']=65532
store_template['spec']['containers'][0]['volumeMounts']=[{'name':'data','mountPath':'/data'}]
claim={'metadata':{'name':'data'},'spec':{'accessModes':['ReadWriteOnce'],'storageClassName':'lesson-local','resources':{'requests':{'storage':'16Mi'}}}}
stateful={'apiVersion':'apps/v1','kind':'StatefulSet','metadata':{'name':'store'},'spec':{'serviceName':'store-headless','replicas':1,'selector':{'matchLabels':{'app':'store'}},'persistentVolumeClaimRetentionPolicy':{'whenDeleted':'Retain','whenScaled':'Retain'},'template':store_template,'volumeClaimTemplates':[claim]}}
author(22,
'''Persistent storage separates data lifetime from a particular Pod. A PersistentVolumeClaim requests storage through an access mode,capacity and StorageClass. A PersistentVolume represents provisioned storage and its lifecycle policy. A StatefulSet adds stable Pod identity and per-replica claim naming,but it does not turn a filesystem into a backup or a complete database recovery system.

The host fixture uses a prequalified StorageClass named lesson-local and a single-replica StatefulSet store. Its claim template data produces a claim associated with store-0. The example explicitly retains claims when the StatefulSet is deleted or scaled down. The normal browser adapter does not create PVCs,StatefulSets or storage classes.

A live persistence test writes a synthetic marker once,records its checksum,replaces the application Pod by exact UID and reads the marker through a separate bounded reader. Re-running an initializer that overwrites the same marker would hide data loss,so initialization and verification must be separate operations.''',
[
('Trace claims,volumes and stable identity','''The claim requests16Mi and ReadWriteOnce from lesson-local. That class must exist and be qualified before the lab;the learner does not install a provisioner or mount a personal host directory. A Pending claim can indicate missing class,capacity or binding topology rather than an application bug.

The StatefulSet uses serviceName store-headless and a headless Service for its stable network identity. Its template mounts the claim at /data. The claim template name and StatefulSet/ordinal contribute to the generated claim identity. A replacement Pod can retain the ordinal name while receiving a new Pod UID and reattaching the same claim.

ReadWriteOnce is a volume access-mode contract commonly associated with one node,not a universal promise that only one Pod can mount it. ReadWriteOncePod has different support requirements. Confirm the storage driver and topology rather than infer concurrency guarantees from the word once.'''),
('Prove persistence and retention separately','''Record the initial PVC/PV binding,Pod UID,marker bytes or synthetic checksum,and writer completion. After an owned Pod replacement,verify the new Pod UID,the intended same claim/PV relationship and unchanged marker hash. This establishes the observed Pod-replacement persistence path.

Deleting the PVC or StatefulSet introduces different lifecycle rules. The StatefulSet retention policy controls its claims under supported actions;the PV reclaim policy controls what happens to underlying storage after release. Retain can leave data requiring deliberate cleanup,while Delete can remove it through the provisioner. Neither is an independent backup.

The course cluster itself is disposable. A local volume retained inside a node may still disappear when that owned cluster/node is released. A data-retention claim must name the failure and lifecycle boundary it covers.'''),
('Avoid false persistence proofs','''A healthy Pod or recreated constant file does not prove old data survived. Use a marker whose initialization is not silently repeated,and keep writer/read operations separate. A Bound PVC alone does not prove the application can read the intended bytes.

Do not delete a claim as a routine repair for a Pending Pod. Inspect binding,events,access mode and ownership first. Live storage operations remain unavailable until the host capability and retention choice are explicit.''')],
[
('Read a claim template','```yaml\n'+yaml.safe_dump(claim,sort_keys=False)+'```','The requested class is lesson-local,capacity16Mi and access mode ReadWriteOnce;actual binding is a separate observation.'),
('Compare replacement evidence','''Synthetic before:Pod UID pod-a,PVC uid pvc-a,PV uid pv-a,marker hash h1. After:Pod UID pod-b,same pvc-a/pv-a,marker hash h1.''','The observed data survives Pod replacement;this does not establish survival after PVC or cluster deletion.')],
[
('Trace storage references','Connect StatefulSet volumeClaimTemplates,data mount and StorageClass.','The data claim is mounted at /data and depends on a qualified lesson-local class.','Separate requested claim from bound volume.','The manifest describes desired storage. Binding status and application access need runtime evidence. A missing class is a capability problem,not a reason to substitute an arbitrary hostPath.'),
('Record initial data once','Use a bounded exclusive-create writer for a synthetic marker and retain its hash.','One initialization receipt,claim/PV identities and a known marker checksum.','Do not overwrite existing data during a verification step.','An initializer that recreates the expected bytes after loss can fake persistence. The writer should refuse an existing marker or otherwise make initialization history explicit,while later readers remain read-only.'),
('Replace only the Pod','Use the host operation with the recorded Pod UID and observe its successor.','New Pod UID with the intended stable ordinal and same claim binding.','Pod identity and claim identity have different lifetimes.','The StatefulSet can replace a Pod while reusing its claim. The before/after graph should show which identity changed and which remained,not merely a familiar Pod name.'),
('Verify the marker independently','Read the marker after replacement without running the writer.','Hash remains h1 in the synthetic trace;actual live bytes/hash are recorded separately.','A Ready condition is not a data checksum.','The independent read closes the application-data boundary. It catches empty or wrong storage even if the container starts successfully. This is the core persistence evidence for the tested failure.'),
('Explain retention and reclaim','Compare StatefulSet claim retention with PV reclaim policy and cluster release.','Each lifecycle boundary has its own policy;retention is not backup.','Ask which object is deleted and who owns the underlying bytes.','Retaining a PVC after StatefulSet deletion does not guarantee data survives node or cluster destruction. The handoff should state the chosen synthetic-data retention and eventual cleanup policy explicitly.'),
('Diagnose a Pending claim','Use supplied binding/events to propose a minimal class/capacity/topology check.','No destructive claim reset;the missing capability or binding condition is identified.','Inspect StorageClass and binding evidence before changing the application.','Storage setup is a separate host responsibility. A bounded lesson should report an unavailable class or incompatible mode instead of deleting data or installing a provisioner automatically.')],
[headless,stateful],
'''
import hashlib

def main():
    marker=b'persistent-demo';digest=hashlib.sha256(marker).hexdigest()
    before={'pod':'pod-a','pvc':'pvc-a','pv':'pv-a','hash':digest}
    after={**before,'pod':'pod-b'}
    assert before['pod']!=after['pod'] and before['pvc']==after['pvc'] and before['hash']==after['hash']
    assert {'whenDeleted':'Retain','whenScaled':'Retain'}['whenDeleted']=='Retain'
    assert hashlib.sha256(b'wrong').hexdigest()!=digest
    print('k8s-022 synthetic persistence evidence passed; no storage provisioned or restored')

if __name__ == "__main__":
    main()
''',capability='qualified owned StorageClass/PVC/StatefulSet and finite marker writer/reader',refs=['[Kubernetes persistent volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)','[Kubernetes StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)'])

route={'apiVersion':'gateway.networking.k8s.io/v1','kind':'HTTPRoute','metadata':{'name':'hello-route'},'spec':{'parentRefs':[{'name':'lesson-gateway'}],'hostnames':['lesson.local'],'rules':[{'matches':[{'path':{'type':'PathPrefix','value':'/version'}}],'backendRefs':[{'name':'hello','port':8080}]}]}}
ingress={'apiVersion':'networking.k8s.io/v1','kind':'Ingress','metadata':{'name':'hello-ingress'},'spec':{'ingressClassName':'lesson-ingress','rules':[{'host':'lesson.local','http':{'paths':[{'path':'/version','pathType':'Prefix','backend':{'service':{'name':'hello','port':{'number':8080}}}}]}}]}}
(BASE/'fixtures/k8s-023-ingress.json').write_text(json.dumps(ingress,indent=2)+'\n')
author(23,
'''A Service provides an internal backend abstraction;an ingress or gateway controller can expose selected routes through a managed listener. Gateway API separates infrastructure ownership,listener configuration and application route attachment. Creating an HTTPRoute object does not install a controller or create a working external address.

This host lab requires a preinstalled qualified Gateway controller,a host-owned Gateway named lesson-gateway,an owned Service backend and a loopback-only listener. A synthetic TLS case also needs a verified local trust chain and hostname. The normal browser adapter provides none of those cluster/controller operations and does not accept Gateway or Ingress resources.

The real HTTPRoute example matches host lesson.local and path prefix /version,then forwards to hello:8080. It leaves other paths unmatched. The Ingress comparison is a separate fixture with its own ingressClassName;do not assume the two APIs are interpreted by the same controller or apply both to an unreviewed listener.''',
[
('Follow Gateway ownership and route status','''GatewayClass identifies a controller/infrastructure class and is cluster-scoped. A Gateway selects that class and defines listeners. HTTPRoute attaches through parentRefs and describes request matches and backends. The parent\'s allowedRoutes policy can restrict which namespaces may attach.

Inspect the route\'s parent-specific Accepted and ResolvedRefs conditions and their observed generation. A syntactically valid backend reference can still be unresolved or unauthorized. Cross-namespace references may require an explicit ReferenceGrant rather than being permitted by a matching name. The host must provide that capability deliberately;the learner should not widen it during diagnosis.

A positive status is necessary controller evidence,but a bounded client request must still prove routing and payload. A controller can accept a configuration before the data plane is ready,or a backend can be unready.'''),
('Test path,host and TLS independently','''For the positive case,connect through the loopback listener using the intended host and /version path. Verify the synthetic certificate against the provided CA and hostname when TLS is enabled. A successful TCP connection or HTTP response obtained by disabling certificate checks does not establish the TLS contract.

An unmatched path should produce the controller\'s expected no-route behavior,while a matching route should return the fixture\'s exact version body. A wrong hostname can select another listener/route or fail TLS verification. Record which layer failed rather than calling every negative result an application error.

The ordinary fixture client is HTTP-only and targets hello internally. It cannot prove the external TLS path. A separately qualified host client is required,with its CA file and loopback address from the owned receipt. No public load balancer or external IP is assumed.'''),
('Avoid controller and exposure assumptions','''A Kubernetes API object is not a running controller. An Ingress class or GatewayClass name must correspond to an installed,qualified implementation. A Service of type ClusterIP does not expose a host port by itself.

Keep listener ownership and cleanup separate from the namespaced route. The learner should remove only its recorded route UID unless the host capability explicitly owns the Gateway/controller lifecycle. Never disable TLS verification or install a remote controller automatically to make the example pass.''')],
[
('Read the HTTPRoute','```yaml\n'+yaml.safe_dump(route,sort_keys=False)+'```','The route attaches to lesson-gateway for lesson.local and forwards /version to hello:8080.'),
('Compare accepted and delivered','''Synthetic status:Accepted=True,ResolvedRefs=True for the current generation. A matching client still receives503 because the backend has no ready endpoints.''','Route acceptance and reference resolution do not establish backend application readiness.')],
[
('Draw the ownership layers','Connect GatewayClass,Gateway,HTTPRoute,Service and Pods.','Controller/listener ownership is separated from the application route and backend.','Identify cluster-scoped versus namespaced objects.','The layered design lets different roles own infrastructure and application routing. It also means a learner route manifest cannot create the missing controller or authorize itself to attach anywhere.'),
('Read matches and references','Inspect host,path prefix,parent and backend port.','lesson.local,/version,lesson-gateway,hello8080 are the declared contract.','A reference name is interpreted within its API/namespace rules.','The route must be accepted by the intended parent and resolve its backend. Cross-namespace attachment/reference permissions are separate conditions,not implied by a familiar service name.'),
('Inspect current conditions','Compare Accepted/ResolvedRefs with observed generation.','Current parent-specific conditions support configuration acceptance,not final delivery alone.','Check which parent/controller produced the status.','Stale or unrelated parent status can mislead a rollout review. The live packet should connect conditions to the requested generation and intended Gateway,then continue to a client check.'),
('Verify matching and unmatched requests','Use the qualified loopback client for /version and an unmatched path.','Expected version response on the match;documented no-route result on the negative path.','Keep host header/hostname and path explicit.','The pair tests the actual route selection rather than only a generic HTTP response. Record backend readiness and route identity so a default route cannot accidentally satisfy the positive case.'),
('Verify synthetic TLS correctly','Use the host-provided CA/hostname and test a mismatched identity.','Valid chain/hostname succeeds;wrong identity fails without an insecure bypass.','Transport encryption and certificate identity are both part of the claim.','A request made with verification disabled would not prove the trust contract. The certificate is synthetic and host-owned;the normal worker receives no Secret or external-listener privilege.'),
('Compare Ingress and cleanup scope','Review the separate Ingress fixture and name what is independently required.','Qualified ingressClass/controller plus exact route cleanup;no assumption of API interchangeability.','An API kind does not identify every implementation behavior.','The comparison should describe ownership and supported features rather than declaring one manifest a universal replacement. Preserve the host Gateway/controller unless its separate receipt authorizes lifecycle cleanup.')],
[route],
'''
def main():
    route={'host':'lesson.local','prefix':'/version','backend':'hello','port':8080}
    assert '/version'.startswith(route['prefix']) and not '/other'.startswith(route['prefix'])
    status={'accepted':True,'resolved':True,'backend_ready':False}
    assert status['accepted'] and status['resolved'] and not status['backend_ready']
    assert route['host']!='wrong.local'
    print('k8s-023 synthetic routing/TLS identity reasoning passed; no listener created')

if __name__ == "__main__":
    main()
''',capability='host-provisioned Gateway/Ingress controller and loopback TLS listener',refs=['[Gateway API HTTP routing](https://gateway-api.sigs.k8s.io/guides/user-guides/http-routing/)','[Kubernetes Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)'])

kroot=BASE/'fixtures/kustomize';(kroot/'base').mkdir(parents=True,exist_ok=True)
base=hello()[0];base['spec']['replicas']=1
(kroot/'base/deployment.yaml').write_text(yaml.safe_dump(base,sort_keys=False))
(kroot/'base/kustomization.yaml').write_text('apiVersion: kustomize.config.k8s.io/v1beta1\nkind: Kustomization\nresources:\n  - deployment.yaml\n')
for name,count in [('dev',1),('test',2)]:
 folder=kroot/'overlays'/name;folder.mkdir(parents=True,exist_ok=True)
 (folder/'kustomization.yaml').write_text('apiVersion: kustomize.config.k8s.io/v1beta1\nkind: Kustomization\nresources:\n  - ../../base\nreplicas:\n  - name: hello\n    count: '+str(count)+'\n')
 expected=copy.deepcopy(base);expected['spec']['replicas']=count
 (kroot/f'expected-{name}.json').write_text(json.dumps(expected,indent=2)+'\n')
author(24,
'''Kustomize transforms a base set of Kubernetes manifests through explicit overlays. It works with structured YAML rather than a general text-template language. Rendering produces desired objects for review;it does not by itself contact or modify a cluster. Server-side apply is a separate API operation that tracks field ownership among managers.

The vendored fixture contains one Deployment base and dev/test overlays that change only replica count. It uses local relative paths and no remote base. A prepared pinned renderer can produce output offline. The checked-in expected JSON records the intended result,but is not a claim that a renderer was executed on this host.

The browser does not run Kustomize or arbitrary apply commands. A reviewed rendered Deployment can fit the fixed manifest contract,while live field-manager conflict experiments need a stateful host capability with explicit ownership and target identity.''',
[
('Read a base and an overlay','''The base kustomization lists deployment.yaml. Each overlay references ../../base and declares a replicas transformation for the object named hello. Dev requests1 and test requests2. No namespace transformer,image replacement or extra resource is hidden in this example.

With an already prepared tool,render the local overlays using its kustomize build or kubectl kustomize command and save output in an owned scratch directory. Rendering is an offline activity;do not add a remote URL or invoke plugins to make a missing dependency appear. Compare the complete rendered object set before any apply.

The independent expected objects differ only at spec.replicas. A diff should reveal that exact path. Unexpected namespace,security,image or resource-kind changes are review findings,even if the renderer exits successfully.'''),
('Understand managed fields and conflicts','''Server-side apply records which field manager owns relevant fields. Two actors can manage different parts of an object,but conflicting intent on the same field can produce a conflict. A field-manager name is an ownership identity for the apply operation,not a user authentication credential.

A synthetic example has teacher-controller owning spec.replicas while lesson-review tries to set a different value. The conflict should be explained and coordinated. Force-conflicts can take ownership and overwrite another manager\'s intent;it is not a default troubleshooting step.

Inspect current object UID,resourceVersion,managedFields and desired source before a live change. The ordinary worker uses create/read/delete,so it does not claim server-side-apply behavior from a one-shot Run.'''),
('Keep rendering,validation and apply distinct','''A rendered file can be valid YAML and still contain an unsupported API,an unapproved image or a namespace escape. A server dry-run can provide admission evidence but is not a completed reconciliation. An apply response is still weaker than application verification.

Do not edit generated output as a hidden second source of truth without recording the change in the overlay. Retain the base/overlay identity,rendered diff and actual runtime receipt when a host apply is performed.''')],
[
('Compare the two overlays','''Local fixture paths are fixtures/kustomize/overlays/dev and overlays/test. Their declared counts are1 and2. The expected JSON files preserve all other Deployment fields.''','Only spec.replicas differs in the intended rendered objects.'),
('Read a field-owner conflict','''Synthetic current manager teacher-controller owns spec.replicas=2. Manager lesson-review requests1 and receives a conflict on that field.''','Coordinate ownership or revise intent;do not automatically force-overwrite the other manager.')],
[
('Locate the source of intent','Identify base resource and overlay replica transform.','One local Deployment base plus explicit dev1/test2 overrides.','Read resources and replicas entries before rendering.','The overlay expresses the intended environment difference. Local paths and a small resource set make review tractable and avoid a hidden network dependency.'),
('Render with prepared tooling','Run the pinned local renderer if available and retain its version/output.','Actual output is compared with expected JSON;missing tool is recorded as unavailable.','Rendering is not an API mutation.','The checked-in expected output is an independent target,not a fabricated execution transcript. A real render receipt should include tool identity and source hashes,especially when versions can change transformations.'),
('Compare the full diff','Verify that dev and test outputs differ only at spec.replicas.','Exactly one intended field path changes.','Inspect namespace,image,security and resource kinds as well as replicas.','A successful renderer can still produce an unsafe or unintended object. The diff must cover the full output set so an extra resource or changed target is not hidden behind the expected count change.'),
('Interpret field ownership','Explain the teacher-controller/lesson-review conflict.','The same field has competing intent;manager identity and current UID/version are recorded.','Managed fields are not the same as RBAC identity.','Authorization can permit a request while field ownership still conflicts. The correct response is to coordinate which actor should manage the field or change the design,not assume force is harmless.'),
('Reject a namespace escape','Review an overlay adding an unrelated namespace or unapproved image.','The output fails the course ownership/allowlist review before apply.','A local render is data,not authorization.','The target must remain bound to the owned receipt. Neither a valid YAML parser nor a successful Kustomize command grants permission to apply elsewhere.'),
('Preserve reproducibility','Record source overlay,renderer version,rendered hash,diff and any actual apply/readback.','A reviewer can separate render,admission,reconciliation and application evidence.','Do not silently edit the rendered file alone.','Keeping the transformation inputs and output connected prevents drift between declared and applied intent. Live acceptance remains a separate bounded host operation with UID-aware cleanup.')],
[base],
'''
import copy

def differences(a,b,path=''):
    if isinstance(a,dict) and isinstance(b,dict):
        result=[]
        for key in sorted(set(a)|set(b)):result+=differences(a.get(key),b.get(key),path+'.'+key)
        return result
    return [] if a==b else [path.lstrip('.')]

def main():
    dev={'metadata':{'name':'hello'},'spec':{'replicas':1,'image':'fixed'}}
    test=copy.deepcopy(dev);test['spec']['replicas']=2
    assert differences(dev,test)==['spec.replicas']
    owners={'spec.replicas':'teacher-controller'}
    assert owners['spec.replicas']!='lesson-review'
    print('k8s-024 synthetic overlay/ownership checks passed; no renderer or apply inferred')

if __name__ == "__main__":
    main()
''',capability='prepared offline Kustomize plus separate stateful field-manager host lab',refs=['[Kubernetes Kustomize guide](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/)','[Server-side apply](https://kubernetes.io/docs/reference/using-api/server-side-apply/)'])

chart=BASE/'fixtures/helm/lesson-hello';(chart/'templates').mkdir(parents=True,exist_ok=True)
(chart/'Chart.yaml').write_text('apiVersion: v2\nname: lesson-hello\nversion: 0.1.0\nappVersion: "fixture-0.2.0"\ntype: application\n')
(chart/'values.yaml').write_text('replicas: 1\nimage: ds60sqlpy-k8s-fixture:0.2.0\n')
(chart/'values.schema.json').write_text(json.dumps({'$schema':'http://json-schema.org/draft-07/schema#','type':'object','additionalProperties':False,'required':['replicas','image'],'properties':{'replicas':{'type':'integer','enum':[1,2]},'image':{'const':'ds60sqlpy-k8s-fixture:0.2.0'}}},indent=2)+'\n')
rendered=hello()[0];rendered['spec']['replicas']=1
template=yaml.safe_dump(rendered,sort_keys=False).replace('replicas: 1','replicas: {{ .Values.replicas }}').replace('image: ds60sqlpy-k8s-fixture:0.2.0','image: {{ .Values.image | quote }}')
(chart/'templates/deployment.yaml').write_text(template)
(chart/'expected-default.json').write_text(json.dumps(rendered,indent=2)+'\n')
author(25,
'''Helm renders parameterized chart templates and can manage release lifecycle through the Kubernetes API. Rendering a chart locally and installing a release are different operations. An install may create release metadata,execute lifecycle hooks or include cluster-scoped resources,so a successful template command is not permission to run the full lifecycle.

The vendored lesson-hello chart has no remote dependencies,plugins,hooks or CRDs. Its values schema restricts replicas to one or two and the image to the approved fixture0.2.0. The only template is a fixed Deployment. A prepared pinned Helm binary can render this local input offline;the browser does not execute Helm commands.

The lesson emphasizes reviewing the rendered objects rather than trusting a chart name or a friendly values file. A template can hide resource kinds,annotations and field changes that are not obvious from one setting. The default expected JSON is a declared output target,not a fabricated Helm execution receipt.''',
[
('Read chart metadata,values and templates','''Chart.yaml describes chart identity and version;appVersion is descriptive application metadata and does not pin image bytes by itself. values.yaml supplies defaults,and values.schema.json constrains the accepted input shape. The template inserts .Values.replicas and a quoted image string into an otherwise fixed Deployment.

With a qualified local Helm binary,use helm template hello courses/kubernetes/fixtures/helm/lesson-hello and retain the rendered output in an owned scratch directory. No dependency update or download is required. Record the actual Helm version because rendering and validation behavior can vary across major versions.

The default output requests one replica. An allowed replicas=2 override should change that field only. An unapproved image or extra values key should fail the schema or subsequent manifest review rather than silently broaden the workload.'''),
('Review hooks,CRDs and release side effects','''A hook is commonly marked by helm.sh/hook annotations and can run at release lifecycle points. A chart can also contain CRDs or other cluster-scoped objects. Local rendering does not execute those hooks,but hiding them from review can make a later install surprising. Inspect all rendered documents and the chart\'s vendored contents.

Helm release storage and lifecycle permissions are broader than applying one reviewed Deployment. The normal worker deliberately lacks those capabilities. A rendered object that matches the fixed source allowlist can be reviewed as ordinary YAML,but that does not mean the worker supports helm install or upgrade.

A negative fixture containing a hook Job or ClusterRole should fail the course review before any lifecycle operation. Do not run plugins or fetch a chart from an unrecorded remote source to satisfy a missing dependency.'''),
('Keep reproducibility and authority separate','''Pin chart contents,dependency inputs,values,renderer version and rendered output identity. A chart version string alone can be reused or refer to changed bytes. Diff the complete output before applying,including security and namespace fields.

If Helm is unavailable,the live render row remains unavailable while the source/expected-output reasoning can be completed offline. A valid render is not API acceptance,reconciliation or application correctness. Those remain separate owned operations with their own cleanup receipts.''')],
[
('Trace one values substitution','''Default values replicas1 and approved image0.2.0 produce the expected fixed Deployment. An override to replicas2 changes only spec.replicas in this chart.''','The rendered resource set remains one Deployment with no namespace escape or new lifecycle object.'),
('Detect a hidden hook','''A rendered Job contains metadata.annotations.helm.sh/hook=post-install. Even if its name sounds harmless,it represents a lifecycle action absent from the ordinary Deployment contract.''','Reject it from this course operation before install;rendering itself does not execute the hook.')],
[
('Inventory the vendored chart','List metadata,values,schema,template and expected output.','One local template,no dependencies/plugins/hooks/CRDs.','Inspect the complete directory,not only values.yaml.','The inventory establishes which inputs the renderer can use. It should reveal hidden resource-producing files before a deployment action is considered.'),
('Render the default locally','Use already prepared pinned Helm and compare output with expected-default.json.','One Deployment with replicas1 and approved image;record actual renderer receipt or unavailable status.','No network dependency step is part of this fixture.','The expected file is an independent reference. A real render should be observed and versioned rather than inferred from readable template syntax.'),
('Review an allowed override','Render replicas2 and diff the full object.','Only spec.replicas changes.','Schema validation and full diff serve different checks.','The schema limits input values,but the rendered output still needs review because a template could use one value in several fields. The simple fixture makes that relationship explicit.'),
('Reject invalid values','Try replicas3,an unapproved image or an extra unknown key in a scratch values file.','Schema/review rejection before any cluster operation.','Read enum,const and additionalProperties restrictions.','The failure is a rendering/input-contract result,not a Kubernetes scheduling failure. Preserve the diagnostic and restore valid values rather than disabling validation.'),
('Detect lifecycle resources','Review a supplied hook annotation or cluster-scoped kind.','The output is outside the normal worker contract and is not installed.','A chart can produce more than its headline Deployment.','Hooks,CRDs and release storage change authority and cleanup needs. The lesson keeps them visible rather than relying on a chart\'s name or suppressing output that would reveal them.'),
('Hand off a reviewed render','Record chart/values hashes,renderer version,full diff and separate apply/application acceptance.','A reviewer can reproduce the local render and identify the exact owned runtime boundary.','Do not equate helm template with helm install.','The handoff connects inputs to desired objects without pretending rendering grants deployment authority. Any host install requires its own scoped capability and lifecycle/cleanup evidence.')],
[rendered],
'''
def review(objects):
    for obj in objects:
        if obj['kind'] not in {'Deployment','Service','ConfigMap'}:return False
        if 'helm.sh/hook' in obj.get('metadata',{}).get('annotations',{}):return False
    return True

def main():
    assert review([{'kind':'Deployment','metadata':{'name':'hello'}}])
    assert not review([{'kind':'Job','metadata':{'annotations':{'helm.sh/hook':'post-install'}}}])
    assert not review([{'kind':'ClusterRole','metadata':{'name':'wide'}}])
    assert 1 in {1,2} and 3 not in {1,2}
    print('k8s-025 synthetic rendered-object review passed; Helm execution is separate')

if __name__ == "__main__":
    main()
''',capability='qualified offline Helm rendering; no release installation in normal worker',refs=['[Helm template command](https://helm.sh/docs/helm/helm_template/)','[Helm chart hooks](https://helm.sh/docs/topics/charts_hooks/)'])

daemon_template=copy.deepcopy(hello()[0]['spec']['template']);daemon_template['metadata']['labels']={'app':'node-fixture'};daemon_template['spec']['nodeSelector']={'lesson.ds60sqlpy/zone':'a'}
daemon={'apiVersion':'apps/v1','kind':'DaemonSet','metadata':{'name':'node-fixture'},'spec':{'selector':{'matchLabels':{'app':'node-fixture'}},'template':daemon_template}}
author(26,
'''A Deployment asks for a replica count; a DaemonSet asks for a Pod on each eligible node under its controller and placement rules. Eligibility depends on selectors,affinity,taints/tolerations and other constraints. A desired DaemonSet count therefore cannot be predicted from cluster node count alone.

The host fixture uses a restricted nonroot server with no host network,privileged mode or host mounts. It selects nodes labeled lesson.ds60sqlpy/zone=a. The normal worker does not create DaemonSets,read arbitrary Node details or patch node labels/taints. The host supplies sanitized node facts and an exclusive qualified placement scope.

The offline calculation models only the explicitly listed label and custom-taint conditions. It is not a full scheduler simulator. Resource capacity,automatic controller tolerations and runtime behavior still require actual cluster evidence.''',
[
('Read selectors,affinity and tolerations','''nodeSelector requires matching label key/value pairs. Required node affinity expresses a richer eligibility condition,while preferred affinity influences scoring without guaranteeing a placement. Scheduling rules named IgnoredDuringExecution do not generally imply that an ordinary running Pod is evicted immediately when a node label later changes.

A NoSchedule taint repels new Pods unless a matching toleration permits them. A toleration allows placement;it does not force the Pod onto that node. DaemonSet controllers add some standard tolerations for their operational role,but an arbitrary custom dedicated-node taint is not automatically an invitation to run there.

Do not patch Nodes to make the example pass. That changes a shared cluster-level scheduling input. A dedicated host capability must own such changes and provide a restoration plan if the lesson explicitly requires them.'''),
('Compare expected and observed DaemonSet counts','''Synthetic nodes:node-a has zone=a with no custom taint;node-b has zone=b;node-c has zone=a and a dedicated NoSchedule taint not tolerated by the fixture. Under this limited predicate,only node-a is eligible. Adding the matching toleration in a separately reviewed host variant makes node-c eligible as well.

Compare the host-provided eligible-node facts with desiredNumberScheduled,numberReady and actual Pod nodeName/UID observations. A count can lag during reconciliation,and a ready count smaller than desired needs conditions/events for diagnosis. Zero desired can be correct if no nodes satisfy the selector.

A one-node kind cluster does not establish multinode placement or DaemonSet behavior across failures. Keep the actual topology in the qualification receipt and avoid a generic claim of one Pod per every possible node.'''),
('Diagnose placement without overreaching','''Pending can result from selector mismatch,untolerated taint or insufficient requested resources. A toleration does not grant host access,and a DaemonSet is not inherently privileged. The restricted fixture demonstrates the controller shape without exposing node files or network namespaces.

The static predicate explains supplied facts only. Actual desired/ready counts and node placement must be read from the exclusive host lab. Cleanup targets the recorded DaemonSet UID and its controlled Pods,not node labels or unrelated node-local agents.''')],
[
('Read the node selection','```yaml\n'+yaml.safe_dump(daemon['spec']['template']['spec']['nodeSelector'],sort_keys=False)+'```','Only nodes matching the declared zone are candidates before other placement constraints.'),
('Count the explicit synthetic candidates','''node-a:zone a,no custom taint;node-b:zone b;node-c:zone a,dedicated NoSchedule without toleration.''','One eligible node under the limited fixture predicate;adding a matching toleration can make two.')],
[
('Compare controller intent','Explain replicas2 Deployment versus a DaemonSet over eligible nodes.','Fixed replica count versus topology-derived desired placement.','The controllers answer different questions.','A Deployment can place several replicas on one node unless other constraints prevent it. A DaemonSet reconciles toward node eligibility. Neither object name alone proves a particular topology.'),
('Evaluate node labels','Apply the zone=a selector to the three supplied node facts.','node-a and node-c pass the label condition;node-b does not.','Separate label eligibility from taint/resource checks.','The first filter narrows candidates but does not finish scheduling. Keeping the stages separate helps explain why a matching node may still not receive the Pod.'),
('Evaluate the custom taint','Add the untolerated dedicated NoSchedule condition.','Only node-a remains eligible in the simplified model.','A toleration permits but does not force placement.','The custom taint blocks a new Pod lacking the matching toleration. The model intentionally omits other scheduler behavior and should not be presented as a complete placement predictor.'),
('Observe actual placement','In the qualified host topology,compare desired/ready counts and Pod nodeName/UIDs.','Observed eligible-node and controller evidence agree or a specific condition explains the gap.','Record the actual node count and labels from the host receipt.','Static facts and desired status are not enough to prove a running Pod on each intended node. The live graph should identify controlled Pods and their observed placement without exposing unrelated Node data.'),
('Reject automatic node edits','Review a proposal to remove a taint from a shared Node to make the lab pass.','No learner Node mutation;request the correct owned capability or report unavailable placement.','Node labels and taints are cluster-level inputs.','Changing a shared node can affect unrelated workloads. The ordinary worker has no such permission. A dedicated host rehearsal needs explicit ownership and restoration evidence.'),
('Clean up the right resources','Describe DaemonSet UID-aware cleanup and retained host configuration.','Only the owned DaemonSet/controller children are removed;unrelated agents and node settings preserved.','Controller ownership differs from node ownership.','The workload may run on nodes it does not own. Cleanup must follow its resource receipt rather than deleting every node-local Pod or reverting unrelated scheduling policy.')],
[daemon],
'''
def eligible(node,tolerate=False):return node['zone']=='a' and (not node['dedicated'] or tolerate)

def main():
    nodes=[{'name':'a','zone':'a','dedicated':False},{'name':'b','zone':'b','dedicated':False},{'name':'c','zone':'a','dedicated':True}]
    assert [n['name'] for n in nodes if eligible(n)]==['a']
    assert [n['name'] for n in nodes if eligible(n,True)]==['a','c']
    assert sum(eligible(n) for n in nodes)==1
    print('k8s-026 limited synthetic placement predicate passed; no Nodes inspected or edited')

if __name__ == "__main__":
    main()
''',capability='exclusive topology/DaemonSet host fixture with sanitized node facts',refs=['[Kubernetes DaemonSets](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/)','[Taints and tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)'])

samples=[{'request_id':'r1','status':200,'latency_ms':10},{'request_id':'r2','status':200,'latency_ms':20},{'request_id':'r3','status':500,'latency_ms':30},{'request_id':'r4','status':200,'latency_ms':40},{'request_id':'r5','status':200,'latency_ms':100}]
(BASE/'fixtures/k8s-027-requests.json').write_text(json.dumps({'provenance':'synthetic request samples','rows':samples},indent=2)+'\n')
author(27,
'''Observability connects internal state to the questions an operator needs to answer. Metrics summarize numeric behavior,logs record events and traces connect work across components. None is useful without a defined unit,time window and relation to the service contract. A dashboard can be visually healthy while omitting the failing path.

A service-level indicator should describe user-relevant behavior,such as successful eligible requests divided by all eligible requests. A service-level objective adds a target over a defined window. A five-request teaching sample can illustrate the calculation but cannot establish a production reliability objective.

The chapter uses an authored request ledger and optional host-provided namespace metrics. It does not install a monitoring stack or assume metrics-server exists. Missing metrics capability is recorded as unavailable,not converted to zero CPU or zero errors.''',
[
('Define denominators and latency conventions','''The five synthetic requests have statuses200,200,500,200,200 and latencies10,20,30,40,100milliseconds. The error fraction is1/5=.2. If success means the expected application result rather than merely a2xx status,the numerator needs that additional validation.

Quantiles depend on the calculation convention. The example uses empirical nearest rank:sort values and choose position ceil(q*n),with one-based positions. The all-request p50 is30ms and p95 is100ms. Restricting to successful requests changes the sample and its quantiles,so state the filter.

A tiny p95 is unstable and should not be mistaken for a well-estimated tail guarantee. Preserve raw bounded samples or an appropriate histogram/summary design so a reviewer can understand the statistic.'''),
('Connect controller and application evidence','''Replica counts,Ready conditions and restart counts help diagnose infrastructure behavior. Application success,error and latency measure a different boundary. A Ready Pod can return errors,and a resource metric can be absent even while requests succeed. Correlate observations through time and owned resource identity rather than assuming one graph explains another.

Counters need reset-aware interpretation. A value moving from120 to3 may indicate a process restart;naively subtracting gives a meaningless negative request count. The observation window and reset information determine what can be recovered. Gauges describe a current level and have different aggregation behavior.

Avoid high-cardinality or sensitive labels such as arbitrary user text in metrics. The course uses bounded synthetic identifiers in a request ledger,not an unbounded production label vocabulary.'''),
('Make incidents evidence-bounded','''A missing metrics API is a capability issue,not proof of zero usage. A single slow request suggests a question but does not establish the system-wide cause. An alert should name the violated contract and a discriminating next check.

Record units,window,sample size,filters and missingness. A screenshot alone cannot reproduce the calculation or prove application correctness. The offline script checks the synthetic ledger;actual collection requires the qualified host/client capability.''')],
[
('Calculate a request indicator','''Four of five synthetic requests succeed under the status-only definition. The error rate is.2 and success rate.8.''','The denominator is five eligible requests;status-only success is explicitly narrower than full payload correctness.'),
('Read nearest-rank latency','''Sorted latencies are[10,20,30,40,100]ms. ceil(.5*5)=3 and ceil(.95*5)=5.''','p50=30ms,p95=100ms for this five-request sample and convention.')],
[
('Define an SLI','State eligible requests,success rule,time window and units for the ledger.','A reproducible numerator/denominator with five synthetic observations.','Decide whether2xx alone is enough for the task.','The metric definition determines what is measured. A successful status with a wrong payload may still violate the application contract,so the indicator should match the intended user outcome.'),
('Compute error and success fractions','Count the single500 response and four200 responses.','Error.2,success.8 under the declared status rule.','Retain counts as well as percentages.','Counts reveal the small evidence base. The result illustrates arithmetic and cannot establish a production SLO or recurrence from five synthetic requests.'),
('Compute the stated quantiles','Use empirical nearest rank on all five latencies.','p50=30ms,p95=100ms.','Sort and use one-based ceil(q*n).','Another interpolation convention can yield a different value. Report the convention and filtering rather than treating one library default as a universal p95 definition.'),
('Inspect a counter reset','Compare observations120 then3 across a process restart.','Do not report negative117 requests;record reset and available interval evidence.','A counter differs from a gauge.','The reset changes the interpretation of a simple difference. Recovering a rate needs enough timing/reset data or a monitoring method designed for counters. Do not invent events that were not observed.'),
('Handle absent metrics','Record an unavailable namespace metrics API alongside successful client evidence.','Metrics capability unavailable,not zero resource use.','Separate collection failure from the measured quantity.','The absence of a data source is itself an operational fact. Installing a stack or broadening credentials is outside this lesson\'s automatic workflow;the host must provide and qualify it deliberately.'),
('Write a focused incident observation','Combine one controller fact and one application metric with a hypothesis and next check.','A bounded evidence record with units,window,UIDs and a reversible diagnostic.','A correlation is a lead,not a confirmed cause.','The next check should discriminate a plausible mechanism such as backend readiness,application errors or resource pressure. Preserve missingness and uncertainty instead of turning a dashboard pattern into a definitive root cause.')],
hello(True),
'''
import math

def nearest_rank(values,q):return sorted(values)[math.ceil(q*len(values))-1]

def main():
    statuses=[200,200,500,200,200];latency=[10,20,30,40,100]
    assert sum(s>=500 for s in statuses)/len(statuses)==.2
    assert nearest_rank(latency,.5)==30 and nearest_rank(latency,.95)==100
    before,after=120,3;assert after<before
    metrics_available=False;assert metrics_available is False
    print('k8s-027 synthetic SLI/quantile/reset checks passed; no metrics stack installed')

if __name__ == "__main__":
    main()
''',capability='bounded request ledger and optional qualified namespace metrics',refs=['[Kubernetes observability](https://kubernetes.io/docs/concepts/cluster-administration/observability/)'])

capstone=[*fixture('hello-configured.yaml'),headless,stateful,np_deny,np_allow]
author(28,
'''The intermediate capstone combines a stateless application response,a synthetic persistent marker store,reviewed configuration rendering and measured traffic policy. It is a host-lab integration exercise because the normal browser adapter does not provide the storage,CNI and stateful-update capabilities needed for the whole scenario.

The supplied manifests keep the components explicit:configured hello Deployment/Service,one StatefulSet claim template and two ingress policies. The persistent marker is a file-based synthetic datastore,not a real database service. Its writer and reader operations must be separately bounded and reviewed by the host. A correct frontend response is not evidence that the marker survived,and an unchanged marker is not evidence that network isolation works.

The capstone\'s acceptance packet connects those independent observations and includes a failed-change recovery. Cleanup respects the declared synthetic-data retention choice and exact resource identities. Releasing the disposable cluster is a separate lifecycle boundary that can remove node-local retained data.''',
[
('Plan component and capability dependencies','''Before starting,verify the owned namespace UID,qualified StorageClass,policy-capable CNI,approved images and prepared renderer if used. Record which host operation owns cluster-scoped prerequisites and which namespaced resources the learner scenario owns. The current ordinary worker lease does not silently acquire these extra rights.

Initialize the marker once using exclusive creation,record its checksum,and verify the application\'s initial response. Establish both permitted and denied client paths around the NetworkPolicy change. The source/overlay or chart render should be reviewed as a complete object set before a stateful apply.

A missing capability is reported explicitly. Do not replace a PVC with a personal hostPath,disable policy checks or infer renderer success from the expected-output file merely to produce a complete-looking packet.'''),
('Rehearse one failed change and recover','''Choose a bounded failure such as a wrong readiness path in the candidate application revision. Record desired generation,old/new Pod identities,client results and marker checksum before the change. After the failed acceptance gate,restore the reviewed desired configuration and verify the intended application marker and data hash.

The persistent data check must be read-only after initialization. A repair that rewrites the expected marker could conceal data loss. Traffic policy should be retested after recovery because a source change may alter labels used by selectors. A ready application alone does not close every capstone gate.

Keep the failure timeline and cleanup outcome. The host may retain the synthetic PVC for a subsequent recovery lesson only when that retention is explicitly recorded;otherwise final cleanup follows exact object receipts and the chosen reclaim policy.'''),
('Do not collapse independent acceptance gates','''Application response,stored data,authorization,network enforcement and cleanup have different evidence. A single green summary cannot replace the underlying identities,checksums and client results. The fixture is bounded and synthetic,so it does not establish production database durability,HA or a universal isolation guarantee.

The offline reference checks the packet logic only. The full host capstone remains unavailable on the basic one-shot profile even though several of its individual manifests resemble supported browser sources.''')],
[
('Read a complete evidence packet','''Synthetic packet:application marker reviewer,data hash h1,allowed client success,denied client failure,limited authorization confirmed,cleanup/retention recorded. Every field has its own source and timestamp.''','All component gates must pass;one cannot substitute for another.'),
('Reject recovery by reinitialization','''After a failed rollout,the operator reruns the marker writer before checking storage. The marker now matches h1,but the prior bytes were never read.''','Persistence recovery is unproved because the verification step overwrote the evidence.')],
[
('Inventory capabilities','List storage,CNI,renderer,image and owned-target requirements.','Each capability has a qualified host receipt or is marked unavailable.','The ordinary worker does not implement the entire capstone.','A complete plan names the missing execution surfaces rather than pretending all Kubernetes objects are interchangeable through the browser adapter. This preserves both authority and evidence quality.'),
('Establish independent baselines','Record application response,marker hash and both client paths before change.','A source-identified baseline exists for every acceptance gate.','Keep writer completion separate from read verification.','The baseline makes later differences interpretable. It should include exact resource identities and the data initialization boundary,not only a screenshot of ready Pods.'),
('Review rendered intent','Compare the full chart/overlay output with the approved object set.','No unexpected kind,namespace,image,hook or security change.','Rendering is data preparation,not deployment authority.','The review catches changes that a single values diff might hide. A host apply still needs scoped identity and field-ownership handling before controller/application checks.'),
('Inject and diagnose one change failure','Use the approved wrong-probe or equivalent bounded candidate fault.','The intended gate fails with a discriminating condition/client result and no unrelated mutation.','Predict the first failing boundary before applying.','A useful negative case demonstrates that the acceptance packet can reject a plausible bad release. Preserve the failed source and observed facts rather than only the eventual repaired result.'),
('Recover without rewriting data','Restore reviewed intent,then read the marker and retest policy/client behavior.','Application recovers,hash remains h1,and allowed/denied paths retain their intended outcomes.','A reader must not double as an initializer.','Recovery evidence is strongest when the old data is inspected independently. Rewriting a constant marker after failure would make an empty volume look correct and invalidate the persistence claim.'),
('Hand off retention and cleanup','Record whether the synthetic PVC remains and which exact resources were removed.','UID-aware cleanup and explicit data-retention/reclaim boundaries are reviewable.','Cluster release is separate from Pod/claim retention.','The packet should let another learner reproduce the failure and recovery while knowing what remains. Retained local data is not an independent backup,and releasing the owned cluster can end that retention boundary.')],
capstone,
'''
def accepted(packet):return all(packet[k] for k in ('application','data','allowed_path','denied_path','authorization','cleanup_or_retention'))

def main():
    packet=dict.fromkeys(('application','data','allowed_path','denied_path','authorization','cleanup_or_retention'),True)
    assert accepted(packet)
    for key in packet:
        bad={**packet,key:False};assert not accepted(bad)
    before='h1';read_after='h1';assert before==read_after
    print('k8s-028 synthetic multi-gate capstone logic passed; full host acceptance is separate')

if __name__ == "__main__":
    main()
''',capability='exclusive storage/policy/stateful-change integration lease',refs=['[Kubernetes persistent volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)','[Kubernetes NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/)'])
