## Starting point and result

A result page needs a defined order and a defined continuation rule. This chapter joins items to owners, returns a bounded page and compares keyset continuation with an offset after earlier data is deleted. The database operations actually execute through SQLAlchemy and SQLite.

## Mechanism: pagination depends on ordering

The query selects the item ID and owner name in one explicit join, orders by item ID and limits the result to two rows. It does not load an object and then issue an extra owner query for every item. The projection makes the needed columns and relationship explicit.

A cursor value identifies where the next query should begin. Here the cursor is the last observed unique item ID, and the next page uses `Item.id > after`. An offset instead skips a number of rows in the current ordered result. If the result changes between requests, those two definitions can lead to different observations.

A unique ordering key makes this simple cursor unambiguous. If ordering by a nonunique value such as a timestamp, include a stable tie-breaker and encode the complete ordering tuple. A cursor is also application input: validate its type and meaning before constructing the query.

## Worked case: a joined first page

The first page contains item IDs one and two with their corresponding owner names. The query joins the owner table and returns only the selected columns. Assertions check both the IDs and names, so an accidental cross join or incorrect join condition would be visible.

The fixture defines a foreign-key relationship but tests the query behavior here. Database-specific enforcement settings and integrity failure cases are separate concerns. In particular, SQLite deployments must explicitly consider their foreign-key enforcement configuration rather than assuming every declared relation has been tested by a successful join.

## Worked case: deletion shifts an offset

After the first page, item one is deleted. Continuing with cursor two returns IDs three and four. Applying offset two to the changed result instead skips IDs two and three and returns only four. The program reproduces both results.

This does not make every offset API invalid. Offset pagination can be reasonable for small, stable results or explicit page-number navigation. The tradeoff becomes important when data changes, pages grow large or clients require a predictable traversal. A snapshot or other consistency contract may also be necessary for the product's meaning of a complete listing.

## Failure diagnosis

Duplicate or missing items across pages can come from unstable ordering, missing tie-breakers, changed filters or concurrent updates. A cursor must be bound to the relevant query contract, not blindly reused with a different sort order or tenant filter. Large offsets may also require the database to visit and discard substantial work before returning a small page.

If a relationship query becomes slow, inspect the actual SQL and query plan. An ORM method chain is not a performance guarantee. Select only required data, use appropriate indexes and compare observed query counts with the intended behavior.

## Interview discussion

**Why is a LIMIT without a meaningful ORDER BY insufficient?** It bounds the number of returned rows but does not define which stable sequence a client is traversing.

**Does keyset pagination provide a complete historical snapshot?** No. It defines continuation relative to ordering keys. Concurrent inserts, updates and deletion still need a documented consistency interpretation.

## Next step

Use real form validation and CSRF checks. A correctly scoped database query still needs an authenticated and authorized request to invoke it.
