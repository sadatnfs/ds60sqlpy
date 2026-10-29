## Starting point and result

A partial update must distinguish a missing field from a field explicitly set to null. Treating both as Python `None` can silently erase data or prevent users from clearing an optional value. This chapter uses Pydantic's field-set tracking and a strict request model to make those semantics visible.

## Mechanism: values and presence are separate information

A model instance contains validated values, but it also records which fields the caller supplied. `model_dump(exclude_unset=True)` preserves that distinction when producing an update mapping. A default value can exist on the model without being an instruction to overwrite the stored value.

Consider a profile with a display name and an optional biography. An empty PATCH means that no field should change. A PATCH containing a new display name changes only that name. A PATCH containing `biography: null` explicitly clears the biography when the schema allows null. These are three different commands even if two model attributes appear similar after defaults are applied.

Strict types and forbidden extra fields support a narrow writable surface. An integer field should not accidentally accept a boolean merely because Python treats booleans as integer subclasses. A client-supplied administrative flag should not disappear silently and create the impression that the server honored it. The example makes these cases observable.

## Worked case: preserve an omitted field

The first request supplies an empty object. The handler dumps only explicitly supplied fields, producing an empty update mapping. The assertion checks that both the existing display name and age remain unchanged. A separate direct model assertion compares that omitted-field mapping with a mapping containing an explicitly null display name.

Read the intermediate update mapping as a command, not a complete replacement object. This explains why PUT and PATCH are not interchangeable labels. A replacement representation may require all necessary fields, whereas this PATCH contract permits a subset and documents how null is interpreted.

The example stores a small in-memory fixture so the field-presence mechanism stays visible. A database implementation would translate the validated mapping into an authorized UPDATE, ideally with version checking when concurrent clients can modify the same record. Validation alone does not prevent lost updates.

## Worked case: explicit clearing and refused fields

The second case supplies null for the optional display name and confirms that the stored field is actually cleared while age stays unchanged. Additional requests submit an invalid strict value or an undeclared field. They receive validation failures and leave the earlier valid state intact.

That final state assertion is important. A status code can be correct while an earlier mutation has already occurred. The intended ordering is parse, validate, authorize, compute the permitted change, then commit. If application code mutates a shared object before validating the whole request, error handling cannot reliably undo the side effect.

Presence semantics also affect generated clients. A client that always serializes every optional property as null may issue clearing commands when its caller intended omission. Contract tests should include actual serialized requests from important clients, especially when different languages represent missing values differently.

## Failure diagnosis and discussion

**Why is `exclude_none=True` not equivalent to `exclude_unset=True`?** The former removes explicit null values too. That would discard a legitimate clearing instruction. The latter keeps supplied nulls while excluding fields the caller omitted.

**Where should writable-field ownership be enforced?** In both the request schema and the domain operation. A narrow schema rejects accidental extra fields; the server still derives sensitive values such as owner identity from trusted context rather than request content.

When a PATCH unexpectedly resets values, log the safe field names of the derived update mapping and inspect defaults and field presence. Avoid logging private profile values. Continue with dependency injection, which gives request-scoped resources a similar explicit lifecycle.
