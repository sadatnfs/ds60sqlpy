## Starting point and result

Caching can avoid transferring an unchanged representation, but it must respect privacy and consistency. An ETag is a validator associated with a representation. This chapter computes one from fixed JSON bytes, tests a conditional request and contrasts a publicly cacheable resource with a private account response.

## Mechanism: a validator describes a representation

The resource's byte string is hashed to produce a strong ETag. The response supplies that validator and a public max-age policy. `make_conditional` examines the incoming request and can return 304 when the client's validator matches.

A strong validator must correspond to the relevant representation bytes under the declared HTTP semantics. Two serializers can produce semantically equivalent JSON with different bytes, so an implementation must decide where the validator is computed and how content encoding or variants affect it. This fixture fixes the bytes explicitly to make the relationship testable.

Cache-Control and ETag serve different roles. A cache policy states when reuse is permitted; a validator helps determine whether a stored representation still matches. An authenticated or personalized response may need private or no-store handling even if its content changes rarely.

## Worked case: reuse an unchanged representation

The first request receives status 200 and an ETag. The next request sends that value in If-None-Match. The server returns 304 with no response body. A third request sends another validator and receives the full 200 response.

The program verifies status, empty conditional body and the exact validator derived from the known bytes. It also inspects the declared max-age/public policy. These are application/protocol observations. The test client is not being claimed as a browser cache that actually stores and reuses the response automatically.

Conditional requests can reduce transfer cost, but they do not necessarily eliminate all server work. If an expensive database calculation is needed before computing the ETag, the representation may still be costly to validate. Version counters, modification metadata or other domain-specific validators can be useful when their semantics are correct.

## Worked case: a private account response has a different policy

The account fixture returns `Cache-Control: private, no-store`. The program checks the exact declaration instead of applying the public resource's policy everywhere. This matters because shared intermediary caches can serve responses to multiple clients under their configured rules.

A cache key must also account for relevant representation differences. Language, content negotiation, authorization scope and query filters can affect the result. A convenient key that omits one of those dimensions can return a valid representation to the wrong request.

## Failure diagnosis

Stale data can come from an overly broad freshness period, a validator that does not change with the representation or an incomplete cache key. Privacy leaks can arise from caching personalized content as public. Unexpected 200 responses to conditional requests can result from quotation/validator mismatches or comparing a different representation variant.

Do not use caching to conceal a correctness problem in the underlying resource. Later chapters address invalidation and shared-worker coordination explicitly. A process-local dictionary cache has different durability and consistency behavior from a browser or reverse-proxy cache.

## Interview discussion

**Is a 304 response an error?** No. It communicates that the client's stored representation can be used under the conditional request contract. The client must already have the relevant representation.

**Does an ETag authorize access?** No. Authorization still applies to the request. A validator is not a credential or proof that the caller may read a protected resource.

## Next step

Use explicit CLI and migration operations to evolve stored state. A new application version must remain compatible with the schema and data it encounters.
