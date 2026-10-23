from author import author,hello,BASE
import copy,json,yaml

hpa={'apiVersion':'autoscaling/v2','kind':'HorizontalPodAutoscaler','metadata':{'name':'hello'},'spec':{'scaleTargetRef':{'apiVersion':'apps/v1','kind':'Deployment','name':'hello'},'minReplicas':1,'maxReplicas':2,'metrics':[{'type':'Resource','resource':{'name':'cpu','target':{'type':'Utilization','averageUtilization':50}}}],'behavior':{'scaleDown':{'stabilizationWindowSeconds':60,'policies':[{'type':'Pods','value':1,'periodSeconds':60}]}}}}
author(33,
'''Horizontal Pod Autoscaling changes a workload's desired replica count using observed metrics and a declared target. It is a feedback loop: measure, compare, choose a desired count, then wait for workload and metrics observations to reflect the change. The extra Pods are not instantaneous capacity, and CPU load is not the same thing as business demand or response-time quality.

This example uses CPU utilization relative to CPU requests. If a Pod requests100m and uses50m, its utilization for that resource is50percent. Changing the request to200m while leaving usage50m changes the ratio to25percent. A request is therefore part of the autoscaling model as well as a scheduling input. An absent metric is unavailable evidence, not a zero-load observation.

The supplied HPA uses autoscaling/v2, targets Deployment hello, and limits replicas to1 through2. It requires a qualified metrics API path and a host-provided bounded load generator. The basic module fixture has no such qualification. Its fast HTTP handler is useful for service checks, but arbitrary traffic against it must not be presented as a reliable CPU scaling experiment.''',
[
('Derive the simple recommendation','''For a complete, current metric sample, a useful first model is desired=ceil(currentReplicas*observedUtilization/targetUtilization). currentReplicas is a count, observed and target use the same percentage units, and ceil rounds upward to a whole Pod. At one replica, observed80 and target50 yield ceil1.6=2. At two replicas, observed20 and target50 yield ceil0.8=1.

The configured min/max then constrain the recommendation. One replica at200percent would suggest4 before the maximum clips it to2. The clip is an important signal: the policy may have reached its budget while demand remains unmet. A stable replica count at the maximum is not evidence of sufficient capacity.

The real controller includes tolerance, readiness/missing-metric treatment, stabilization and scaling policy rules. The checker below deliberately models only the complete-data proportional calculation and range clamp. It must not be used to predict an exact timestamp or every live HPA decision.'''),
('Read the manifest and feedback delay','''scaleTargetRef names the object whose scale subresource the HPA controls. minReplicas and maxReplicas bound that desired count. The Resource metric uses cpu and target type Utilization, so the percentage is tied to requests. Metrics that represent raw values or custom external demand have different semantics and must not be substituted without redefining the equation.

The scaleDown behavior keeps a60-second stabilization window and limits reduction to one Pod per60seconds. This reduces rapid shrink/grow oscillation in the teaching contract. It does not guarantee a scale-down at exactly second60, because collection, controller reconciliation, readiness and policy timing also matter.

A load step can first raise usage, then trigger a recommendation, then cause scheduling/startup, then distribute load across ready replicas. Record these observations separately. If new Pods are Pending or unready, the desired count can increase without useful serving capacity. Check response failures and latency alongside CPU and replica status.'''),
('Design a bounded measurement','''Use the host-provided fixed load duration, request concurrency and stop limit in an exclusive lease. Record metrics API health, per-Pod requests, sample timestamps and HPA conditions. Define a permissible range and deadline rather than an exact transition second. Stop if the load exceeds the lesson resource budget or the target identity changes.

If metrics are missing, preserve the unavailable condition and fix the qualified measurement path. Do not report zero utilization, remove resource requests to silence a warning or install a metrics component from the learner pad. A single successful scaling step does not establish production sizing, cost efficiency or stability under all workloads.''')],
[
('Compute and clamp a recommendation','```yaml\n'+yaml.safe_dump(hpa,sort_keys=False)+'```\nWith one replica and80percent utilization against50percent, the ideal count is2. With200percent, ideal4 is limited to maximum2.','Both cases request at most2; the second remains potentially capacity-limited.'),
('Explain a delayed scale-down','''Synthetic observations: t0 two ready replicas at20percent; t10 raw recommendation1; t20 an earlier higher recommendation remains inside the stabilization window; later the window expires and reduction is permitted. Another trace has no metric sample at all.''','The first trace can legitimately remain at2 during stabilization. The missing-data trace cannot be interpreted as zero load.')],
[
('Calculate request-relative utilization','Compare usage50m with requests100m and200m.','50percent and25percent respectively.','Divide usage by request, not by the CPU limit.','The same measured CPU use can lead to different utilization ratios when requests change. This explains why tuning requests changes both scheduling commitments and autoscaling behavior, and why units must be recorded.'),
('Apply the ideal formula','Evaluate current1,observed80,target50 and current2,observed20,target50.','Unclipped recommendations2 and1.','Multiply before rounding upward.','The proportional model scales count according to the demand ratio. It is useful for understanding the direction and approximate magnitude, while controller safeguards and incomplete measurements can alter the actual action.'),
('Recognize saturation at the maximum','Compute the ideal count at current1 and utilization200percent.','Ideal4, configured maximum2; capacity adequacy remains unproven.','A policy bound is not a performance result.','The HPA can be operating exactly as configured while failing to meet latency or throughput needs. Report the bound and observed application performance instead of equating a stable count with success.'),
('Diagnose missing metrics','Interpret an unavailable CPU metric and failed HPA metric condition.','Unknown load, with a qualified metrics-path investigation.','Absence is not numeric zero.','The denominator requests and the metrics supply must both be valid. The appropriate response is to inspect the declared host capability and conditions, not to fabricate a low-utilization sample or widen the learner credential.'),
('Observe a bounded live step','Use the fixed host load and compare sample, desired replicas, ready replicas and application results.','Timestamped transitions within declared ranges and deadline, not an exact scaling second.','Separate desired count from ready capacity.','The observation chain exposes delays and failures. A desired count of2 with only one ready Pod is incomplete capacity expansion, and a load generator reaching its own limit can also distort interpretation.'),
('Explain stabilization and stop','Interpret delayed scale-down and end the load at its budget.','Reasoned delay explanation and confirmed load termination; no production sizing claim.','Review the recommendation window and scaling policy.','Stabilization deliberately avoids reacting to every temporary dip. The final packet should preserve metrics freshness, bounded workload settings and application evidence so another reader can understand the scope of the observed behavior.')],
[hello()[0],hpa],
'''
import math

def recommend(current,observed,target,minimum=1,maximum=2):
    if observed is None:raise ValueError('metric unavailable')
    if current<1 or observed<0 or target<=0:raise ValueError('invalid model input')
    ideal=math.ceil(current*observed/target)
    return ideal,min(maximum,max(minimum,ideal))

def main():
    assert 50/100*100==50 and 50/200*100==25
    assert recommend(1,80,50)==(2,2)
    assert recommend(2,20,50)==(1,1)
    assert recommend(1,200,50)==(4,2)
    try:recommend(1,None,50)
    except ValueError:pass
    else:raise AssertionError('missing metric was converted to zero')
    print('k8s-033 complete-data proportional model passed; real HPA timing is not simulated')

if __name__ == "__main__":
    main()
''',capability='qualified metrics API, HPA operations and fixed bounded load fixture',refs=['[Horizontal Pod Autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/)','[Resource metrics pipeline](https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/)'])

stable=copy.deepcopy(hello()[0]);candidate=copy.deepcopy(stable)
for obj,release,message in ((stable,'stable','hello'),(candidate,'candidate','reviewer')):
    obj['metadata']['name']='hello-'+release
    obj['spec']['selector']['matchLabels']={'app':'hello','release':release}
    obj['spec']['template']['metadata']['labels']={'app':'hello','release':release}
    obj['spec']['template']['spec']['containers'][0]['env']=[{'name':'DS60_MESSAGE','value':message}]
service=copy.deepcopy(hello(True)[1]);service['spec']['selector']={'app':'hello','release':'stable'}
author(34,
'''A rollout creates or replaces workload replicas; a traffic change determines which ready backends receive requests. Those operations are related but different. A Deployment can finish creating a candidate while the Service still selects only the stable release. Conversely, broadening a selector can send requests to a candidate before the team has collected the intended application evidence.

The host fixture has hello-stable and hello-candidate Deployments with distinct release labels. Both use the same preloaded0.2 image, but /message returns hello or reviewer through a fixed environment value. This is a configuration-release rehearsal. It does not demonstrate a binary image upgrade, and /version remains the legacy fixture version string for both. A real two-image rehearsal requires separately qualified, preloaded image identities.

A release gate states what must be true before changing traffic and what triggers rollback. For this small fixture, require the expected candidate marker, zero unexpected payloads and zero errors in a declared finite request sample. That sample is evidence about the observed requests, not a proof of all future behavior or an exact traffic-share guarantee.''',
[
('Compare rolling and two-version selection','''A rolling Deployment update gradually changes replicas under one controller. Old and new Pods may coexist while readiness controls endpoint eligibility. The update strategy bounds replacement behavior, but it does not by itself evaluate whether the new application gives correct answers.

The two-Deployment fixture makes traffic selection explicit. Service hello starts with selector app=hello,release=stable. The candidate has matching app but a different release label, so it is excluded. Changing the release selector to candidate is a coarse cutover; a reviewed host operation must preserve Service identity and handle concurrent edits rather than replacing an unrelated object.

A canary exposes a subset of traffic to the candidate. Simply having one candidate Pod and one stable Pod does not prove a50percent request split. Connection reuse, endpoint selection, client behavior and topology can affect finite samples. Weighted routing requires a separately qualified traffic controller; the current browser adapter has none.'''),
('Build an application release gate','''Before cutover, probe the candidate through the host's fixed path and record message marker, error count, sample size and latency summary. A Ready Pod only says its probe passed. The marker confirms which configuration answered, while a schema or business assertion confirms whether the answer is acceptable.

After the selector change, collect another bounded sample through the ordinary Service. Record the Service UID, resourceVersion and selected endpoint identities. A candidate marker from a direct Pod check does not prove Service traffic moved. Mixed markers during a transition need an explanation based on actual connections and endpoints, not an assumed instantaneous global switch.

Rollback should restore the last verified selector or desired state through a conditional, identity-checked operation. Then verify the stable marker through the Service. Deleting the candidate without restoring a selector that points to it can leave the Service with no endpoints. Cleanup order therefore belongs in the runbook.'''),
('Avoid overclaiming a small release test','''The two markers represent different configuration values in the same binary. Keep that distinction visible in the release packet. A successful finite sample cannot establish production capacity, error probability zero or exact canary ratios.

If the candidate fails, retain its observations and restore the verified path. Do not loosen the gate after seeing a failure merely to label the release successful. Predeclare acceptable conditions and record any later policy revision as a separate decision.''')],
[
('Trace Service selection','```yaml\n'+yaml.safe_dump(service,sort_keys=False)+'```\nhello-stable has app=hello,release=stable. hello-candidate has app=hello,release=candidate.','Only the stable backend matches this selector, regardless of whether the candidate is Ready.'),
('Evaluate a candidate and rollback','''Synthetic candidate sample: reviewer,reviewer,ERROR,reviewer. The gate requires four valid reviewer responses and zero errors. It fails. Restore stable selection, then observe hello,hello,hello,hello through the Service.''','The candidate is rejected; the four stable responses establish the finite rollback observation, not an unlimited future guarantee.')],
[
('Distinguish binary and configuration versions','Compare /version with /message in both fixture Deployments.','Same binary version; different synthetic configuration markers.','The image field is identical.','A useful experiment must name what changed. Calling this a binary upgrade would claim a version transition that never happened. The marker still provides a valid way to trace routing to two different configured backends.'),
('Predict selected backends','Apply the stable selector to the two Deployment label sets.','Stable matches and candidate does not.','Selectors combine their key-value requirements.','Readiness cannot override a label mismatch. The candidate can be healthy yet receive no Service traffic, which is often intentional before a controlled cutover and explains why Pod checks and Service checks answer different questions.'),
('Predeclare the release gate','Specify marker, sample size, error rule and bounded request deadline.','A concrete gate that can fail independently of Ready replicas.','Use application observations, not only Kubernetes counts.','The gate must be chosen before examining the candidate results. Retain exact sample semantics so a reviewer can tell whether retries hid failures or whether only successful responses were counted.'),
('Reject the failing candidate','Evaluate reviewer,reviewer,ERROR,reviewer against the four-response gate.','Failure with one error; do not proceed to promotion.','Count all attempted requests.','A finite negative result is actionable because it violates the declared rule. Retrying until four successes appear would change the experiment and conceal the failure rate observed during the original window.'),
('Restore and verify stable traffic','Use the conditional host selector repair, then sample the ordinary Service.','Correct Service identity and four observed hello responses.','Removing a candidate is not the same as restoring a route.','The rollback sequence needs an application confirmation through the same path users would take. A selector still pointing to deleted candidate Pods can leave no endpoints even though the stable Deployment remains healthy.'),
('Explain ratio and evidence limits','Compare one-to-one replica counts with an uneven finite request sample.','Replica ratio does not establish an exact traffic ratio or production reliability.','Connections and routing policy affect samples.','The final review should identify the routing mechanism, sample size and remaining uncertainty. A real weighted canary or binary release would require additional qualified capabilities and separate evidence.')],
[stable,candidate,service],
'''
def selects(selector,labels):return all(labels.get(k)==v for k,v in selector.items())
def gate(samples,marker,count=4):return len(samples)==count and all(x==marker for x in samples)

def main():
    selector={'app':'hello','release':'stable'}
    assert selects(selector,{'app':'hello','release':'stable'})
    assert not selects(selector,{'app':'hello','release':'candidate'})
    assert not gate(['reviewer','reviewer','ERROR','reviewer'],'reviewer')
    assert gate(['hello']*4,'hello')
    print('k8s-034 synthetic selector and release gates passed; no live traffic changed')

if __name__ == "__main__":
    main()
''',capability='identity-checked host traffic edits and bounded two-configuration request samples',refs=['[Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)','[Kubernetes Services](https://kubernetes.io/docs/concepts/services-networking/service/)'])

cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'hello-config'},'data':{'message':'hello'}}
author(35,
'''A read-modify-write operation can lose another client's change if it assumes the object stayed unchanged after reading. Kubernetes uses resourceVersion for optimistic concurrency. The client submits a conditional update based on the version it read; if the stored object changed, the server can reject the stale update with409 Conflict. The correct recovery is to read current state and recompute the intended change, not repeatedly force the old snapshot over newer state.

resourceVersion is an opaque token supplied by the server. Treat it as a string for the API contract. Do not increment it, subtract two versions to estimate elapsed time or use it as a user-defined clock. UID identifies an object lifetime, while resourceVersion identifies a state version within API semantics. Recreating the same name can change UID and invalidate an operation's ownership assumptions.

A watch streams changes after a starting point, reducing repeated full-list work. It can disconnect, deliver repeated information or expire beyond the server's retained history. A robust observer rebuilds a current snapshot when required and reconciles from that state. The normal course credential does not offer arbitrary watch/update operations; this is a host-scoped advanced activity with an offline trace model.''',
[
('Trace a conflict without losing intent','''Client A and client B read the same ConfigMap UID u1 at token rv-A with message hello. B writes reviewer and receives a new token rv-B. A then tries an update carrying rv-A. The server returns conflict because A's premise is stale. A should reread u1 at rv-B and decide whether its intended change still makes sense.

Recomputation is important when the edit is relative, such as adding one approved entry or merging a field. Replacing the entire old object can erase B's unrelated field changes. A bounded retry budget prevents an indefinitely contended object from holding a lesson operation forever. Cancellation must stop retries and leave the current object recoverable.

If A rereads the same name with UID u2, this is a replacement object. The course ownership contract stops instead of updating it. A resourceVersion comparison alone does not authorize mutation across identity replacement.'''),
('Recover a watch from current state','''A typical observer obtains a list snapshot and its resourceVersion, then watches from that point. It maintains a local view as matching events arrive. A bookmark can indicate progress in the stream; it does not describe a new workload object that should be created or counted as an application event.

When the server reports that the requested history is too old, commonly410 Gone, relist and rebuild the current view before watching again. Replaying an imagined sequence of missing events is unsafe because those events are not available. A level-driven reconciler can act on the new snapshot without needing every intermediate transition.

Deleting and recreating a name must replace the local identity entry, not silently merge old-owner state with the new object. Duplicate events should not double-count side effects. Watches provide observation, not an exactly-once external action guarantee.'''),
('Choose the right edit and evidence boundary','''A conditional replace, a patch with appropriate preconditions and server-side apply have different merge/ownership semantics. This lesson models compare-and-swap on a tiny object; it does not teach that every PATCH automatically prevents lost updates. Specify the actual API operation and precondition when reviewing a live client.

A supplied409 or410 trace is a deterministic teaching fixture. A live receipt must include the exact owned identity, request outcome and bounded recovery observation without exposing credentials. Do not enable broad watch or write permissions merely to make a reading exercise runnable in the normal module pad.''')],
[
('Replay a stale conditional update','''Store: UID u1,resourceVersion rv-B,message reviewer. Request: expected UID u1,expected token rv-A,new message hello. Identity matches,version does not. Refuse with conflict and preserve reviewer.''','The stale request changes nothing. A reread is required before a new bounded attempt.'),
('Rebuild after expired history','''Local cache holds hello-config UID u1. Watch reports410. A fresh list now contains hello-config UID u2,message reviewer. Replace the cache from the snapshot, then resume observation with its list token.''','The current cache contains u2 only; no invented intermediate event or old-UID mutation is permitted.')],
[
('Separate name,UID and version','Explain the role of hello-config,u1 and rv-A.','Name addresses an object; UID its lifetime; resourceVersion is an opaque API token.','A reused name is not a reused identity.','The distinctions prevent accidental updates after replacement and incorrect arithmetic on server tokens. A human-friendly name is useful navigation, but it is not enough for a destructive or ownership-sensitive operation.'),
('Predict the conflict','Apply an rv-A update to stored rv-B with the same UID.','409-style conflict with current data unchanged.','The precondition is checked before mutation.','Optimistic concurrency detects that the read premise became stale. The rejection protects the newer state, but the client still has to handle it explicitly rather than treating conflict as an unexplained generic failure.'),
('Recompute after reread','Read rv-B and preserve unrelated fields while reconsidering the intended message edit.','A new conditional request uses current state and a bounded retry count.','Do not resend the old whole-object snapshot.','A correct retry is a fresh decision based on current state. The desired change may no longer be necessary or appropriate. Bounded retries and cancellation make contention visible instead of hiding an endless loop.'),
('Stop on replacement identity','Reread the same name with UID u2 when the lease expected u1.','Refuse the mutation across object replacement.','Ownership follows the recorded UID.','The new object may belong to another actor or a later operation. Updating it solely because the name matches violates the original operation scope, even if its content looks familiar.'),
('Recover from watch expiration','Replace a stale cache with a supplied fresh list after410.','Current u2 snapshot retained; watcher restarts from the new list token.','Relist instead of guessing missed events.','The server no longer promises the requested historical stream. Rebuilding from current state is compatible with level-driven reconciliation and avoids fabricating a sequence that may never have happened.'),
('Handle bookmarks and duplicates','Classify a bookmark and a repeated modified event.','Bookmark advances progress; duplicate state does not repeat external effects.','Observation events are not a transaction log.','The observer should separate stream progress from application objects and make side effects idempotent. A watch reconnect is expected operational behavior, not evidence that each event must trigger another create or external call.')],
[cm],
'''
def replace(store,expected_uid,expected_rv,message):
    if store['uid']!=expected_uid:return 'identity-refused',dict(store)
    if store['rv']!=expected_rv:return '409',dict(store)
    return 'accepted',{**store,'message':message,'rv':'server-next-token'}

def main():
    store={'uid':'u1','rv':'rv-B','message':'reviewer','other':'preserve'}
    status,after=replace(store,'u1','rv-A','hello')
    assert status=='409' and after==store
    status,after=replace(store,'u1','rv-B','hello')
    assert status=='accepted' and after['other']=='preserve'
    assert replace({**store,'uid':'u2'},'u1','rv-B','hello')[0]=='identity-refused'
    cache={'hello-config':{'uid':'u1'}}
    fresh={'hello-config':{'uid':'u2','message':'reviewer'}}
    cache=dict(fresh)
    assert cache['hello-config']['uid']=='u2'
    print('k8s-035 synthetic concurrency and relist passed; resourceVersion tokens remain opaque')

if __name__ == "__main__":
    main()
''',capability='owned-object conditional update and bounded watch/relist observer',refs=['[Kubernetes API concepts](https://kubernetes.io/docs/reference/using-api/api-concepts/)','[Server-side apply field ownership](https://kubernetes.io/docs/reference/using-api/server-side-apply/)'])
