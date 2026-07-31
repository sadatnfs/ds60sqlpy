-- SQL-SEC-01: Roles, privileges, schemas, and row-level security
-- BEGINNER WORKFLOW — sql-sec-01: Schemas, Roles, Privileges, and Row-Level Security
-- Guide: sql/professional/companion-guides/sql_sec_01_roles_privileges_rls.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-sec-01/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: pg_catalog.pg_roles, pro_security_lab.documents, pro_security_lab.announcements, pro_security_lab.owner_context_documents, pro_security_lab.visible_documents.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Target: PostgreSQL 16+
--
-- The role-admin path creates NOLOGIN course roles inside one transaction and
-- rolls the transaction back. If the connected role lacks CREATEROLE (and is
-- not a superuser), psql prints a safe instructional skip.

\set ON_ERROR_STOP on

SELECT COALESCE(
    (
        SELECT r.rolsuper OR r.rolcreaterole
        FROM pg_catalog.pg_roles AS r
        WHERE r.rolname = CURRENT_USER
    ),
    false
) AS ds60_can_manage_roles
\gset

\if :ds60_can_manage_roles
    SELECT NOT EXISTS (
        SELECT 1
        FROM pg_catalog.pg_roles AS r
        WHERE r.rolname IN (
            'ds60_sec_owner',
            'ds60_sec_north',
            'ds60_sec_south'
        )
    ) AS ds60_role_names_available
    \gset

    \if :ds60_role_names_available
        \echo 'SQL-SEC-01: role capability available; starting disposable lab'
        BEGIN;

        CREATE ROLE ds60_sec_owner NOLOGIN;
        CREATE ROLE ds60_sec_north NOLOGIN;
        CREATE ROLE ds60_sec_south NOLOGIN;

        -- Membership allows this course session to SET ROLE to the object owner.
        -- The transaction rollback removes this membership and all three roles.
        GRANT ds60_sec_owner TO CURRENT_USER WITH ADMIN OPTION;

        CREATE SCHEMA pro_security_lab AUTHORIZATION ds60_sec_owner;
        REVOKE ALL ON SCHEMA pro_security_lab FROM PUBLIC;

        SET LOCAL ROLE ds60_sec_owner;
        SET LOCAL search_path TO pg_catalog, pro_security_lab;

        -- Default privileges belong to the object-creating role and affect only
        -- future objects in this schema.
        ALTER DEFAULT PRIVILEGES IN SCHEMA pro_security_lab
            REVOKE ALL ON TABLES FROM PUBLIC;
        ALTER DEFAULT PRIVILEGES IN SCHEMA pro_security_lab
            GRANT SELECT ON TABLES TO ds60_sec_north, ds60_sec_south;
        ALTER DEFAULT PRIVILEGES IN SCHEMA pro_security_lab
            REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

        CREATE TABLE pro_security_lab.documents (
            document_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            tenant_key text NOT NULL
                CHECK (tenant_key IN ('north', 'south')),
            title text NOT NULL CHECK (btrim(title) <> ''),
            body text NOT NULL,
            created_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );

        CREATE TABLE pro_security_lab.announcements (
            announcement_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            message text NOT NULL
        );

        ALTER TABLE pro_security_lab.documents ENABLE ROW LEVEL SECURITY;

        CREATE POLICY documents_tenant_select
        ON pro_security_lab.documents
        FOR SELECT
        TO ds60_sec_north, ds60_sec_south
        USING (
            tenant_key = CASE CURRENT_USER::text
                WHEN 'ds60_sec_north' THEN 'north'
                WHEN 'ds60_sec_south' THEN 'south'
                ELSE NULL
            END
        );

        CREATE POLICY documents_tenant_insert
        ON pro_security_lab.documents
        FOR INSERT
        TO ds60_sec_north, ds60_sec_south
        WITH CHECK (
            tenant_key = CASE CURRENT_USER::text
                WHEN 'ds60_sec_north' THEN 'north'
                WHEN 'ds60_sec_south' THEN 'south'
                ELSE NULL
            END
        );

        CREATE POLICY documents_tenant_update
        ON pro_security_lab.documents
        FOR UPDATE
        TO ds60_sec_north, ds60_sec_south
        USING (
            tenant_key = CASE CURRENT_USER::text
                WHEN 'ds60_sec_north' THEN 'north'
                WHEN 'ds60_sec_south' THEN 'south'
                ELSE NULL
            END
        )
        WITH CHECK (
            tenant_key = CASE CURRENT_USER::text
                WHEN 'ds60_sec_north' THEN 'north'
                WHEN 'ds60_sec_south' THEN 'south'
                ELSE NULL
            END
        );

        INSERT INTO pro_security_lab.documents (tenant_key, title, body)
        VALUES
            ('north', 'North checklist', 'Visible to the north role.'),
            ('south', 'South checklist', 'Visible to the south role.');

        INSERT INTO pro_security_lab.announcements (message)
        VALUES ('This future table inherited default SELECT grants.');

        -- SECURITY INVOKER preserves the caller as the permission/RLS context.
        CREATE VIEW pro_security_lab.visible_documents
        WITH (security_invoker = true) AS
        SELECT
            d.document_id,
            d.tenant_key,
            d.title,
            d.created_at
        FROM pro_security_lab.documents AS d;

        -- A default view uses its owner's access context for underlying
        -- relations. It is intentionally not exposed to tenant roles.
        CREATE VIEW pro_security_lab.owner_context_documents AS
        SELECT
            d.document_id,
            d.tenant_key,
            d.title
        FROM pro_security_lab.documents AS d;

        CREATE FUNCTION pro_security_lab.visible_document_count()
        RETURNS bigint
        LANGUAGE sql
        STABLE
        SECURITY INVOKER
        SET search_path = pg_catalog
        AS $function$
            SELECT COUNT(*)
            FROM pro_security_lab.documents AS d
        $function$;

        -- SECURITY DEFINER changes current_user to the function owner. The fixed
        -- search_path, qualified table, narrow return value, and explicit revoke
        -- are minimum controls; this example is not granted to tenant roles.
        CREATE FUNCTION pro_security_lab.owner_document_count(p_tenant_key text)
        RETURNS bigint
        LANGUAGE sql
        STABLE
        SECURITY DEFINER
        SET search_path = pg_catalog
        AS $function$
            SELECT COUNT(*)
            FROM pro_security_lab.documents AS d
            WHERE d.tenant_key = p_tenant_key
        $function$;

        REVOKE ALL
        ON FUNCTION pro_security_lab.visible_document_count()
        FROM PUBLIC;
        REVOKE ALL
        ON FUNCTION pro_security_lab.owner_document_count(text)
        FROM PUBLIC;

        RESET ROLE;

        -- Schema USAGE permits name resolution; it does not grant table access.
        GRANT USAGE ON SCHEMA pro_security_lab
        TO ds60_sec_north, ds60_sec_south;

        -- Default privileges supplied SELECT. Add only the write operations and
        -- columns required by the exercise.
        GRANT INSERT (tenant_key, title, body),
              UPDATE (title, body)
        ON TABLE pro_security_lab.documents
        TO ds60_sec_north, ds60_sec_south;

        GRANT USAGE, SELECT
        ON ALL SEQUENCES IN SCHEMA pro_security_lab
        TO ds60_sec_north, ds60_sec_south;

        GRANT EXECUTE
        ON FUNCTION pro_security_lab.visible_document_count()
        TO ds60_sec_north, ds60_sec_south;

        REVOKE ALL
        ON TABLE pro_security_lab.owner_context_documents
        FROM ds60_sec_north, ds60_sec_south;
        REVOKE ALL
        ON FUNCTION pro_security_lab.owner_document_count(text)
        FROM ds60_sec_north, ds60_sec_south;

        \echo 'Privilege inspection before acting as tenant roles'
        SELECT
            access.role_name,
            pg_catalog.has_schema_privilege(
                access.role_name,
                'pro_security_lab',
                'USAGE'
            ) AS has_schema_usage,
            pg_catalog.has_table_privilege(
                access.role_name,
                'pro_security_lab.documents',
                'SELECT'
            ) AS can_select_documents,
            pg_catalog.has_table_privilege(
                access.role_name,
                'pro_security_lab.documents',
                'DELETE'
            ) AS can_delete_documents,
            pg_catalog.has_table_privilege(
                access.role_name,
                'pro_security_lab.announcements',
                'SELECT'
            ) AS inherited_future_select
        FROM (
            VALUES
                ('ds60_sec_north'::text),
                ('ds60_sec_south'::text)
        ) AS access(role_name)
        ORDER BY access.role_name;

        \echo 'North: allowed SELECT, INSERT, and title UPDATE'
        SET LOCAL ROLE ds60_sec_north;
        SET LOCAL search_path TO pg_catalog, pro_security_lab;

        SELECT
            CURRENT_USER AS active_role,
            vd.document_id,
            vd.tenant_key,
            vd.title
        FROM pro_security_lab.visible_documents AS vd
        ORDER BY vd.document_id;

        SELECT
            CURRENT_USER AS active_role,
            pro_security_lab.visible_document_count() AS visible_count;

        INSERT INTO pro_security_lab.documents (tenant_key, title, body)
        VALUES ('north', 'North follow-up', 'Inserted by the north role.')
        RETURNING document_id, tenant_key, title;

        UPDATE pro_security_lab.documents AS d
        SET title = 'North checklist - reviewed'
        WHERE d.tenant_key = 'north'
          AND d.title = 'North checklist'
        RETURNING document_id, tenant_key, title;

        \echo 'North: expected RLS denial for a south INSERT'
        DO $rls_test$
        BEGIN
            BEGIN
                INSERT INTO pro_security_lab.documents (tenant_key, title, body)
                VALUES ('south', 'Cross-tenant insert', 'Must be rejected.');
                RAISE EXCEPTION 'cross-tenant INSERT unexpectedly succeeded';
            EXCEPTION
                WHEN insufficient_privilege THEN
                    RAISE NOTICE 'Expected row-policy denial: %', SQLERRM;
            END;
        END
        $rls_test$;

        \echo 'North: expected privilege denial for DELETE'
        DO $privilege_test$
        BEGIN
            BEGIN
                DELETE FROM pro_security_lab.documents AS d
                WHERE d.tenant_key = 'north';
                RAISE EXCEPTION 'DELETE unexpectedly succeeded';
            EXCEPTION
                WHEN insufficient_privilege THEN
                    RAISE NOTICE 'Expected DELETE privilege denial: %', SQLERRM;
            END;
        END
        $privilege_test$;
        RESET ROLE;

        \echo 'South: the same invoker view exposes only south rows'
        SET LOCAL ROLE ds60_sec_south;
        SET LOCAL search_path TO pg_catalog, pro_security_lab;
        SELECT
            CURRENT_USER AS active_role,
            vd.document_id,
            vd.tenant_key,
            vd.title
        FROM pro_security_lab.visible_documents AS vd
        ORDER BY vd.document_id;

        SELECT
            CURRENT_USER AS active_role,
            pro_security_lab.visible_document_count() AS visible_count;
        RESET ROLE;

        \echo 'Owner: table owners normally bypass RLS unless FORCE RLS is used'
        SET LOCAL ROLE ds60_sec_owner;
        SELECT
            CURRENT_USER AS active_role,
            COUNT(*) AS owner_visible_count
        FROM pro_security_lab.documents AS d;

        SELECT
            pro_security_lab.owner_document_count('south')
                AS owner_context_south_count;
        RESET ROLE;

        SELECT
            c.relname,
            c.reloptions
        FROM pg_catalog.pg_class AS c
        JOIN pg_catalog.pg_namespace AS n
          ON n.oid = c.relnamespace
        WHERE n.nspname = 'pro_security_lab'
          AND c.relname IN ('visible_documents', 'owner_context_documents')
        ORDER BY c.relname;

        -- Exercises:
        --
        -- 1. Explain why schema USAGE without table SELECT is insufficient, and
        --    why table SELECT without schema USAGE is also insufficient. Extend
        --    the has_*_privilege query to prove both layers.
        --    Inputs: For sql-sec-01 Exercise 1, test schema USAGE and table SELECT as separate privilege layers, first before schema grants and then after temporarily removing one table grant.
        --    Expected result/shape: For sql-sec-01 Exercise 1, expected output: evidence for table SELECT without schema USAGE, schema USAGE without table SELECT, and a final three-role matrix with USAGE/SELECT true and INSERT false.
        --    Verify: For sql-sec-01 Exercise 1, assert the two observed boolean rows equal `(USAGE=false, SELECT=true)` and `(USAGE=true, SELECT=false)`, attempt the corresponding qualified SELECTs, and restore only the intended least-privilege state before later exercises.
        --    Hint ladder, rung 1: For sql-sec-01 Exercise 1, check the two-layer reads written analysis against `usage`, `has_schema_privilege`, `has_table_privilege`, and `insert`.
        --
        -- 2. Add a NOLOGIN ds60_sec_auditor role. Grant only schema USAGE and
        --    SELECT, then add a SELECT policy that permits both tenants. Prove it
        --    sees all current documents but cannot INSERT, UPDATE, or DELETE.
        --    Inputs: For sql-sec-01 Exercise 2, grant the auditor table SELECT via owner defaults, schema USAGE explicitly, and an RLS SELECT policy with `USING (true)`; grant no table writes.
        --    Expected result/shape: For sql-sec-01 Exercise 2, expected output: two tenant rows when SET ROLE auditor, correct north/south definer counts, and an expected insufficient-privilege notice for INSERT.
        --    Verify: For sql-sec-01 Exercise 2, assert the auditor sees exactly both seeded IDs, has no INSERT/UPDATE/DELETE privilege, and cannot execute routines except those explicitly granted.
        --    Hint ladder, rung 1: For sql-sec-01 Exercise 2, inspect `pg_catalog.pg_roles`, `information_schema.role_table_grants`, `pg_catalog.pg_policies`, and `pg_catalog.pg_class` for `auditor_read`, `pro_security_lab.documents`, and `ds60_sec_auditor`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object.
        --
        -- 3. Verify that a table created by ds60_sec_owner after ALTER DEFAULT
        --    PRIVILEGES automatically grants SELECT to tenant roles. Explain why
        --    a table created by a different owner would not inherit that rule.
        --    Inputs: For sql-sec-01 Exercise 3, create one future table as the role whose default privileges were configured and one as a different NOLOGIN owner with schema CREATE authority.
        --    Expected result/shape: For sql-sec-01 Exercise 3, expected output: the auditor has SELECT on `audit_notes` created by `ds60_sec_owner` but not on `other_owner_notes` created by `ds60_sec_other_owner`.
        --    Verify: For sql-sec-01 Exercise 3, compare `has_table_privilege` for both tables and state that ALTER DEFAULT PRIVILEGES uses only the current object's creating role—not inherited membership defaults.
        --    Hint ladder, rung 1: For sql-sec-01 Exercise 3, select `ds60_sec_auditor` from `ds60_sec_owner` before adding derived columns.
        --
        -- 4. Review owner_document_count(text). List the controls that make a
        --    SECURITY DEFINER routine safer, and explain why granting an
        --    arbitrary-tenant parameter to ordinary tenant roles would cross the
        --    row-security boundary.
        --    Inputs: For sql-sec-01 Exercise 4, create a validated, fixed-search-path SECURITY DEFINER tenant-count function owned by the NOLOGIN owner, revoke PUBLIC, grant only the auditor, and inspect `pg_proc`.
        --    Expected result/shape: For sql-sec-01 Exercise 4, expected output: valid north/south counts, an invalid-parameter rejection for unknown tenant, and catalog rows with owner, `prosecdef`, `proconfig`, and `proacl`.
        --    Verify: For sql-sec-01 Exercise 4, test allowed and NULL/unknown inputs under SET ROLE auditor, assert PUBLIC lacks EXECUTE, confirm the owner cannot login, and trace every referenced object as schema-qualified.
        --    Hint ladder, rung 1: For sql-sec-01 Exercise 4, check the definer boundary written analysis against `document_count_for_tenant`, `search_path`, and `current_user`.
        --
        -- 5. Explain the RLS bypass behavior for a table owner, a superuser, and
        --    a role with BYPASSRLS. When can FORCE ROW LEVEL SECURITY subject an
        --    ordinary table owner to policies, and who still bypasses them?
        --    Inputs: For sql-sec-01 Exercise 5, SET LOCAL ROLE north and south separately, query the RLS table, then FORCE RLS and test the table owner; inventory superuser/BYPASSRLS separately.
        --    Expected result/shape: For sql-sec-01 Exercise 5, expected output: north sees only north, south sees only south, the forced owner sees zero without a matching policy, and bypass-capable roles are clearly labeled unsuitable tenant-test identities.
        --    Verify: For sql-sec-01 Exercise 5, assert one own-tenant row and zero cross-tenant rows for each low-privilege role, distinguish owner bypass before FORCE from forced-owner behavior, and never grant or rely on BYPASSRLS for tenants.
        --    Hint ladder, rung 1: For sql-sec-01 Exercise 5, check the rls bypass written analysis against `bypassrls`.
        --
        -- 6. Build an effective-access inventory for every course role across
        --    schema, table, column, sequence, and routine privileges. Include
        --    inherited membership and PUBLIC; do not mistake ACL text for the
        --    final answer.
        --    Inputs: For sql-sec-01 Exercise 6, use PostgreSQL `has_*_privilege` functions to report schema, table, column, sequence, and function access for north, south, and auditor roles.
        --    Expected result/shape: For sql-sec-01 Exercise 6, expected output: one row per role with five distinct privilege booleans and an `effective_source` explanation distinguishing owner-default table grants from direct function grants.
        --    Verify: For sql-sec-01 Exercise 6, compare every effective-access boolean row with object ACLs, role membership, ownership, and PUBLIC and record the matching source evidence; do not infer the grant source from a true boolean alone.
        --    Hint ladder, rung 1: For sql-sec-01 Exercise 6, check the effective access written analysis against `has__privilege`, `aclexplode`, `insert`, and `usage`.
        --
        -- 7. Demonstrate SESSION_USER versus CURRENT_USER before, during, and
        --    after SET ROLE, then explain their values inside a SECURITY DEFINER
        --    routine. Which identity should an audit record preserve?
        --    Inputs: For sql-sec-01 Exercise 7, display SESSION_USER/CURRENT_USER before SET ROLE, after SET ROLE auditor, and from inside an auditor-invoked SECURITY DEFINER identity probe.
        --    Expected result/shape: For sql-sec-01 Exercise 7, expected output: authenticated identity remains SESSION_USER; effective identity changes to auditor under SET ROLE and to the function owner inside SECURITY DEFINER.
        --    Verify: For sql-sec-01 Exercise 7, compare all three evidence rows and design audit fields that preserve both identities plus the called routine and tenant context.
        --    Hint ladder, rung 1: For sql-sec-01 Exercise 7, check the identity context written analysis against `session_user`, and `current_user`.
        --
        -- 8. Add negative tests for NULL, mixed-case, and unknown tenant
        --    identifiers. Prove the policy fails closed and explain why a
        --    session setting used for tenancy must be validated and reset.
        --    Inputs: For sql-sec-01 Exercise 8, map exact role names to tenant keys with a fail-closed CASE; test lowercase valid roles, case mismatch, unknown, and NULL.
        --    Expected result/shape: For sql-sec-01 Exercise 8, expected output: four rows with `candidate_role`, `derived_tenant`, and `accepted_identity`; only exact north/south role names are accepted.
        --    Verify: For sql-sec-01 Exercise 8, assert unknown, case-changed, and NULL identities derive NULL and `accepted_identity = false`; if a pooled custom setting is adopted instead, validate and transaction-locally reset it.
        --    Hint ladder, rung 1: For sql-sec-01 Exercise 8, check the fail-closed tenancy written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
        --
        -- 9. Create an API-only writer role in a scratch transaction. Grant
        --    schema USAGE and EXECUTE on one hardened tenant-specific insert
        --    function, but no table or sequence privileges. Prove the API
        --    returns only the inserted row and direct SELECT/INSERT/UPDATE/
        --    DELETE remain denied.
        --    Inputs: For sql-sec-01 Exercise 9, create a NOLOGIN API-only writer with schema USAGE and one explicit function EXECUTE grant; give it no table or sequence privileges, while the hardened owner API enforces north-only INSERT/RETURNING under FORCE RLS.
        --    Expected result/shape: For sql-sec-01 Exercise 9, expected output: one returned north document from the insert API; cross-tenant INSERT, direct UPDATE, DELETE, and table SELECT each produce an expected denial.
        --    Verify: For sql-sec-01 Exercise 9, SET LOCAL ROLE writer for every probe, assert the API owner/path/ACL and owner-scoped RLS policies in catalogs, confirm no direct table or sequence privilege, and prove the failed operations leave no rows changed.
        --    Hint ladder, rung 1: For sql-sec-01 Exercise 9, check the narrow writer written analysis against `usage`, `insert`, and `returning`.
        --
        -- 10. Write an offboarding and incident-revocation runbook. Cover login
        --     revocation, active sessions, memberships, owned objects, default
        --     privileges, dependent grants, verification, and recoverable audit
        --     evidence; do not execute destructive cluster-wide commands here.
        --    Inputs: For sql-sec-01 Exercise 10, return a non-destructive offboarding plan covering login/session fencing, ownership, memberships, current/default grants, dependent credentials, negative verification, and break-glass recovery.
        --    `pg_catalog.pg_roles`, `pg_catalog.pg_auth_members`, and
        --    `information_schema.role_table_grants`; keep `rolname`,
        --    `member`, `roleid`, and the grantor/grantee identity visible.
        --    Expected result/shape: For sql-sec-01 Exercise 10, expected output: seven rows ordered by `step_number` with `action` and `required_evidence`; no cluster-wide destructive command is executed.
        --    Verify: For sql-sec-01 Exercise 10, rehearse the plan with an expendable role and record an evidence checklist: owned/dependent-object counts before revocation, denied-login/query results, application smoke-test result, and independently tested recovery administrator.
        --    Hint ladder, rung 1: For sql-sec-01 Exercise 10, check the revocation runbook written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.

        ROLLBACK;
        \echo 'SQL-SEC-01 complete: roles and pro_security_lab were rolled back'
    \else
        \echo 'SAFE SKIP: course role names already exist; no objects were changed'
        \echo 'Remove only known disposable course roles before retrying.'
    \endif
\else
    \echo 'SAFE SKIP: the connected PostgreSQL role cannot administer roles.'
    \echo 'Read the guide and learner SQL; ask a local administrator for a disposable'
    \echo 'CREATEROLE training account only if hands-on role testing is appropriate.'
    SELECT
        CURRENT_USER AS connected_role,
        r.rolsuper,
        r.rolcreaterole,
        r.rolbypassrls
    FROM pg_catalog.pg_roles AS r
    WHERE r.rolname = CURRENT_USER;
\endif
