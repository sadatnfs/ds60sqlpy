# k8s-053: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

Ingress describes HTTP and HTTPS routing intent to Services. It requires an Ingress controller that interprets the resource and implements a proxy path. Creating an Ingress object without a controller does not create a web server or make a hostname reachable.

A host rule matches the HTTP host name, while a path rule matches the URL path according to its pathType. Exact, Prefix and implementation-specific rules are not interchangeable. Prefix matching is based on path elements, not an arbitrary raw string startsWith rule. Rewriting paths is controller-specific behavior rather than a universal core Ingress feature.

The controller itself needs an exposure path, such as a load balancer or a deliberately mapped local port. DNS must point the chosen hostname at that entrypoint. An HTTP route can be configured correctly while public DNS or TLS is still wrong. Diagnose the request as a chain.

Use networking.k8s.io/v1 and specify ingressClassName when the prepared environment requires it. Each backend references a Service and a port in the API, not a Pod directly. That reference does not require every controller to send packets through the Service ClusterIP. A controller can derive eligible Pod endpoints and proxy to them directly, or use the ClusterIP according to its implementation and configuration. Traefik’s documented nativeLB option is one concrete example of these alternatives. The fixture uses a reserved example hostname and is manual-only.

Ingress remains a supported API, while Gateway API offers a more expressive role-oriented model. Neither choice installs its own controller. A learner should understand both the API contract and the selected implementation before relying on annotations.

## Exercise 1: Predict behavior with no Ingress controller.

API acceptance is not implementation. Inspect controller availability before debugging backend application code.

**Expected:** The object can exist without any serving proxy.

**Solution reasoning**

- **Approach:** Check whether any Ingress controller watches the Ingress class used by the object.
- **Why it is correct:** An Ingress is only configuration; without a controller nothing programs a proxy to serve it.
- **Plausible wrong approach:** Assuming a successful apply means routing works confuses object storage with a running proxy.
- **How to verify:** The prediction says the object can exist with no serving proxy.

## Exercise 2: Distinguish host and path matching.

Both participate in routing. A request to the right IP with a different Host header can select another rule.

**Expected:** Host identifies the requested site; path identifies a route within it.

**Solution reasoning**

- **Approach:** Assign host matching to the requested site name and path matching to the route within that site.
- **Why it is correct:** The controller selects a rule by host first and then by path, so each field narrows a different part of the request.
- **Plausible wrong approach:** Putting the site name into a path rule makes it match only a literal path segment.
- **How to verify:** Host maps to the site and path maps to a route within it.

## Exercise 3: Draw the full Ingress-to-Pod request path.

The API references the Service, while the controller may proxy directly to derived Pod endpoints or use ClusterIP routing. Name the actual implementation path.

**Expected:** The Service backend reference and the actual configured upstream path are distinguished.

**Solution reasoning**

- **Approach:** Draw the client, controller proxy, backend Service reference and the upstream the controller actually configured.
- **Why it is correct:** Many controllers resolve the Service to Pod endpoints, so the configured upstream can differ from the named Service.
- **Plausible wrong approach:** Assuming traffic always passes through the ClusterIP can misplace a fault in a controller that targets Pods.
- **How to verify:** The drawing separates the Service backend reference from the configured upstream.

## Exercise 4: Diagnose an app 404 after a matched prefix route.

Inspect rewrite behavior and actual request path. A proxy match only chooses a backend.

**Expected:** The forwarded path may not exist in the application.

**Solution reasoning**

- **Approach:** Compare the matched route with the path the application received and the routes it serves.
- **Why it is correct:** A Prefix match forwards the full original path unless a rewrite is configured, so the app may not serve it.
- **Plausible wrong approach:** Blaming the Ingress for a 404 that the application returned skips reading which component answered.
- **How to verify:** The diagnosis shows the forwarded path does not exist in the application.

## Exercise 5: Explain why controller annotations are not universal.

Copying annotations from another controller can be ignored or behave differently. Use the prepared implementation documentation.

**Expected:** They belong to a particular implementation contract.

**Solution reasoning**

- **Approach:** Tie each annotation to the controller that reads it.
- **Why it is correct:** Annotations are free-form metadata, and each controller defines its own keys and meanings.
- **Plausible wrong approach:** Copying an annotation from another controller's docs adds a key that the installed controller ignores.
- **How to verify:** The answer says annotations belong to a specific implementation contract.

## Exercise 6: Compare Ingress and a Layer 4 Service.

Choose the mechanism according to the protocol and routing requirement rather than treating both as generic public exposure switches.

**Expected:** Ingress interprets HTTP routing; the Service handles transport endpoint selection.

**Solution reasoning**

- **Approach:** Contrast HTTP routing by host and path with Service connection selection by IP and port.
- **Why it is correct:** The Ingress proxy reads HTTP requests, while the Service picks a backend when a connection opens.
- **Plausible wrong approach:** Expecting a Service to route by path asks Layer 4 to read data it never inspects.
- **How to verify:** Ingress handles HTTP routing, and the Service handles transport endpoint selection.
