## Starting point and result

A resource-oriented API exposes identifiable things and consistent ways to inspect or change them. This chapter creates tasks, returns a link to each representation and demonstrates that repeating an ordinary POST can create another resource. It is a small design investigation, not a claim to implement every constraint of the REST architectural style.

## Mechanism: identity, representation and transitions

The collection path `/tasks` accepts a bounded title. The server allocates a new ID using a monotonic counter within this disposable application fixture. The response includes the representation and a self link generated from the registered read route. A client can follow that link to retrieve the identified task.

A representation is the data the API chooses to expose about a resource. It need not mirror every internal database field. Here the public fields are ID and title. The input contract accepts only title, so a caller cannot assign an arbitrary owner field through this endpoint. Later authorization chapters derive ownership from trusted authentication state.

REST includes broader constraints such as client/server separation, stateless interactions, cacheability, a uniform interface and layering. JSON plus a set of routes does not automatically satisfy all of them. A practical application should state its choices and tradeoffs clearly rather than treating an architectural label as proof of quality.

## Worked case: create and retrieve a resource

The client posts a title and receives status 201, an ID and a self link. It follows the link and obtains the expected representation. The assertions connect creation to retrieval, which is stronger than testing each handler's return value in isolation.

The route supplies the resource identity on each read request. The server does not require a hidden variable such as “the task this client most recently opened” to decide which task is requested. That makes requests easier to reason about, retry, log and route between workers, subject to the chosen authentication and persistence design.

The counter is a finite fixture mechanism. A deployed application needs an identity strategy appropriate to its database and concurrency model. A process-local counter does not coordinate several workers or survive a restart.

## Worked case: repeat POST and reject unintended fields

The client sends the same POST body twice. Two different IDs are created. That behavior is allowed by this collection-creation contract, so the program explicitly records it. A client retry after an uncertain response could therefore create a duplicate task unless the application provides an additional idempotency mechanism.

A request containing an extra owner field returns 422. An unknown task ID returns 404. These refusals address different concerns: one violates the write schema, while the other identifies a resource the fixture does not have. Neither result should be silently converted into a successful empty object.

Later chapters add idempotency keys, version preconditions, transactions and authorization. They build on the same discipline: define the intended state transition and what a client can observe when it succeeds, repeats, conflicts or fails.

## Failure diagnosis

Endpoints that require undocumented call ordering often hide conversational state. APIs that expose database internals can make future migrations unnecessarily difficult. Inconsistent error bodies can force clients to guess which parser to use. Start from concrete client operations and explicit representations, then test their relationships rather than optimizing route syntax first.

A successful local fixture also says nothing about concurrency, storage durability or the behavior of a reverse proxy. The owned workshops add those surfaces with separate acceptance. Keep the confidence supported by each test layer explicit.

## Interview discussion

**Is POST always non-idempotent?** HTTP does not give every POST operation an idempotence guarantee. An application can define a suitable idempotency-key contract, but clients must not assume one exists without documentation.

**Does stateless interaction mean the server stores no data?** No. Resource data can live on the server. The architectural question concerns how much request meaning depends on hidden conversational context rather than information supplied with the request.

## Next step

Choose a framework branch. Flask begins with factories and explicit composition; FastAPI begins with typed request/response contracts; Django begins with a coordinated project and application structure.
