-- SQL-TYPES-01 executable solutions
-- SOLUTION READING MAP — sql-types-01: PostgreSQL-Native Types and Searchable Documents
-- Explanation: sql/professional/solutions/sql_types_01_native_types_search_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_types_01_native_types_search_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL search_path TO pg_catalog, public;
CREATE SCHEMA pro_types_lab;

CREATE TABLE pro_types_lab.documents (
    document_id uuid PRIMARY KEY,
    state text NOT NULL CHECK (state IN ('draft', 'published')),
    title text NOT NULL,
    body text NOT NULL,
    tags text[] NOT NULL,
    availability daterange NOT NULL,
    blackout_windows datemultirange NOT NULL DEFAULT '{}'::datemultirange,
    metadata jsonb NOT NULL CHECK (jsonb_typeof(metadata) = 'object'),
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(
            to_tsvector('english'::regconfig, COALESCE(title, '')),
            'A'
        )
        ||
        setweight(
            to_tsvector('english'::regconfig, COALESCE(body, '')),
            'B'
        )
    ) STORED
);

INSERT INTO pro_types_lab.documents
VALUES
    (
        '00000000-0000-0000-0000-000000000201',
        'published',
        'Safe schema migrations',
        'Verify each schema migration and backfill before contract.',
        ARRAY['postgresql', 'sql', 'operations'],
        daterange(DATE '2026-01-01', DATE '2027-01-01', '[)'),
        datemultirange(
            daterange(DATE '2026-08-10', DATE '2026-08-12', '[)')
        ),
        '{"minutes":45,"audience":["operator"]}',
        DEFAULT
    ),
    (
        '00000000-0000-0000-0000-000000000202',
        'published',
        'SQL analytics',
        'Build retention and funnel queries with explicit grain.',
        ARRAY['postgresql', 'sql', 'analytics'],
        daterange(DATE '2026-01-01', DATE '2027-01-01', '[)'),
        '{}'::datemultirange,
        '{"minutes":35,"audience":["analyst"]}',
        DEFAULT
    ),
    (
        '00000000-0000-0000-0000-000000000203',
        'draft',
        'Python notes',
        'Structured logs and configuration.',
        ARRAY['python'],
        daterange(DATE '2026-01-01', DATE '2026-06-01', '[)'),
        '{}'::datemultirange,
        '{"minutes":20,"audience":["developer"]}',
        DEFAULT
    );

-- Exercise 1.
SELECT
    d.document_id,
    d.title
FROM pro_types_lab.documents AS d
WHERE d.state = 'published'
  AND d.tags @> ARRAY['postgresql', 'operations']::text[]
ORDER BY d.document_id;

-- Exercise 2. Document 201 is excluded by its blackout; document 202 remains.
SELECT
    d.document_id,
    d.title
FROM pro_types_lab.documents AS d
WHERE d.availability @> DATE '2026-08-11'
  AND NOT (d.blackout_windows @> DATE '2026-08-11')
ORDER BY d.document_id;

SELECT
    probe.probe_name,
    probe.probe_date,
    d.availability @> probe.probe_date AS inside_availability,
    d.blackout_windows @> probe.probe_date AS inside_blackout,
    (d.availability @> probe.probe_date)
        AND NOT (d.blackout_windows @> probe.probe_date) AS is_available
FROM pro_types_lab.documents AS d
CROSS JOIN (
    VALUES
        ('availability lower bound'::text, DATE '2026-01-01'),
        ('blackout lower bound', DATE '2026-08-10'),
        ('blackout upper bound', DATE '2026-08-12'),
        ('availability upper bound', DATE '2027-01-01')
) AS probe(probe_name, probe_date)
WHERE d.document_id = '00000000-0000-0000-0000-000000000201'::uuid
ORDER BY probe.probe_date;

-- Exercise 3. JSONPath tests the JSON type and numeric threshold before a
-- numeric cast. It does not promise that every JSON number fits an integer.
SELECT
    d.document_id,
    d.title,
    (d.metadata ->> 'minutes')::numeric AS minutes_numeric
FROM pro_types_lab.documents AS d
WHERE d.metadata @? '$.minutes ? (@.type() == "number" && @ > 30)'
ORDER BY d.document_id;

-- Exercise 4.
WITH query AS (
    SELECT websearch_to_tsquery(
        'english'::regconfig,
        '"schema migration" verify'
    ) AS ts_query
)
SELECT
    d.document_id,
    d.title,
    ts_rank_cd(d.search_vector, query.ts_query) AS rank_score
FROM pro_types_lab.documents AS d
CROSS JOIN query
WHERE d.search_vector @@ query.ts_query
ORDER BY rank_score DESC, d.document_id;

DO $solution$
BEGIN
    IF (
        SELECT COUNT(*)
        FROM pro_types_lab.documents AS d
        WHERE d.tags @> ARRAY['postgresql', 'operations']::text[]
    ) <> 1 THEN
        RAISE EXCEPTION 'tag containment solution failed';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM pro_types_lab.documents AS d
        WHERE d.document_id =
            '00000000-0000-0000-0000-000000000201'::uuid
          AND d.availability @> DATE '2026-08-11'
          AND NOT (d.blackout_windows @> DATE '2026-08-11')
    ) THEN
        RAISE EXCEPTION 'blackout exclusion solution failed';
    END IF;
END
$solution$;

-- Exercise 5: choose an access method from the operators the workload really
-- uses. `nonmatching_query` makes a common false assumption explicit.
SELECT *
FROM (
    VALUES
        ('tags contains all values'::text, 'tags @> ARRAY[...]'::text,
         'GIN array_ops'::text, 'tags[1] = ...'::text,
         'array element position is a different expression'),
        ('JSON containment/path', 'metadata @> ... or metadata @? ...',
         'GIN jsonb_ops or jsonb_path_ops',
         'metadata ->> ''minutes'' > ...',
         'extracted scalar comparison needs an expression/generated-column index'),
        ('full-text match', 'search_vector @@ tsquery',
         'GIN tsvector_ops', 'title ILIKE ''%term%''',
         'substring similarity needs optional pg_trgm, not tsvector GIN'),
        ('range overlap/containment', 'availability @> date',
         'GiST range_ops', 'lower(availability) = date',
         'a lower-bound expression is not a range-containment search')
) AS index_choice(
    workload,
    matching_operator,
    candidate_index,
    nonmatching_query,
    reason
)
ORDER BY workload;

-- Exercise 6: type selection is a domain decision, not a fashion choice.
SELECT *
FROM (
    VALUES
        ('money with a reusable nonnegative rule'::text, 'domain over numeric'::text,
         'fixed scale plus reusable validation; column still declares NOT NULL'::text),
        ('small stable workflow vocabulary', 'CHECK or enum',
         'CHECK is easier to evolve; enum is strongly typed but migration-heavy'),
        ('operator-managed vocabulary', 'reference table',
         'rows carry metadata, lifecycle, and foreign-key identity'),
        ('small owned tag bag', 'array',
         'containment is concise when order and duplicates are not business facts'),
        ('time window', 'range or multirange',
         'boundary and overlap operators encode interval semantics'),
        ('sparse evolving payload', 'JSONB',
         'flexible shape, but frequently queried properties need validation/index policy'),
        ('many-to-many tags', 'normalized relation',
         'foreign keys, canonical identity, and duplicate prevention')
) AS type_decision(field_shape, candidate_type, decision_rule)
ORDER BY field_shape;

-- Exercise 7: discrete date multiranges canonicalize overlapping/adjacent
-- members. Subtracting from the month produces the uncovered gaps.
WITH schedule AS (
    SELECT datemultirange(
        daterange(DATE '2026-08-01', DATE '2026-08-05', '[)'),
        daterange(DATE '2026-08-04', DATE '2026-08-08', '[)'),
        daterange(DATE '2026-08-10', DATE '2026-08-12', '[)')
    ) AS available
)
SELECT
    s.available AS normalized_availability,
    datemultirange(
        daterange(DATE '2026-08-01', DATE '2026-09-01', '[)')
    ) - s.available AS august_gaps
FROM schedule AS s;

-- Exercise 8: longest prefix is the most-specific containing network.
WITH rules(rule_id, network) AS (
    VALUES
        (1, '10.0.0.0/8'::cidr),
        (2, '10.20.0.0/16'::cidr),
        (3, '2001:db8::/32'::cidr)
),
clients(client_id, address) AS (
    VALUES
        ('client-a'::text, '10.20.1.5'::inet),
        ('client-b'::text, '2001:db8::42'::inet),
        ('client-unmatched'::text, '192.0.2.10'::inet)
)
SELECT
    c.client_id,
    c.address,
    best.rule_id,
    best.network
FROM clients AS c
LEFT JOIN LATERAL (
    SELECT r.rule_id, r.network
    FROM rules AS r
    WHERE r.network >>= c.address
    ORDER BY masklen(r.network) DESC, r.rule_id
    LIMIT 1
) AS best
  ON true
ORDER BY c.client_id;

-- Exercise 9: exact decimal storage with an explicit nonnegative reusable rule.
CREATE DOMAIN pro_types_lab.nonnegative_money AS numeric(12, 2)
CHECK (VALUE >= 0);

SELECT
    10.10::pro_types_lab.nonnegative_money
    + 20.20::pro_types_lab.nonnegative_money AS exact_decimal_sum,
    round(10.125::numeric, 2) AS declared_rounding_example,
    NULL::pro_types_lab.nonnegative_money AS domain_null_without_column_rule;

SELECT *
FROM (
    VALUES
        ('numeric(12,2)'::text, 'exact decimal', 'declared half-away-from-zero example', 'common database money model'),
        ('bigint minor units', 'exact integer', 'application supplies currency scale', 'fast and interoperable if scale/currency are explicit'),
        ('double precision', 'binary approximation', 'not exact for decimal equality', 'scientific measurement, not contractual money')
) AS money_choice(storage, equality_model, rounding_policy, suitable_use)
ORDER BY storage;

-- Exercise 10: add malformed-for-this-property-but-valid-JSON probes before
-- defining the generated column. The CASE must classify all of them safely.
INSERT INTO pro_types_lab.documents (
    document_id,
    state,
    title,
    body,
    tags,
    availability,
    blackout_windows,
    metadata
)
SELECT
    probe.document_id,
    'draft',
    probe.title,
    'Boundary fixture',
    ARRAY['boundary'],
    daterange(DATE '2026-01-01', DATE '2027-01-01', '[)'),
    '{}'::datemultirange,
    probe.metadata
FROM (
    VALUES
        ('00000000-0000-0000-0000-000000000210'::uuid, 'String minutes'::text,
         '{"minutes":"45"}'::jsonb),
        ('00000000-0000-0000-0000-000000000211'::uuid, 'Missing minutes',
         '{"audience":[]}'::jsonb),
        ('00000000-0000-0000-0000-000000000212'::uuid, 'Fractional minutes',
         '{"minutes":12.5}'::jsonb),
        ('00000000-0000-0000-0000-000000000213'::uuid, 'Out-of-range minutes',
         '{"minutes":999999999999}'::jsonb)
) AS probe(document_id, title, metadata);

ALTER TABLE pro_types_lab.documents
ADD COLUMN estimated_minutes integer GENERATED ALWAYS AS (
    CASE
        WHEN jsonb_typeof(metadata -> 'minutes') = 'number'
         AND (metadata ->> 'minutes')::numeric
             = trunc((metadata ->> 'minutes')::numeric)
         AND (metadata ->> 'minutes')::numeric BETWEEN 0 AND 2147483647
        THEN ((metadata ->> 'minutes')::numeric)::integer
        ELSE NULL
    END
) STORED;

CREATE INDEX documents_estimated_minutes_idx
ON pro_types_lab.documents (estimated_minutes);

SELECT d.document_id, d.estimated_minutes
FROM pro_types_lab.documents AS d
WHERE d.document_id >= '00000000-0000-0000-0000-000000000210'::uuid
ORDER BY d.document_id;

-- Exercise 11: inspect lexemes after the explicit English configuration.
SELECT
    d.document_id,
    to_tsvector('english'::regconfig, d.title || ' ' || d.body) AS lexemes
FROM pro_types_lab.documents AS d
ORDER BY d.document_id;

-- Exercise 12: normalized vocabulary and bridge enforce tag identity and
-- duplicate prevention through foreign keys plus a composite primary key.
CREATE TABLE pro_types_lab.tags (
    tag_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tag_name text NOT NULL UNIQUE
);

CREATE TABLE pro_types_lab.document_tags (
    document_id uuid NOT NULL
        REFERENCES pro_types_lab.documents (document_id)
        ON DELETE CASCADE,
    tag_id bigint NOT NULL
        REFERENCES pro_types_lab.tags (tag_id)
        ON DELETE RESTRICT,
    PRIMARY KEY (document_id, tag_id)
);

-- Deliberately inject duplicate/case/whitespace legacy spellings. The
-- normalized bridge policy is lower(btrim(tag)); array order is discarded.
UPDATE pro_types_lab.documents
SET tags = ARRAY['python', ' Python ', 'python']
WHERE document_id = '00000000-0000-0000-0000-000000000203'::uuid;

INSERT INTO pro_types_lab.tags (tag_name)
SELECT DISTINCT lower(btrim(tag_name))
FROM pro_types_lab.documents AS d
CROSS JOIN LATERAL unnest(d.tags) AS tag_name
WHERE btrim(tag_name) <> ''
ORDER BY lower(btrim(tag_name));

INSERT INTO pro_types_lab.document_tags (document_id, tag_id)
SELECT DISTINCT d.document_id, t.tag_id
FROM pro_types_lab.documents AS d
CROSS JOIN LATERAL unnest(d.tags) AS item(tag_name)
JOIN pro_types_lab.tags AS t
  ON t.tag_name = lower(btrim(item.tag_name))
WHERE btrim(item.tag_name) <> '';

SELECT
    d.document_id,
    d.title
FROM pro_types_lab.documents AS d
JOIN pro_types_lab.document_tags AS dt
  ON dt.document_id = d.document_id
JOIN pro_types_lab.tags AS t
  ON t.tag_id = dt.tag_id
WHERE t.tag_name IN ('postgresql', 'operations')
GROUP BY d.document_id, d.title
HAVING COUNT(DISTINCT t.tag_name) = 2
ORDER BY d.document_id;

ROLLBACK;
