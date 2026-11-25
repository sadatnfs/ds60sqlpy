"""Lesson-specific teaching prose for the networking extension, k8s-043 to k8s-066.

Each entry supplies the parts of a guide that used to be shared boilerplate:
- trace: how to read this lesson's diagram
- run: which fixture files model the lesson and what the offline check can and cannot prove
- reads: kubectl arguments for one scoped observation in an owned lab
- read_note: which output fields answer the lesson's questions
- hints: one progressive hint per exercise, never the answer
- mistakes: lesson-specific diagnosis and common mistakes
- retrieval: a transfer prompt with a changed case

Shared workflow, run boundary and diagnosis rules live in courses/kubernetes/STUDY-GUIDE.md.
"""

FX = "../fixtures/networking"

TEACHING = {
    "k8s-043": dict(
        trace=(
            "Follow the arrows left to right and attach an owner to each address. The caller Pod dials "
            "10.96.0.20:80 because DNS or configuration gave it the Service, and the data plane on the "
            "caller's node rewrites that destination to 10.244.1.7:8080. The second line is not a hop at "
            "all: 192.0.2.10 only tells you which machine hosts the listener."
        ),
        run=(
            f"The fixture's [topology.json]({FX}/topology.json) is this lesson's whole universe: two node "
            "addresses in 192.0.2.0/24, two Pod addresses inside 10.244.0.0/16 and one Service address "
            "inside 10.96.0.0/16. The checker confirms each address sits in the range its role claims and "
            "that every Pod names a real node. It cannot tell you what your own cluster actually allocated, "
            "so live addresses must come from a read."
        ),
        reads=[
            "get pods -l app=network-study -o custom-columns=POD:.metadata.name,UID:.metadata.uid,POD_IP:.status.podIP,NODE_IP:.status.hostIP",
            "get service network-study -o custom-columns=NAME:.metadata.name,CLUSTER_IP:.spec.clusterIP,PORT:.spec.ports[*].port",
        ],
        read_note=(
            "Put the columns side by side: POD_IP and NODE_IP come from Pod status, CLUSTER_IP from the "
            "Service spec. Replace one Pod through the host lab and read again. The UID and POD_IP change "
            "while CLUSTER_IP stays the same, which is the evidence Exercise 2 and Exercise 6 ask for."
        ),
        hints=[
            "For each address, find the object that reports it: a Node status, a Pod status or a Service spec.",
            "Ask which object a Deployment recreates and which one nobody recreates. Only the recreated one gets new identity fields.",
            "The Service port entry holds two numbers. Decide which one the caller dials and which one the process binds.",
            "A ClusterIP lives in node rules inside the cluster. Does your laptop's routing table have any entry for 10.96.0.0/16?",
            "Ask who hands out each address and what sits in front of it: the machine's network or a provider's edge.",
            "Two observations are involved: the request succeeded, and the UID differs. Which object does each belong to?",
        ],
        mistakes=(
            "The classic mistake in Exercise 4 is treating 10.96.0.20 as a machine. No interface owns a "
            "ClusterIP; it exists only as translation rules on cluster nodes, so a host browser outside the "
            "cluster usually times out rather than getting a refusal. A second mistake is writing a Pod IP "
            "into configuration as if it were stable: the next rollout hands out a new one and the old "
            "address may later belong to a different Pod. A third is copying the node address column as the "
            "Pod's address because `kubectl get pods -o wide` prints them next to each other. When a request "
            "fails, first write down which of the three address roles the caller actually used, then look "
            "only at the component that owns that role."
        ),
        retrieval=(
            "Without the guide, redraw the path for a caller that uses node-b's address 192.0.2.11 instead "
            "of the Service name. What port would it need, what Service type would have to exist, and which "
            "Pod could answer given that pod-b is not ready? Then name the one field that changes if pod-a "
            "is replaced and the one that does not."
        ),
    ),
    "k8s-044": dict(
        trace=(
            "The first line is the decision every sender makes: compare the destination with the routing "
            "table and let the longest matching prefix win. The second line lists the ranges that must "
            "never compete in that lookup. If a host or VPN route covers part of 10.244.0.0/16, the more "
            "specific route can carry traffic away before any Kubernetes component sees it."
        ),
        run=(
            f"[topology.json]({FX}/topology.json) declares Pod CIDR 10.244.0.0/16 and Service CIDR "
            "10.96.0.0/16. The checker uses Python's ipaddress module to prove each Pod address and the "
            "Service address fall inside their declared ranges and that the two ranges do not overlap. That "
            "is arithmetic on supplied text. Your laptop's VPN routes and the ranges your real cluster was "
            "configured with are outside its view."
        ),
        reads=[
            "get pods -l app=network-study -o custom-columns=POD:.metadata.name,POD_IPS:.status.podIPs[*].ip",
            "get service network-study -o custom-columns=NAME:.metadata.name,CLUSTER_IPS:.spec.clusterIPs",
        ],
        read_note=(
            "Paste each observed address into the membership check from worked example 1 and test it "
            "against the range your cluster was actually given, not 10.244.0.0/16 by assumption. Node "
            "podCIDR fields are cluster scoped, so a namespace lease may answer Forbidden for them; that "
            "is a permission boundary, not a reason to change credentials."
        ),
        hints=[
            "Write the /16 as its first and last address. Membership is just whether 10.244.1.7 falls between them.",
            "Each extra prefix bit halves the set. Count the bits between /16 and /24 before computing sizes.",
            "List every range a packet from your laptop might match, including ones Kubernetes never mentions, such as a home router.",
            "Longest prefix match picks the route. Compare the VPN prefix length with the cluster route for the same destination.",
            "Network and broadcast addresses, per-node slicing and max-pods settings all come out of the same block.",
            "Put the first cluster's ranges beside the proposed ones and check every pair, not only Pod against Pod.",
        ],
        mistakes=(
            "Overlap problems rarely look like routing problems. When a VPN on the host installs a route "
            "that covers the Pod or Service range, tools on the host that reach into a local cluster send "
            "packets into the tunnel instead, while everything inside the cluster keeps working, so people "
            "blame the Service or the app. The opposite mistake is assuming a /24 per node gives 256 usable "
            "Pods; reserved addresses, the plugin's allocation scheme and the kubelet's max-pods setting all "
            "reduce that. Also avoid checking membership by eye on string prefixes: 10.244.1.7 and "
            "10.24.41.7 look alike and only one is inside 10.244.0.0/16. Compute with ipaddress, and keep "
            "the result next to the exact range you tested."
        ),
        retrieval=(
            "Plan a second local cluster that must coexist with this fixture and with a VPN that owns "
            "172.16.0.0/12. Choose its Pod and Service CIDRs, prove with ipaddress that none of the five "
            "ranges overlap, and say which overlap would produce the hardest symptom to diagnose, and from "
            "which caller."
        ),
    ),
    "k8s-045": dict(
        trace=(
            "The first line stays inside one network namespace: the app and its sidecar share a loopback "
            "interface, so 127.0.0.1:8080 reaches whichever container bound that port. The second line "
            "crosses namespaces, and there loopback means the caller's own Pod. A caller in another Pod "
            "needs the Pod IP and a listener bound to a reachable interface such as 0.0.0.0."
        ),
        run=(
            f"[deployment.yaml]({FX}/deployment.yaml) shows a single container named app declaring the "
            "named port http on 8080, and the checker resolves that name to a number. Nothing in the "
            "fixture proves which interface the process binds, and the fixture has no sidecar, so the "
            "two-container port layout in Exercise 3 is a design you write and defend, not something the "
            "checker validates for you."
        ),
        reads=[
            "get pods -l app=network-study -o custom-columns=POD:.metadata.name,CONTAINERS:.spec.containers[*].name,PORTS:.spec.containers[*].ports[*].containerPort,INIT:.spec.initContainers[*].name",
        ],
        read_note=(
            "This read lists containers and their declared ports; a native sidecar appears under "
            "initContainers with restartPolicy Always. It shows no sockets. Proving that a process accepts "
            "connections on 8080 from outside its Pod needs a bounded request from another owned Pod, "
            "because a declared containerPort is only metadata."
        ),
        hints=[
            "Two containers in one Pod: how many network namespaces, and so how many loopback interfaces, exist?",
            "The client's 127.0.0.1 is evaluated inside the client's own namespace. Whose loopback is that?",
            "One Pod means one port table. Give each process its own number and mark which one other Pods may reach.",
            "The second bind call fails. Find which container's log reports the address already in use.",
            "Delete the containerPort line in your head. Would the process still accept connections?",
            "List what the helper shares with the app: start and stop timing, replica count, loopback access and failure impact.",
        ],
        mistakes=(
            "When the second container in Exercise 4 crashes with an address-in-use error, people blame the "
            "image or the probe. Read that container's own log first; the failed bind is reported there. A "
            "related mistake is assuming `containerPort` opens or reserves a port: removing it changes "
            "nothing about the socket, and adding it does not make a loopback-only listener reachable from "
            "other Pods. The reverse trap is an app bound to 127.0.0.1 that passes every check run inside "
            "its own Pod yet refuses connections on the Pod IP. Check the bind address before you touch the "
            "Service or any policy, because neither can fix a listener that only accepts local callers."
        ),
        retrieval=(
            "Design a Pod with an app on 8080, a metrics sidecar and a proxy sidecar that must be the only "
            "path from other Pods. Assign ports and bind addresses, say which listener other Pods may reach, "
            "and predict what a different Pod sees when it requests the app's port directly."
        ),
    ),
    "k8s-046": dict(
        trace=(
            "Read the first line as two layers. PodA and PodB addresses ride inside; when an overlay "
            "encapsulates, node addresses such as 192.0.2.10 and 192.0.2.11 carry the packet across the "
            "underlay. The second line is the budget: every encapsulation header is paid for out of the "
            "same path MTU, so large payloads are the first to fail."
        ),
        run=(
            f"[topology.json]({FX}/topology.json) places pod-a on node-a and pod-b on node-b, the cross-node "
            "pair this lesson traces, and the checker confirms every Pod references a real node. It says "
            "nothing about which CNI plugin you run, whether it encapsulates or routes natively, or the MTU "
            "of any interface. Those are properties of the network implementation, recorded from the "
            "operator's receipt in an owned lab."
        ),
        reads=["get pods -l app=network-study -o wide"],
        read_note=(
            "The NODE column tells you whether a request between two Pods must cross the underlay at all. "
            "Plugin mode and MTU are not visible through the Kubernetes API in your namespace; they live in "
            "the plugin's configuration, usually readable only by the operator, so copy them from the lab "
            "receipt instead of guessing."
        ),
        hints=[
            "One is a specification for how a runtime asks for an interface; the other is software that builds routes. Which is which?",
            "In worked example 1, find the header added on node-a and removed on node-b. Its addresses are the outer pair.",
            "Start at PodA's interface and do not skip the node. Each hand-off between namespaces or machines is one arrow.",
            "Small and large requests take the same route. What changes with payload size along that route?",
            "Where does the kubelet send the readiness request from, and how far does that packet travel?",
            "Name the plugin and version from the receipt first, then choose reads and probes that leave its configuration untouched.",
        ],
        mistakes=(
            "The MTU symptom in Exercise 4 is confusing because health checks keep passing: small probe "
            "responses fit, while a large JSON body or a TLS certificate chain stalls. Do not raise "
            "application timeouts or blame the server first. Compare one small and one large bounded "
            "request between Pods on different nodes and see whether size alone flips the result. Another "
            "error is treating CNI as a product name. Two clusters can both say CNI and use different "
            "routing, encapsulation and policy engines, so advice copied from one may be wrong for the "
            "other. Never replace or reconfigure the plugin to test a theory; ask the operator for its "
            "documented mode and MTU."
        ),
        retrieval=(
            "Suppose the underlay MTU is 1400 instead of 1500 and the overlay still adds 50 bytes. Recompute "
            "the inner budget from worked example 2, then describe the smallest pair of requests between "
            "pod-a on node-a and a Pod on node-b that would show whether MTU is the cause."
        ),
    ),
    "k8s-047": dict(
        trace=(
            "The two lines run on different clocks. The bottom line is control: the selector "
            "app=network-study is evaluated continuously and the result lands in an EndpointSlice. The top "
            "line is one connection: at connect time the data plane picks one ready address from that slice "
            "and rewrites 10.96.0.20:80 to it. Repair a broken top line by reading the bottom one."
        ),
        run=(
            f"[service.yaml]({FX}/service.yaml) and [deployment.yaml]({FX}/deployment.yaml) are the pair this "
            "lesson reads: the Service selects app=network-study and maps port 80 to targetPort http, and "
            "the Deployment's container names that port on 8080. The checker proves the selector matches "
            "the Pod template labels and the name resolves to 8080. It cannot prove that kube-proxy "
            "programmed anything or that a connection succeeds."
        ),
        reads=["get endpointslices -l kubernetes.io/service-name=network-study -o yaml"],
        read_note=(
            "In the slice, `ports[].port` should be 8080, and each `endpoints[].conditions.ready` says "
            "whether that address can receive new connections. Compare every `endpoints[].targetRef.name` "
            "with your Pod list. An empty `endpoints` list beside a healthy ClusterIP is exactly the case "
            "in Exercise 4."
        ),
        hints=[
            "Find the two numbers on the Service port entry and decide which side of the translation each belongs to.",
            "The selector is a filter over Pod labels. Change it in the record and ask which Pods still pass.",
            "Name four things in order: who connects, to which virtual address, which endpoint was chosen, which process accepts.",
            "Before looking past the Service, compare its selector with real Pod labels and check each Pod's Ready condition.",
            "Ask what a TCP connection contains at the moment its endpoint is chosen. Is the URL path visible yet?",
            "Clients need a name that survives Pod replacement. Which object in this lesson keeps its address while Pods change?",
        ],
        mistakes=(
            "The most common ClusterIP failure is a selector typo: the Service exists, has an address and "
            "resolves in DNS, yet its slice is empty, so connections fail in a way that depends on the data "
            "plane. Read the EndpointSlice before changing anything else. Another frequent slip is setting "
            "targetPort to the Service port, 80, when the container listens on 8080; referring to the named "
            "port http avoids that and survives a later port change. Finally, expecting one ClusterIP to "
            "split /api and /web traffic confuses Layer 4 with Layer 7. A Service chooses a connection's "
            "endpoint without reading HTTP, so path routing needs Ingress or Gateway API."
        ),
        retrieval=(
            "Change the fixture so the container listens on 9090 under the same port name http. List which "
            "of the Service, the EndpointSlice and the client URL change, then predict the result if someone "
            "had hard-coded targetPort 8080 instead of using the name."
        ),
    ),
    "k8s-048": dict(
        trace=(
            "The two lines are separate phases with separate evidence. Line one turns a short name into an "
            "address using the resolver's search list and any cached answer, so the namespace you ask from "
            "matters. Line two starts only after an address exists. A correct answer of 10.96.0.20 followed "
            "by a failed connection is a line-two problem, not a DNS problem."
        ),
        run=(
            f"[topology.json]({FX}/topology.json) supplies namespace study-example and cluster domain "
            "cluster.local, so the fully qualified name from worked example 1 is "
            "network-study.study-example.svc.cluster.local. The checker treats those as declared strings. A "
            "real cluster may use another domain, and only a resolver query from an owned Pod shows what "
            "your search path actually returns and from which suffix."
        ),
        reads=[
            "get service network-study -o custom-columns=NAME:.metadata.name,NAMESPACE:.metadata.namespace,CLUSTER_IP:.spec.clusterIP",
        ],
        read_note=(
            "kubectl reads the API, not DNS, so this read tells you what a correct answer should contain: "
            "the namespace that completes the name and the ClusterIP the A record should return. Compare it "
            "with a resolver answer captured from an owned client Pod, and note which search suffix "
            "produced the match."
        ),
        hints=[
            "Write out the client Pod's search list. Its first suffix is built from the client's own namespace.",
            "Two parts of the long name come from cluster configuration rather than from the Service. Which one is asked about?",
            "Draw a line between having an address and having a connection. Each side needs its own observation.",
            "If the address works and the name does not, the listener is fine. Look at what turns the name into the address.",
            "Separate the two Service types: one name resolves to a virtual IP, the other to the Pod addresses themselves.",
            "Decide what the client knows in advance, how long it waits at each phase and when it resolves again.",
        ],
        mistakes=(
            "Short names cause most surprises. A client in namespace tools asking for network-study tries "
            "network-study.tools.svc.cluster.local first and either fails or, worse, reaches a same-named "
            "Service there. Use the namespaced name whenever the namespace is known. Another mistake is "
            "hard-coding cluster.local; some clusters use a different domain. When direct-IP requests work "
            "and named ones fail, read the client's /etc/resolv.conf and check whether an egress policy "
            "blocks UDP and TCP 53 to the DNS Service before suspecting the app. Finally, a negative answer "
            "cached by the client can outlive the fix, so wait out its TTL before declaring the repair failed."
        ),
        retrieval=(
            "A client in namespace tools reaches the wrong backend when it asks for network-study. Write the "
            "exact name it should use, the records it should receive for network-study and for "
            "network-study-headless, and one resolver observation that would prove which namespace answered."
        ),
    ),
    "k8s-049": dict(
        trace=(
            "Line one is two inputs feeding one controller: Pod readiness and the Service selector. Its "
            "output is a set of endpoint conditions, not traffic. Line two shows the data plane consuming "
            "those conditions later, so a slice can already say pod-a is ready while some node has not "
            "caught up. Only a fresh request names the backend that actually answered."
        ),
        run=(
            f"[topology.json]({FX}/topology.json) gives network-study two endpoints: pod-a on node-a marked "
            "ready and pod-b on node-b marked not ready. The checker joins them to the Service selector and "
            "asserts that pod-a is the only eligible identity, which models the controller's decision. Real "
            "slices also carry serving and terminating conditions and can be split across several objects, "
            "which the fixture does not show."
        ),
        reads=[
            "get endpointslices -l kubernetes.io/service-name=network-study -o custom-columns=SLICE:.metadata.name,ADDRESSES:.endpoints[*].addresses[0],READY:.endpoints[*].conditions.ready,POD:.endpoints[*].targetRef.name",
        ],
        read_note=(
            "Expect one row per slice, and aggregate every row before you conclude anything. For each "
            "endpoint, compare its targetRef with the current Pod list and that Pod's UID, because a slice "
            "can briefly list a Pod that was already replaced. A false READY beside a Running Pod is "
            "Exercise 4's signature."
        ),
        hints=[
            "Read the ready field for both endpoints in topology.json. Which Pod has the value ordinary traffic requires?",
            "One Service can own several slices. Collect every slice with its service-name label, then remove duplicate addresses.",
            "Each endpoint carries a targetRef. Compare its UID with the Pods that exist now, not with names alone.",
            "Running describes the process. Find the condition that decides whether new connections may be sent there.",
            "A terminating Pod can still be serving. Which of the three conditions changes first during graceful shutdown?",
            "You need two things: the new UID listed as ready, and a response that only that backend could have produced.",
        ],
        mistakes=(
            "When a Service has no ready endpoints, the reflex is to restart Pods, which erases the evidence. "
            "A Pod can be Running and still unready because its /ready probe fails, so read the probe result "
            "and the endpoint condition together. Another mistake is reading only the first slice; large and "
            "dual-stack Services spread endpoints across several. Do not treat serving and ready as "
            "synonyms: during termination an endpoint can be serving but not ready, and some proxies still "
            "use it for existing traffic. Join endpoints to Pods by UID, not by name, because a recreated Pod "
            "or a StatefulSet member can reuse the old name."
        ),
        retrieval=(
            "pod-b becomes ready and pod-a starts terminating at the same moment. Write the endpoint "
            "conditions you expect for each in the next slice update, then name the request evidence that "
            "would show new connections moving to pod-b while existing ones finish on pod-a."
        ),
    ),
    "k8s-050": dict(
        trace=(
            "The first line is asynchronous: a watcher on every node notices Service and EndpointSlice "
            "changes and rewrites local state, whether iptables chains, nftables maps, IPVS tables or eBPF "
            "maps. The second line happens per packet with no API call at all. A slow or broken watcher "
            "leaves one node with stale rules while the API looks perfectly correct."
        ),
        run=(
            f"No fixture file models a data plane. The Service in [service.yaml]({FX}/service.yaml) and the "
            "two endpoints in topology.json are the input any proxy mode would program, and the checker "
            "validates only that input. Which mode your cluster runs, what its rules look like and whether "
            "every node is current are runtime facts. Reading them needs node access that an ordinary "
            "namespace lease does not grant."
        ),
        reads=[
            "get endpointslices -l kubernetes.io/service-name=network-study -o custom-columns=SLICE:.metadata.name,GENERATION:.metadata.generation,RESOURCE_VERSION:.metadata.resourceVersion",
        ],
        read_note=(
            "These versions are the API side of the watch-to-packet sequence. If one node behaves "
            "differently, the operator compares that node's programmed rules with this state. Your lease "
            "cannot list node rules or the proxy configuration in kube-system, and a Forbidden there marks "
            "the boundary of what you can observe."
        ),
        hints=[
            "One is a stored object you can read with kubectl; the other is state in each node's kernel. Which one handles packets?",
            "Read the expected answer's release timeline: defaults and deprecations moved between 1.33 and 1.35.",
            "Number the steps from API write to packet decision and mark where a delay could leave a node behind.",
            "If the Service spec were wrong, every node would fail. What can differ between one node and the others?",
            "eBPF changes how lookups run in the kernel. Does that tell you anything about the response body?",
            "Before reading any rules, write down the mode, the versions and which diagnostics the operator approved.",
        ],
        mistakes=(
            "Reading iptables output before confirming the proxy mode wastes time: an nftables or eBPF "
            "cluster may have almost no relevant iptables rules, and that absence proves nothing. Another "
            "mistake is copying advice from an older release; IPVS deprecation and nftables graduation "
            "changed what is normal. When only one node fails, resist editing the Service. The API object "
            "is shared by every node, so compare the failing node's programmed state and proxy logs with a "
            "healthy node instead. Never flush rules or restart a node's proxy outside the operator's "
            "approved procedure, because that destroys the stale state you were trying to observe."
        ),
        retrieval=(
            "Requests from Pods on node-b fail while node-a works, and the Service and slice look correct. "
            "Write the three facts you would ask the operator for, in order, and the observation that "
            "would distinguish a stale rule set on node-b from a policy difference on node-b."
        ),
    ),
    "k8s-051": dict(
        trace=(
            "Two entry points share one logical Service. The external line enters at a node address and "
            "node port, and that node's data plane forwards to any ready Pod, possibly on another node. The "
            "internal line never touches 30080. Both end at the Pod listener 8080. When a laptop request "
            "times out, check the first arrow, reaching the node, before anything inside the cluster."
        ),
        run=(
            f"The maintained [service.yaml]({FX}/service.yaml) is a ClusterIP Service, so this lesson's "
            "NodePort is the synthetic variant in the worked examples, with port 80, targetPort http and "
            "nodePort 30080. The checker still validates the shared parts, the selector and the named port. "
            "Whether 192.0.2.10:30080 is reachable from your desk depends on the VM, kind container or "
            "firewall between you and the node."
        ),
        reads=[
            "get service network-study -o custom-columns=TYPE:.spec.type,PORT:.spec.ports[*].port,TARGET:.spec.ports[*].targetPort,NODE_PORT:.spec.ports[*].nodePort",
        ],
        read_note=(
            "On the maintained fixture TYPE is ClusterIP and NODE_PORT is empty, which is correct. If an "
            "owned lab deliberately applies a NodePort variant, this read shows the allocated port. That "
            "allocation is API state only; a host request through the node address is the separate "
            "reachability evidence."
        ),
        hints=[
            "Follow a packet from outside: which number does it carry at the node, after the Service, and at the process?",
            "Allocating a port on a node changes nothing about who can route to that node. Where does the node address live?",
            "On a local engine the node is itself a container or VM. Draw that boundary between your host and the node.",
            "A timeout before the node means Kubernetes never saw the packet. Check the host-side mapping first.",
            "The range is an API server flag. Must every cluster keep the same default?",
            "Compare who can use each path, how long it lasts and which process carries the bytes.",
        ],
        mistakes=(
            "People often open localhost:30080 in a browser and conclude NodePort is broken. With kind or a "
            "desktop VM, the node is not localhost unless a port mapping was configured when the cluster was "
            "created. Another mistake is hard-coding 30080 everywhere; leave the field empty and the API "
            "allocates from the configured range, and that range itself can differ between clusters. Do not "
            "confuse NodePort with port-forward either: port-forward tunnels through the API server to one "
            "Pod and stops when the command ends, while NodePort opens the port on every node. Never open "
            "every node port in a firewall to test a theory."
        ),
        retrieval=(
            "Write the full path for a request from your host to network-study through a kind cluster whose "
            "node container maps host port 8080 to node port 30080. Label every port, then predict what "
            "happens to that request if pod-a becomes unready while pod-b is still unready."
        ),
    ),
    "k8s-052": dict(
        trace=(
            "The top line is a request for infrastructure: a controller outside the core reads the Service "
            "and asks a cloud provider, or a local implementation, for an address. The bottom line is what "
            "a client then traverses. An address in Service status covers only the top line; the listener, "
            "health checks, backend path and application each need their own evidence."
        ),
        run=(
            "There is no LoadBalancer manifest in the fixture. The lesson treats network-study as the backend "
            f"a load balancer would front, and the checker covers that backend: the selector in "
            f"[service.yaml]({FX}/service.yaml), the named port and the one ready identity. No local "
            "controller is assumed, so on an ordinary kind cluster a LoadBalancer Service stays pending, "
            "which this lesson records as an honest unavailable capability."
        ),
        reads=[
            "get services -o custom-columns=NAME:.metadata.name,TYPE:.spec.type,EXTERNAL:.status.loadBalancer.ingress[*].ip",
        ],
        read_note=(
            "An empty EXTERNAL column on a LoadBalancer Service means no controller has fulfilled it, the "
            "pending case in worked example 1. An address there is necessary but not sufficient: follow it "
            "with one bounded request to the listener and record the exact response body."
        ),
        hints=[
            "Ask which component would fulfil the request on this cluster. Is one installed at all?",
            "Split the work into deciding and doing: one part watches the Service, the other owns the real network resources.",
            "After the external listener, draw two variants: one stops at a node, the other goes straight to a Pod address.",
            "Walk the bottom line of the diagram one arrow at a time. The address proves only that the first arrow exists.",
            "List what the provider's health check requests and what the kubelet's readiness probe requests. Are they the same?",
            "For each environment, name the implementation, who pays and cleans up, and the request that proves success.",
        ],
        mistakes=(
            "A pending external address on a local cluster sends people into application logs, but the app "
            "is irrelevant until a controller exists. Report the capability as unavailable instead of "
            "installing one on a shared machine. The opposite trap is celebrating once an address appears: "
            "the provider's health check may target nodes that have no local ready endpoint, or a firewall "
            "may block the listener. Cloud load balancers also cost money and can outlive the lesson when "
            "cleanup is skipped, so record the provider resource's identity at creation and remove it "
            "through the owning Service, not by hand in a console."
        ),
        retrieval=(
            "In a cloud lab the external address answers on port 80, yet about half of the requests fail. "
            "Using network-study's two Pods and their readiness, write two hypotheses that could explain a "
            "50 percent failure rate and the single observation that would separate them."
        ),
    ),
    "k8s-053": dict(
        trace=(
            "The first line is decided by an HTTP proxy, not by Kubernetes itself: it reads the Host header "
            "and path, then finds a backend reference. The second line is a choice the controller makes, "
            "sending to Pod endpoints directly or through the ClusterIP. The last line belongs to the "
            "application, which can still answer 404 for a path the proxy matched."
        ),
        run=(
            f"[ingress.yaml]({FX}/ingress.yaml) routes host study.example.test, path / with pathType Prefix, "
            "to network-study port 80 under ingressClassName study-controller. The checker confirms that "
            "the backend Service and port exist in the fixture. It cannot know whether any controller "
            "claims study-controller on your cluster, and study.example.test is a reserved teaching name "
            "that never resolves in public DNS."
        ),
        reads=["get ingress network-study-ingress -o yaml"],
        read_note=(
            "Look at `spec.ingressClassName` and `status.loadBalancer.ingress`. An empty status usually means "
            "no controller has claimed the class. If one is present, its address plus a request carrying "
            "Host study.example.test to /version, expecting ds60-fixture-v1, is the acceptance evidence."
        ),
        hints=[
            "An Ingress is data. Which process reads that data and turns it into a listening proxy?",
            "One field selects the site, the other a route within it. Find both fields in ingress.yaml.",
            "After the rule matches, the backend is a Service reference. Draw both upstream modes from the diagram's second line.",
            "Prefix / matches every path. Does the app implement the path that was forwarded unchanged?",
            "An annotation is read by one controller's code. What does a different controller do with one it does not know?",
            "Which layer reads the URL? A Service never looks past the TCP connection.",
        ],
        mistakes=(
            "A 404 is the most misread result in this lesson. If it carries the controller's default page, "
            "no rule matched, so check the Host header and the class. If it comes from the app, the rule "
            "matched and the app has no handler for that path; the fixture returns 404 for / by design, so "
            "test /version instead. Another error is creating an Ingress and waiting for traffic on a "
            "cluster with no controller; the object will sit there unchanged and nothing will report a "
            "failure. Copying nginx annotations into a Traefik setup, or the reverse, silently does nothing "
            "either."
        ),
        retrieval=(
            "Add a second rule that sends study.example.test/api to network-study and keeps / for a future "
            "frontend Service. Write the new paths block, predict the response to GET /api/version without "
            "a rewrite, and name the observation that tells you whether the proxy or the app produced it."
        ),
    ),
    "k8s-054": dict(
        trace=(
            "Read the first two lines as an ownership chain. A GatewayClass names the controller, a Gateway "
            "owns listeners, and an HTTPRoute attaches by parentRef only if the listener's allowedRoutes "
            "permits its namespace. The third line warns that conditions such as Accepted and ResolvedRefs "
            "are reports from that controller. They localize a failure; a request through the listener is "
            "still the proof."
        ),
        run=(
            f"[gateway.yaml]({FX}/gateway.yaml) defines Gateway study-gateway with one HTTP listener named "
            "http on port 80 that accepts routes from the same namespace, plus HTTPRoute network-study-route "
            "attaching to sectionName http for host study.example.test with backend network-study:80. The "
            "checker verifies that parentRef and backend names line up. It cannot tell whether the Gateway "
            "API types or a study-controller class exist."
        ),
        reads=[
            "get gateway study-gateway -o yaml",
            "get httproute network-study-route -o yaml",
        ],
        read_note=(
            "On the Gateway, check `status.listeners[].attachedRoutes` and the listener conditions. On the "
            "route, check `status.parents[].conditions` for Accepted and ResolvedRefs and read each reason. If "
            "kubectl says the resource type does not exist, Gateway API is not installed, and that is the "
            "result to record."
        ),
        hints=[
            "Assign each resource to a role: platform provider, cluster operator, application team. What does each own?",
            "Follow the route's parentRef. If the target is missing or not programmed, what can the route attach to?",
            "Read allowedRoutes on the listener and parentRefs on the route. Both sides must agree before attachment.",
            "ResolvedRefs is about what the route points at. Check the backend's name, namespace, port and permission to reference it.",
            "A grant lives in the target's namespace and names who may refer in. Keep its from and to lists minimal.",
            "List what must be true before the first request: types installed, class accepted, listener programmed, route attached.",
        ],
        mistakes=(
            "When a route shows Accepted=False, the usual cause is a parentRef mismatch: a wrong Gateway "
            "name, a wrong sectionName, or a listener whose allowedRoutes excludes the route's namespace. "
            "Read the reason field before editing anything. ResolvedRefs=False points somewhere else, at a "
            "missing backend Service, a wrong port, or a cross-namespace reference without a ReferenceGrant. "
            "Do not fix that by widening the grant to every namespace or every kind. And do not assume "
            "Gateway API exists because Ingress does; its types are installed separately, and on a cluster "
            "without them kubectl reports an unknown resource type rather than an empty list. Record that "
            "error as the capability boundary."
        ),
        retrieval=(
            "Move network-study to namespace apps while the Gateway and route stay in study-example. Write "
            "the ReferenceGrant you need, the namespace it must live in, and the route condition and reason "
            "you expect before and after it exists."
        ),
    ),
    "k8s-055": dict(
        trace=(
            "The first line happens before any HTTP exists: the client sends the name it expects as SNI, "
            "receives a certificate and checks both the name and the chain. The second line is a new "
            "connection from the proxy to the app, plain HTTP or a second TLS session with its own identity. "
            "A browser padlock describes the first hop only."
        ),
        run=(
            f"None of the networking manifests uses TLS. [ingress.yaml]({FX}/ingress.yaml) and "
            f"[gateway.yaml]({FX}/gateway.yaml) listen on plain HTTP, so no certificate or private key is ever "
            "stored in the repository. This lesson works from certificate metadata in the worked examples, "
            "and the checker has nothing TLS-specific to validate. A live lab needs a deliberately prepared "
            "teaching certificate and scoped trust."
        ),
        reads=[
            "get secrets --field-selector type=kubernetes.io/tls -o custom-columns=NAME:.metadata.name,TYPE:.type,CREATED:.metadata.creationTimestamp",
        ],
        read_note=(
            "This read names TLS Secrets without printing their data, deliberately: never use -o yaml on a "
            "Secret for evidence. Certificate names and validity come from a handshake against the listener, "
            "recorded as subject, issuer, SAN list and expiry. A Forbidden answer is normal for a narrow lease."
        ),
        hints=[
            "A certificate lists the names it is valid for. Is an address match the same as a name match?",
            "Find the component holding the private key for the client-facing name. Decryption happens there.",
            "Record only what a handshake shows anyone: subject names, issuer, validity dates and the validation result.",
            "One failure happens before any HTTP exchange; the other needs a working HTTP exchange to exist at all.",
            "Decode a base64 string. Did you need a key to do it?",
            "Write two trust rows: what the client verifies about the proxy, and what the proxy verifies about the app.",
        ],
        mistakes=(
            "A certificate error and an HTTP 404 are often lumped together as the site being down. They come "
            "from different layers: a name mismatch fails the handshake before any request is sent, while a "
            "404 requires a successful handshake first. Another mistake is disabling verification with "
            "`curl -k` to get past a mismatch; that removes the very evidence you need. Never paste private "
            "keys, Secret YAML or key material into a worksheet, and remember base64 is an encoding anyone "
            "can reverse. Finally, do not assume the hop from proxy to Pod is encrypted because the "
            "client's hop is. Check the proxy's upstream configuration, which is a separate setting with "
            "its own trust anchor and its own failure messages in the proxy's log."
        ),
        retrieval=(
            "A client connects to study.example.test through a proxy that terminates TLS and opens a second "
            "TLS connection to the Pod using the name network-study.study-example.svc. Write both identities "
            "that must validate, which component checks each, and one failure that would appear only in the "
            "proxy's logs."
        ),
    ),
    "k8s-056": dict(
        trace=(
            "The first line rewrites addresses: a node or load balancer changes the destination to a Pod "
            "and, under the Cluster policy, may also replace the source with its own address. The second "
            "line is why replies still find the client: connection tracking remembers the rewrite. The third "
            "line is a separate channel, since forwarding headers are only claims until a trusted proxy sets them."
        ),
        run=(
            f"[service.yaml]({FX}/service.yaml) uses the default traffic policies, and topology.json puts "
            "the only ready endpoint, pod-a, on node-a. That placement is the key fact for "
            "externalTrafficPolicy Local: node-b has no ready local endpoint. The checker establishes "
            "placement and readiness, not translation. Observing a real source address needs a bounded "
            "request through an owned external entry point."
        ),
        reads=[
            "get service network-study -o custom-columns=NAME:.metadata.name,TYPE:.spec.type,EXTERNAL_POLICY:.spec.externalTrafficPolicy,INTERNAL_POLICY:.spec.internalTrafficPolicy",
            "get pods -l app=network-study -o wide",
        ],
        read_note=(
            "For a ClusterIP Service EXTERNAL_POLICY is blank because it applies only to NodePort and "
            "LoadBalancer types. INTERNAL_POLICY Cluster lets any node forward to any ready endpoint. Pair "
            "that with the Pods' NODE column to predict where a Local policy would leave a node with no backend."
        ),
        hints=[
            "Ask which field each rewrite changes: where the packet is going, or where it came from.",
            "If a node rewrote the source, whose address does the Pod's socket report as the peer?",
            "Write source IP, source port, destination IP, destination port and protocol on both sides of the translation.",
            "Under Local policy a node forwards only to Pods on itself. Which fixture node has none ready?",
            "Who wrote the header? What stops a client from sending its own X-Forwarded-For value?",
            "Name the caller, its path, the peer address the Pod reports and the header the trusted proxy set.",
        ],
        mistakes=(
            "Logging the socket peer and calling it the client address is the usual mistake; behind SNAT it "
            "is a node or proxy address. Switching to externalTrafficPolicy Local preserves the client "
            "address but drops traffic that arrives at nodes without a local ready endpoint, exactly what "
            "would happen on node-b in the fixture unless the load balancer's health check removes that "
            "node. The other trap is trusting X-Forwarded-For from anyone: a client can send any value "
            "unless the edge proxy overwrites it. Do not allowlist by header unless you know which proxy set "
            "it and that nothing else can reach the backend directly."
        ),
        retrieval=(
            "Switch a LoadBalancer version of network-study to Local and let the provider health-check both "
            "nodes. Predict which node is marked unhealthy, what source address pod-a then logs for an "
            "external request, and what changes once pod-b becomes ready."
        ),
    ),
    "k8s-057": dict(
        trace=(
            "There is no virtual address in this diagram. DNS for the headless Service returns the Pod "
            "addresses themselves, and the client picks one and speaks its own protocol to port 8080. The "
            "second line separates the stable name a StatefulSet gives each member from the process and UID "
            "behind it, which every replacement changes."
        ),
        run=(
            f"[headless.yaml]({FX}/headless.yaml) defines network-study-headless with clusterIP None, the "
            f"same selector and a named port. The [fixture README]({FX}/README.md) explains that clients "
            "connect to 8080 directly because port 80 is never translated. The checker confirms the headless "
            "Service still selects the fixture Pods. It cannot show DNS records, and the fixture uses a "
            "Deployment, so stable member names stay worked-example material."
        ),
        reads=[
            "get service network-study-headless -o custom-columns=NAME:.metadata.name,CLUSTER_IP:.spec.clusterIP,PUBLISH_NOT_READY:.spec.publishNotReadyAddresses",
            "get endpointslices -l kubernetes.io/service-name=network-study-headless -o yaml",
        ],
        read_note=(
            "CLUSTER_IP should read None. The headless slice lists the Pod addresses that A records will "
            "return, with port 8080. Because publishNotReadyAddresses is unset, DNS normally returns only "
            "ready members, so pod-b should be missing until its probe passes."
        ),
        hints=[
            "Without a ClusterIP, what is left for a DNS answer to contain?",
            "Replace one StatefulSet member in your head. Which comes back the same, the name or the UID?",
            "Order the steps: resolve peers, confirm which peer is which, then connect. Where does the application protocol begin?",
            "When DNS returns several addresses, who chooses the destination? Is there a proxy in between?",
            "Some members must find each other before they can serve. Who else would see those unready addresses?",
            "After replacement, check the logical name, the new UID, the volume claim and a data read from the application.",
        ],
        mistakes=(
            "Treating a headless Service like a ClusterIP leads to clients that resolve once, cache one "
            "address and keep calling a Pod that no longer exists. The client owns selection, retry and "
            "re-resolution. Another mistake is connecting to port 80 because the Service says 80; there is "
            "no proxy to translate, so connect to the listener port. Assuming a stable name means unchanged "
            "data is risky too: the name returns after replacement, but only the persistent volume carries "
            "state, and only an application read proves it. Turning on publishNotReadyAddresses for ordinary "
            "clients sends them to members that are still starting."
        ),
        retrieval=(
            "A three-member StatefulSet behind network-study-headless loses member 1. Write what DNS returns "
            "during the replacement, which fields of the new member match the old one, and the single "
            "application-level check that proves it rejoined with the right data."
        ),
    ),
    "k8s-058": dict(
        trace=(
            "Read the first line from the destination's side: once a policy selects network-study Pods for "
            "ingress, everything is denied except what some rule allows. The second line is one rule, where "
            "a peer and a port must both match. The third line says rules from every applicable policy are "
            "unioned, and none of it happens unless the plugin enforces policy."
        ),
        run=(
            f"[network-policy.yaml]({FX}/network-policy.yaml) allows ingress to app=network-study on TCP 8080 "
            "only from one peer that combines namespaceSelector study-role=client with podSelector "
            "role=tester. topology.json supplies the client cases, and the checker evaluates allowed, "
            "wrong-namespace and wrong-pod against that AND peer. A pass is selector logic; real allow and "
            "deny need an enforcing plugin and two owned callers."
        ),
        reads=["get networkpolicy network-study-allow-client -o yaml"],
        read_note=(
            "Check that namespaceSelector and podSelector sit in the same `from` element, which makes them "
            "AND, and that the port is 8080, the Pod port, not the Service port 80. Then list other policies "
            "selecting the same Pods, because their rules add to this one."
        ),
        hints=[
            "Both selectors sit in one peer. Does the wrong-namespace caller satisfy both at once?",
            "Rewrite the peer as two list items, a dash before each selector. Is the result narrower or broader?",
            "One row per client case in topology.json: namespace label, Pod label, port and your prediction.",
            "First ask whether the plugin enforces policy at all, then list every policy that selects the destination.",
            "Policies never subtract. What does a second policy allowing another peer do to the first one's set?",
            "One allowed flow is not enough. Name the denied flow that must fail and the plugin that enforces it.",
        ],
        mistakes=(
            "One indentation mistake changes everything: a dash before podSelector turns an AND peer into "
            "two OR peers and quietly admits every Pod in client namespaces plus testers in the policy's own "
            "namespace. Read the YAML structure, not just the labels. Another mistake is matching the Service "
            "port 80 in policy rules; policy sees the Pod port 8080 after translation. Seeing traffic flow "
            "despite a policy usually means the plugin does not enforce NetworkPolicy or another policy "
            "allows it. Never delete policies to diagnose; read all of them and build the union by hand."
        ),
        retrieval=(
            "Add a monitoring namespace labeled study-role=monitor whose scraper must reach port 8080 on "
            "network-study Pods. Write the extra peer, decide whether it belongs in this policy or a new "
            "one, and predict the result for the wrong-pod client case afterward."
        ),
    ),
    "k8s-059": dict(
        trace=(
            "The first line is a dependency people forget: before the app can call anything by name, it "
            "sends a DNS query, and that query is itself egress. The second line is the real call. The third "
            "line is the rule that follows: an egress policy must allow every leg, including DNS on UDP and "
            "TCP 53, not just the final destination."
        ),
        run=(
            f"[network-policy.yaml]({FX}/network-policy.yaml) covers ingress only, so this lesson's "
            "default-deny egress fragment comes from the worked examples. The egress-blocked case in "
            f"[topology.json]({FX}/topology.json) is the bridge: the caller's labels match the destination's "
            "ingress rule, yet source_egress_allowed is false, and the checker records that flow as denied. "
            "That models both ends of a connection, not an enforcing plugin."
        ),
        reads=[
            "get networkpolicies -o custom-columns=NAME:.metadata.name,TYPES:.spec.policyTypes,SELECTOR:.spec.podSelector.matchLabels",
        ],
        read_note=(
            "List every policy in the namespace and look for one whose TYPES include Egress and whose "
            "selector covers your client Pod; an empty selector covers all Pods. If none mention Egress, "
            "policy does not restrict the client's outbound traffic, and a failure lies elsewhere."
        ),
        hints=[
            "An empty egress list permits nothing. What does that mean when a selected Pod looks up a name?",
            "Before the real call, the app queries a resolver. Find its Service and both protocols it uses.",
            "Start from deny-all, add one rule per named dependency including DNS, and check nothing else slipped in.",
            "If the address works and the name does not, the policy may allow the destination but not the resolver.",
            "An ipBlock matches addresses. What happens when the provider moves the hostname to another address?",
            "After NAT the destination may see another source. Record one allowed and one denied case under the named plugin.",
        ],
        mistakes=(
            "The most frequent egress mistake is forgetting DNS: a default-deny egress policy plus an allow "
            "rule for the database still breaks every request that uses a hostname. Allow the cluster DNS "
            "Pods on UDP and TCP 53. Another mistake is writing an ipBlock for a SaaS hostname; providers "
            "change addresses and share them across customers, so the rule is both brittle and broad. When a "
            "caller fails despite matching the destination's ingress rule, check the caller's own egress "
            "before editing the destination, exactly as the egress-blocked case shows."
        ),
        retrieval=(
            "The network-study app must call one external API at a fixed /32 on port 443 and nothing else. "
            "Write the egress policy including DNS, then predict what happens to the egress-blocked client "
            "case if your policy is applied in the caller's namespace by mistake."
        ),
    ),
    "k8s-060": dict(
        trace=(
            "The first line is a client decision: DNS may return A and AAAA records and the client picks a "
            "family, often IPv6 first. The next two lines are independent paths, each with its own Service "
            "address, endpoints and routes. The last line is the point of the lesson: one family passing "
            "tells you nothing about the other, including policy coverage."
        ),
        run=(
            f"[dual-stack-service.yaml]({FX}/dual-stack-service.yaml) declares network-study-dual with "
            "RequireDualStack and families IPv4 then IPv6, but the ordinary fixture app binds IPv4 only. The "
            f"separate [dual-stack fixture]({FX}/dual-stack/README.md) supplies a server bound to :: with "
            "IPV6_V6ONLY set to zero and a family-specific client. The checker validates API intent; family "
            "routing needs an owned dual-stack cluster."
        ),
        reads=[
            "get service network-study-dual -o custom-columns=NAME:.metadata.name,POLICY:.spec.ipFamilyPolicy,FAMILIES:.spec.ipFamilies,CLUSTER_IPS:.spec.clusterIPs",
        ],
        read_note=(
            "On a single-stack cluster the API server rejects RequireDualStack, so the object may not exist; "
            "record that rejection as your evidence for Exercise 1. On a dual-stack cluster CLUSTER_IPS shows "
            "two addresses, and each family still needs its own request result."
        ),
        hints=[
            "What does RequireDualStack demand of the cluster, and what can the API server do if it cannot comply?",
            "Each record type carries one family. Which one holds the longer address written with colons?",
            "Make two columns, one per family, and fill DNS, Service, endpoints, policy and response separately.",
            "IPv4 works, so the app runs. Check the IPv6 leg: route, endpoint address, listener family and policy.",
            "An IPv6 address already contains colons. How would a URL parser find the port without a delimiter?",
            "Read every ipBlock in your policies. Does each one have a twin for the other family?",
        ],
        mistakes=(
            "The supplied network-study app binds IPv4 only, so creating network-study-dual and seeing an "
            "IPv6 ClusterIP is not success; IPv6 requests reach no listener. Use the separate dual-stack "
            "fixture when you need a real IPv6 response. Another mistake is testing one family and filling "
            "both rows, when a client that prefers IPv6 may be the only one failing. Policies are often "
            "written with IPv4 ipBlocks only, leaving IPv6 open or blocked by accident. Finally, typing an "
            "IPv6 address into a URL without brackets makes the last group look like a port."
        ),
        retrieval=(
            "Change network-study-dual to PreferDualStack and apply it on a single-stack IPv4 cluster. "
            "Predict the families and ClusterIPs the API assigns, then explain why the IPv6 row of your "
            "acceptance table must say not run rather than passed."
        ),
    ),
    "k8s-061": dict(
        trace=(
            "The first line happens at scheduling: where Pods land decides how many endpoints each zone has. "
            "The second line happens for each connection: the caller's zone and the routing preference narrow "
            "the eligible set. The third line is the consequence. If zone-b has one endpoint and half the "
            "callers, that endpoint carries all their load unless routing falls back."
        ),
        run=(
            f"[topology.json]({FX}/topology.json) puts node-a in zone-a and node-b in zone-b with one Pod "
            "each, but only pod-a is ready. The checker confirms node and zone references. The topology is "
            "lopsided on purpose: callers in zone-b have no ready local endpoint. Whether the data plane "
            "honors hints or trafficDistribution is a release and implementation fact, readable only in a lab."
        ),
        reads=[
            "get endpointslices -l kubernetes.io/service-name=network-study -o custom-columns=SLICE:.metadata.name,ZONES:.endpoints[*].zone,NODES:.endpoints[*].nodeName,HINTS:.endpoints[*].hints.forZones[*].name",
        ],
        read_note=(
            "ZONES and NODES show where each endpoint lives. HINTS is filled only when topology-aware routing "
            "or trafficDistribution requests it and the controller judges capacity sufficient. Empty hints "
            "mean callers in any zone may select any ready endpoint."
        ),
        hints=[
            "Divide each zone's client demand by that zone's endpoint count. Which endpoint ends up busier?",
            "One decision is made when a Pod is scheduled, the other each time a connection opens. Which component makes each?",
            "Remove one zone's endpoints and ask whether the preference allows falling back to the other zone.",
            "Compare endpoints per zone with requests per zone, not just total replicas.",
            "Field names and accepted values changed between releases. What does the pinned version's API reference accept?",
            "Write the latency or cost gain next to what happens when a zone loses its only endpoint.",
        ],
        mistakes=(
            "Adding replicas without checking their zones is the usual locality mistake: six Pods all in "
            "zone-a do nothing for zone-b callers under a same-zone preference. Read endpoint zones, not just "
            "counts. Another mistake is assuming hints are active because the field was set; the controller "
            "drops hints when capacity is too uneven, and the data plane must support them. Do not copy "
            "trafficDistribution values from a newer release onto an older cluster. Decide in advance "
            "whether falling back to a remote zone during an outage is acceptable, and write that down "
            "before an incident forces the choice."
        ),
        retrieval=(
            "With pod-a ready in zone-a and pod-b unready in zone-b, predict where a zone-b caller's request "
            "goes under PreferSameZone, then repeat after pod-b becomes ready. Name the endpoint field that "
            "would confirm each prediction."
        ),
    ),
    "k8s-062": dict(
        trace=(
            "Read the first line as gates in order: a startup probe must pass before the others count, then "
            "readiness admits the Pod to new traffic. The second line runs in reverse for the old Pod: it "
            "leaves the endpoint set, drains in-flight work and exits. The third line warns that endpoint "
            "removal reaches every node only after a delay."
        ),
        run=(
            f"[deployment.yaml]({FX}/deployment.yaml) sets readiness on /ready every 2 seconds with "
            "failureThreshold 2 and has no startup or liveness probe, so a failing /ready removes a Pod from "
            "traffic within roughly 4 seconds without restarting it. The checker validates that the probe's "
            "port name resolves. Rollout timing, preStop delays and in-flight connections need a stateful "
            "host lab with a real revision change."
        ),
        reads=[
            "get deployment network-study -o custom-columns=NAME:.metadata.name,GENERATION:.metadata.generation,OBSERVED:.status.observedGeneration,UPDATED:.status.updatedReplicas,READY:.status.readyReplicas,AVAILABLE:.status.availableReplicas",
        ],
        read_note=(
            "GENERATION ahead of OBSERVED means the controller has not caught up. UPDATED below the replica "
            "count while READY stays full is the masked rollout from worked example 2: old Pods serve while "
            "the new revision is not ready. Record both numbers before deciding a rollout worked."
        ),
        hints=[
            "Readiness and liveness have different consequences. Which restarts the container and which only changes traffic?",
            "Measure how long initialization actually takes, then set the window from that measurement plus a margin.",
            "Order the shutdown: stop accepting, finish running work, exit. Place the grace period and preStop on that line.",
            "A 200 proves some Pod answered. Which revision does that Pod belong to?",
            "If the database is down, what does restarting the web container fix?",
            "Name the evidence for the new revision, the responses during the switch and the fate of the old ReplicaSet.",
        ],
        mistakes=(
            "Using liveness for dependency checks is the most damaging probe mistake: a database outage then "
            "restarts every web Pod in a loop, adding load and fixing nothing. Keep liveness for a wedged "
            "process. Another mistake is declaring a rollout fine because requests still return 200; old "
            "Pods can carry all traffic while the new revision fails readiness, so read updatedReplicas and "
            "the ReplicaSet revision. On shutdown, a process that exits the instant it receives SIGTERM drops "
            "in-flight requests, because endpoint removal reaches nodes later; a short preStop pause or a "
            "graceful drain covers that gap."
        ),
        retrieval=(
            "Add a startupProbe to the network-study fixture for an app that needs up to 45 seconds to "
            "initialize. Choose periodSeconds and failureThreshold, explain why readiness stays unchanged, "
            "and predict what the Service's endpoints show during those 45 seconds."
        ),
    ),
    "k8s-063": dict(
        trace=(
            "The first line follows one request through three components and needs a shared request ID to "
            "connect them. The second line ties events to a resource UID and generation, so lifecycle "
            "changes match the right object. The third line is the discipline: choose a time window first, "
            "then compare signals inside it instead of reading everything."
        ),
        run=(
            f"The fixture app's only outputs are its /version and /ready responses described in the "
            f"[fixture README]({FX}/README.md), and topology.json carries no time series, so this lesson's "
            "signals are the synthetic packets in the worked examples. The checker has nothing to evaluate "
            "about logs or metrics. Events and logs for network-study are readable in an owned lab; metrics "
            "and traces need a separately installed pipeline."
        ),
        reads=[
            "get events --field-selector involvedObject.kind=Pod --sort-by=.lastTimestamp",
            "logs deployment/network-study --since=10m --tail=50",
        ],
        read_note=(
            "Events expire after about an hour by default, so read them early and keep each involved "
            "object's UID. The log read is bounded by time and line count. Neither shows request latency; "
            "that needs metrics or traces captured in the same window."
        ),
        hints=[
            "Ask what each signal is for: a lifecycle change, a message from code, a number over time or one request's path.",
            "Find the first and last timestamps that matter, then add margin for clock skew and delayed events.",
            "Carry one request ID through every record and add the resource revision so you know which code answered.",
            "Latency is a sum. Split it into lookup, connect, queue and handler time before naming a suspect.",
            "Every distinct label value creates a new series. What happens if the value is a user ID?",
            "Keep what helps correlation, drop what identifies people or carries secrets, and decide how long records live.",
        ],
        mistakes=(
            "Reading events too late is common; default retention is short, and the event explaining a crash "
            "loop may already be gone. Another mistake is correlating by Pod name alone, which silently joins "
            "a replacement Pod with a different UID. When latency rises, people jump to CPU; break the "
            "request into DNS, connect, queue and handler time first. Do not put request IDs or user IDs into "
            "metric labels, and never log tokens or private payloads to make debugging easier, since logs "
            "are retained and copied far more widely than the request itself."
        ),
        retrieval=(
            "A latency spike lasted three minutes yesterday on network-study. Write the time window you would "
            "use, which signal you would read first and why, and the correlation field that would link a slow "
            "trace to the Pod UID and revision that served it."
        ),
    ),
    "k8s-064": dict(
        trace=(
            "The first line is a ladder: each rung must work before the next can even be tested, so localize "
            "by finding the highest rung that succeeds. The second line runs in parallel and explains ladder "
            "failures; an empty EndpointSlice, for example, explains a failed connect. Climb with bounded "
            "probes, one hypothesis at a time."
        ),
        run=(
            f"This lesson uses the fixture as one system: [service.yaml]({FX}/service.yaml) and "
            "deployment.yaml for selector and targetPort, topology.json for readiness, and the README's exact "
            "response, /version returning ds60-fixture-v1. The checker's pass is a known-good baseline for "
            "the configuration rungs. Rungs that need traffic, such as connect and response body, need an "
            "owned caller."
        ),
        reads=[
            "get service network-study -o custom-columns=SELECTOR:.spec.selector,TARGET_PORT:.spec.ports[*].targetPort",
            "get endpointslices -l kubernetes.io/service-name=network-study -o custom-columns=ADDRESSES:.endpoints[*].addresses[0],READY:.endpoints[*].conditions.ready,PORT:.ports[*].port",
        ],
        read_note=(
            "These two reads cover the control-evidence line: selector, target port, endpoint addresses and "
            "readiness. If the selector matches and a ready endpoint carries port 8080, you can eliminate the "
            "selector and targetPort hypotheses in Exercise 3 before asking about data-plane state."
        ),
        hints=[
            "Each rung needs the one below it. Start from the name and finish at the body.",
            "A refusal means something answered with a reset; a timeout means nothing answered. Which narrows the location more?",
            "One row per hypothesis, each with the read that would prove it wrong. Keep the reads separate.",
            "Internal requests work, so Service, endpoints and app are fine. Which layers does the external path add?",
            "Which revision, namespace and caller produced the old receipt, and has any of them changed?",
            "Break one thing on purpose, preserve the failure, repair only that, then recheck the original invariant.",
        ],
        mistakes=(
            "The biggest troubleshooting mistake is changing several things at once. Restarting Pods, editing "
            "the Service and widening a policy together leaves no way to know what fixed it, or what new "
            "problem appeared. Change one thing per hypothesis. Another is skipping rungs: if DNS fails, no "
            "amount of reading app logs helps. Watch for stale proof as well; a success from yesterday's "
            "revision or another namespace says nothing about today's path. Write each hypothesis so a single "
            "read can falsify it before any repair."
        ),
        retrieval=(
            "A request to http://network-study/version from namespace tools times out, while the same request "
            "from study-example works. Climb the ladder for the failing caller, write the first two "
            "hypotheses in falsifiable form, and name the read for each."
        ),
    ),
    "k8s-065": dict(
        trace=(
            "The first line adds two traffic components to the path, one beside each app, and the hop between "
            "them is mutually authenticated TLS. The second line is easy to forget: the mesh control plane "
            "hands out identities and policy, but the underlying network still carries every packet. The "
            "third line multiplies each boundary when a second cluster joins."
        ),
        run=(
            "No mesh appears in the fixture and no lesson installs one. The fixture's single Service and two "
            f"Pods in [service.yaml]({FX}/service.yaml) and deployment.yaml are the plain baseline: one DNS "
            "name, one ClusterIP hop, no sidecars. The checker validates that baseline only. A mesh lab needs "
            "an operator-installed mesh with its own version, identity authority and owned namespace enrollment."
        ),
        reads=[
            "get pods -l app=network-study -o custom-columns=POD:.metadata.name,CONTAINERS:.spec.containers[*].name,INIT:.spec.initContainers[*].name",
        ],
        read_note=(
            "Without a mesh, CONTAINERS shows only app. A sidecar-based mesh injects a proxy container or init "
            "container here, the first sign a namespace is enrolled. Ambient-style meshes inject nothing per "
            "Pod, so an absence alone does not prove there is no mesh."
        ),
        hints=[
            "One part decides policy and certificates; the other handles every byte. Which part sits beside the app?",
            "mTLS tells the server who is calling. Does it say whether that caller may perform this specific action?",
            "Name each hop: discovery of the remote service, the path between clusters, the trust check and the app call.",
            "Count the layers that retry: client, sidecar, gateway. Multiply their attempts.",
            "If both clusters use 10.244.0.0/16, what does a route to 10.244.1.7 mean?",
            "List the capabilities you need, then check whether something simpler already provides them.",
        ],
        mistakes=(
            "Adopting a mesh only for encryption often adds more operational risk than it removes; "
            "NetworkPolicy plus application TLS may be enough. When a call fails under strict mTLS, people "
            "disable strict mode cluster-wide; read the peer identity and the authorization policy instead. "
            "Retry settings at the client, the sidecar and an edge gateway multiply, so three attempts at each "
            "of three layers can reach the backend 27 times and duplicate unsafe writes. Joining clusters "
            "whose Pod CIDRs overlap breaks direct routing unless the mesh deliberately uses gateways."
        ),
        retrieval=(
            "A team wants a mesh only to get mTLS between network-study and one caller. Write the capability "
            "list, one simpler alternative, the evidence that would justify the mesh anyway, and the retry "
            "budget you would set at each layer."
        ),
    ),
    "k8s-066": dict(
        trace=(
            "The first line is the full request ladder from client to response, and every arrow needs a named "
            "component and a piece of evidence. The second line runs beside it: policy decides which arrows "
            "may exist, and observability ties a request to resource identities. The third line is the "
            "incident loop the capstone rehearses, ending with owned cleanup."
        ),
        run=(
            "The capstone uses every networking fixture together: deployment and service for the internal hop, "
            "ingress or gateway for the edge, network-policy for isolation and topology.json for the client "
            f"cases. Run the checker from the [fixture README]({FX}/README.md) first as the baseline. Then mark "
            "each acceptance row as passed with live evidence, synthetic only, or not run because the "
            "capability is missing."
        ),
        reads=[
            "get deployment,service,networkpolicy -l course-fixture=deep-networking -o custom-columns=KIND:.kind,NAME:.metadata.name,UID:.metadata.uid,GENERATION:.metadata.generation",
        ],
        read_note=(
            "This read builds the ownership ledger: kind, name, UID and generation for each retained fixture "
            "object. Cleanup later compares against these UIDs, never just names or labels. Add Ingress or "
            "Gateway rows only if those APIs exist in your lease."
        ),
        hints=[
            "Start at the client and stop at the response body. Each arrow needs a caller, a destination and an owner.",
            "For each row of the fixture README's capability table, ask whether this lab has it. Missing ones become explicit rows.",
            "Check that diagram, manifests, ledger and checks name the same objects, ports and limits.",
            "Compare the Service's targetPort with the container's named port. The first mismatch you find is the fault.",
            "Use one allowed and one denied client case from topology.json, both under a plugin known to enforce policy.",
            "Teach from the packet: which results are live, which are synthetic and which platforms you never tested.",
        ],
        mistakes=(
            "Capstones fail on evidence more often than on YAML. Marking a row passed because the object was "
            "created confuses API acceptance with traffic. Another mistake is repairing the target-port fault "
            "while also restarting Pods and widening the policy; the fresh request then no longer proves which "
            "change fixed it. Test isolation with a denied flow as well as an allowed one. During cleanup, "
            "delete by recorded UID through the reviewed procedure, never by namespace or by a broad label "
            "such as course-fixture."
        ),
        retrieval=(
            "Teach the capstone to a peer in five minutes. Name the one fault you injected, the rung where "
            "evidence first broke, the repair and the fresh request proving it, then list two platforms or "
            "capabilities your packet does not cover and why."
        ),
    ),
}

CHECKLISTS = {
    "k8s-047": [
        "`spec.selector` beside the labels of each candidate Pod, so a one-character typo in app=network-study is visible.",
        "`port` 80, `targetPort` http and the container port named http, which must resolve to listener 8080.",
        "Each EndpointSlice address with its `conditions.ready` value; an address marked not ready gets no new connections.",
        "The caller, the virtual destination 10.96.0.20:80 and the chosen Pod address for one fresh TCP connection.",
    ],
    "k8s-051": [
        "All three numbers in one row: Service port 80, targetPort 8080 and nodePort 30080, each with its role.",
        "The node address you actually dialed, and whether your laptop has a route or a kind port mapping to it.",
        "The cluster's configured NodePort range, if you can read it, instead of assuming the 30000 to 32767 default.",
        "Whether the same request through ClusterIP port 80 succeeds from inside the cluster, which separates node reachability from backend health.",
    ],
    "k8s-052": [
        "The Service `status.loadBalancer.ingress` field, empty or filled, and the time you read it.",
        "The name of the load-balancer controller that should act, or a plain statement that none is installed.",
        "For an assigned address: the listener port, the provider health check target and its reported backend state.",
        "One real request result against the external address, kept separate from any Pod readiness reading.",
    ],
    "k8s-054": [
        "The HTTPRoute `parentRefs` name, namespace and sectionName, beside the Gateway listener they claim to attach to.",
        "The listener's `allowedRoutes.namespaces` setting and whether the route's namespace falls inside it.",
        "Each route condition with its status and reason, such as Accepted=False with reason NotAllowedByListeners.",
        "For a cross-namespace backendRef, the ReferenceGrant's `from` kind and namespace and its `to` kind.",
    ],
    "k8s-055": [
        "The hostname the client sent as SNI and the names in the certificate's subjectAltName list.",
        "The certificate's issuer and its notBefore and notAfter dates, read as metadata with no key bytes.",
        "Which component decrypts the client connection, and whether its upstream hop is plain HTTP or a second TLS session.",
        "The layer of each failure: handshake errors arrive before any status line, HTTP codes such as 404 only after it.",
    ],
    "k8s-059": [
        "Every leg of one named request: the resolver address on UDP and TCP 53, then the dependency address and port.",
        "Each egress policy that selects the Pod, since allowances from several policies add together.",
        "Paired results for the same destination by hostname and by direct IP, which separate DNS from transport.",
        "The source address the destination observed after NAT, if an external allow list depends on it.",
    ],
    "k8s-060": [
        "The Service `ipFamilies` and `ipFamilyPolicy`, and whether a RequireDualStack request was accepted or rejected.",
        "Separate A and AAAA answers for the Service name; one row never stands in for both families.",
        "The app's listener bind address: 0.0.0.0 alone serves IPv4, while :: may also serve IPv6.",
        "IPv6 test URLs written with brackets, such as `http://[2001:db8::10]:8080/`, so the port parses correctly.",
    ],
    "k8s-062": [
        "Each probe's endpoint, periodSeconds and failureThreshold, plus its consequence: a restart or removal from endpoints.",
        "The startup allowance as failureThreshold times periodSeconds, compared with the measured initialization time.",
        "`terminationGracePeriodSeconds` beside any preStop delay and the app's own drain deadline; all three must fit.",
        "updatedReplicas, readyReplicas and the ReplicaSet revision that served each successful response.",
    ],
    "k8s-063": [
        "The incident window as start and end timestamps, chosen before you open any signal.",
        "The Pod UID and `metadata.generation` tied to each event, not the Pod name alone.",
        "One request ID followed through the proxy, the app and the data operation, with each hop's duration.",
        "Every proposed metric label with its bounded set of values; request IDs belong in logs or traces.",
    ],
    "k8s-064": [
        "The highest ladder rung that succeeded and the first that failed, from DNS answer to expected body.",
        "Refused versus timed out for a failing connect, since refusal narrows the search and a timeout does not.",
        "The parallel control reads: selector match, EndpointSlice addresses and readiness for the current revision.",
        "One hypothesis per change, with the read that could disprove it and the result after the change.",
    ],
    "k8s-065": [
        "The peer identity presented on the failing hop and the authorization rule that admitted or rejected it.",
        "Retry counts and timeouts at the client, the sidecar and the gateway, multiplied into a worst case.",
        "Pod and Service CIDRs of both clusters, checked for overlap before any cross-cluster route is trusted.",
        "The capability that justifies the mesh, and the simpler alternative you rejected with your reason.",
    ],
}

for _key, _items in CHECKLISTS.items():
    TEACHING[_key]["checklist"] = _items
