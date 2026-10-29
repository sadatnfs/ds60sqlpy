## Starting point and result

An OpenAPI document describes an HTTP API's paths, operations, schemas and responses. FastAPI derives much of it from route declarations and Pydantic models. This chapter checks that generated contract directly and examines a small breaking request change without depending on an external documentation CDN.

## Mechanism: generated documentation still needs review

The route declares a stable operationId, a request model and a response model. The generated schema includes a successful 201 response and the framework's validation response. Required fields and forbidden extra properties come from the request model.

A schema is a representation of declarations, not proof that every runtime behavior is correct. Authorization, transactional side effects and domain rules may need descriptions and separate tests. A generated client can faithfully implement a mistaken contract, so generation does not remove API design responsibility.

The example disables FastAPI's default Swagger and ReDoc HTML routes because their standard pages reference external assets. It still serves the local OpenAPI JSON. The owned workshop provides an original local explorer using prepared local JavaScript and CSS, with no runtime CDN requirement.

## Worked case: inspect the actual generated operation

The client fetches openapi.json and locates the notes POST operation. It checks the stable operationId, 201 and 422 responses, the required title field and additionalProperties false. It then sends a valid request and verifies the public response.

These assertions connect declarations with real application behavior. They catch a renamed operation or weakened schema that might otherwise break generated clients silently. Stable operation IDs are useful because many generators derive method names from them.

The example also checks that the default documentation routes are absent. That is a deployment choice for an offline product, not a claim that OpenAPI itself requires internet access. The JSON schema and locally prepared documentation UI can work entirely within the owned server.

## Worked case: adding a required field breaks old callers

The program compares an earlier request's required-field set with a proposed set that adds category. Existing callers sending only title would now fail validation. The added required property is therefore a breaking request change even if the endpoint path and response remain unchanged.

Compatibility is directional. Adding an optional response field may be tolerated by some clients but rejected by strict ones. Removing a response field can break consumers. Tightening an enum, changing units or altering pagination semantics can break callers without a dramatic structural difference.

A useful compatibility review combines schema comparison with representative client requests and documented semantics. The small set comparison here explains one mechanism; it is not advertised as a complete OpenAPI compatibility checker.

## Failure diagnosis and discussion

**Does changing only a Python type annotation affect clients?** It can change validation and generated schema, so it may be an API change. Review it as part of the public contract.

**Why not fetch documentation assets when the page opens?** The classroom must remain usable offline and should not make hidden external requests. Asset preparation belongs to a deliberate build step or original local implementation.

If a generated client changes method names unexpectedly, inspect operation IDs. If an old caller starts receiving 422, compare required fields, coercion and bounds before debugging transport. Continue with the integrated application walkthrough, where contract, authentication, persistence and ownership are exercised together.
