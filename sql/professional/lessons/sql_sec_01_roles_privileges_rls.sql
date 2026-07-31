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
        --    Inputs: For sql-sec-01 Exercise 1, complete the two-layer reads written analysis and support its claims with read-only evidence from `pg_catalog.pg_roles`, `PUBLIC`, and `TO`. Mark unverified assumptions explicitly.
        --    Expected result/shape: For sql-sec-01 Exercise 1, expected output: a completed the two-layer reads written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `usage`, `has_schema_privilege`, `has_table_privilege`, and `insert`.
        --    Verify: For sql-sec-01 Exercise 1, check the two-layer reads written analysis against `usage`, `has_schema_privilege`, `has_table_privilege`, and `insert`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
        --    Hint ladder, rung 1: For sql-sec-01 Exercise 1, check the two-layer reads written analysis against `usage`, `has_schema_privilege`, `has_table_privilege`, and `insert`.
        --
        -- 2. Add a NOLOGIN ds60_sec_auditor role. Grant only schema USAGE and
        --    SELECT, then add a SELECT policy that permits both tenants. Prove it
        --    sees all current documents but cannot INSERT, UPDATE, or DELETE.
        --    Inputs: For sql-sec-01 Exercise 2, change only `auditor_read`, `pro_security_lab.documents`, and `ds60_sec_auditor` inside the lesson rollback/cleanup boundary. Capture the DDL command tag and the relevant `pg_catalog.pg_roles`, `information_schema.role_table_grants`, `pg_catalog.pg_policies`, and `pg_catalog.pg_class` rows.
        --    Expected result/shape: For sql-sec-01 Exercise 2, expected output: the requested DDL command tag plus catalog rows and one accepted and one rejected behavior. The final columns are `usage`.
        --    Verify: For sql-sec-01 Exercise 2, inspect `pg_catalog.pg_roles`, `information_schema.role_table_grants`, `pg_catalog.pg_policies`, and `pg_catalog.pg_class` for `auditor_read`, `pro_security_lab.documents`, and `ds60_sec_auditor`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object. Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.
        --    Hint ladder, rung 1: For sql-sec-01 Exercise 2, inspect `pg_catalog.pg_roles`, `information_schema.role_table_grants`, `pg_catalog.pg_policies`, and `pg_catalog.pg_class` for `auditor_read`, `pro_security_lab.documents`, and `ds60_sec_auditor`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object.
        --
        -- 3. Verify that a table created by ds60_sec_owner after ALTER DEFAULT
        --    PRIVILEGES automatically grants SELECT to tenant roles. Explain why
        --    a table created by a different owner would not inherit that rule.
        --    Inputs: For sql-sec-01 Exercise 3, read from `ds60_sec_owner`. Compute `ds60_sec_auditor` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
        --    Expected result/shape: For sql-sec-01 Exercise 3, expected output: exactly one aggregate summary row. The final columns are `ds60_sec_auditor`.
        --    Verify: For sql-sec-01 Exercise 3, evaluate each of `row_count` in a separate control `SELECT` over `ds60_sec_owner`; require one final row and compare every value. Run the same operation as one allowed identity and one denied identity; record both outcomes without granting new access.
        --    Hint ladder, rung 1: For sql-sec-01 Exercise 3, select `ds60_sec_auditor` from `ds60_sec_owner` before adding derived columns.
        --
        -- 4. Review owner_document_count(text). List the controls that make a
        --    SECURITY DEFINER routine safer, and explain why granting an
        --    arbitrary-tenant parameter to ordinary tenant roles would cross the
        --    row-security boundary.
        --    Inputs: For sql-sec-01 Exercise 4, complete the definer boundary written analysis and support its claims with read-only evidence from `pg_catalog.pg_roles`, `PUBLIC`, and `TO`. Mark unverified assumptions explicitly.
        --    Expected result/shape: For sql-sec-01 Exercise 4, expected output: a completed the definer boundary written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `document_count_for_tenant`, `search_path`, and `current_user`.
        --    Verify: For sql-sec-01 Exercise 4, check the definer boundary written analysis against `document_count_for_tenant`, `search_path`, and `current_user`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
        --    Hint ladder, rung 1: For sql-sec-01 Exercise 4, check the definer boundary written analysis against `document_count_for_tenant`, `search_path`, and `current_user`.
        --
        -- 5. Explain the RLS bypass behavior for a table owner, a superuser, and
        --    a role with BYPASSRLS. When can FORCE ROW LEVEL SECURITY subject an
        --    ordinary table owner to policies, and who still bypasses them?
        --    Inputs: For sql-sec-01 Exercise 5, complete the rls bypass written analysis and support its claims with read-only evidence from `pg_catalog.pg_roles`, `PUBLIC`, and `TO`. Mark unverified assumptions explicitly.
        --    Expected result/shape: For sql-sec-01 Exercise 5, expected output: a completed the rls bypass written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `bypassrls`.
        --    Verify: For sql-sec-01 Exercise 5, check the rls bypass written analysis against `bypassrls`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
        --    Hint ladder, rung 1: For sql-sec-01 Exercise 5, check the rls bypass written analysis against `bypassrls`.
        --
        -- 6. Build an effective-access inventory for every course role across
        --    schema, table, column, sequence, and routine privileges. Include
        --    inherited membership and PUBLIC; do not mistake ACL text for the
        --    final answer.
        --    Inputs: For sql-sec-01 Exercise 6, complete the effective access written analysis and support its claims with read-only evidence from `pg_auth_members`. Mark unverified assumptions explicitly.
        --    Expected result/shape: For sql-sec-01 Exercise 6, expected output: a completed the effective access written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `has__privilege`, `aclexplode`, `insert`, and `usage`.
        --    Verify: For sql-sec-01 Exercise 6, check the effective access written analysis against `has__privilege`, `aclexplode`, `insert`, and `usage`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
        --    Hint ladder, rung 1: For sql-sec-01 Exercise 6, check the effective access written analysis against `has__privilege`, `aclexplode`, `insert`, and `usage`.
        --
        -- 7. Demonstrate SESSION_USER versus CURRENT_USER before, during, and
        --    after SET ROLE, then explain their values inside a SECURITY DEFINER
        --    routine. Which identity should an audit record preserve?
        --    Inputs: For sql-sec-01 Exercise 7, complete the identity context written analysis and support its claims with read-only evidence from `pg_catalog.pg_roles`, `PUBLIC`, and `TO`. Mark unverified assumptions explicitly.
        --    Expected result/shape: For sql-sec-01 Exercise 7, expected output: a completed the identity context written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `session_user`, and `current_user`.
        --    Verify: For sql-sec-01 Exercise 7, check the identity context written analysis against `session_user`, and `current_user`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
        --    Hint ladder, rung 1: For sql-sec-01 Exercise 7, check the identity context written analysis against `session_user`, and `current_user`.
        --
        -- 8. Add negative tests for NULL, mixed-case, and unknown tenant
        --    identifiers. Prove the policy fails closed and explain why a
        --    session setting used for tenancy must be validated and reset.
        --    Inputs: For sql-sec-01 Exercise 8, complete the fail-closed tenancy written analysis and support its claims with read-only evidence from `pg_catalog.pg_roles`, `PUBLIC`, and `TO`. Mark unverified assumptions explicitly.
        --    Expected result/shape: For sql-sec-01 Exercise 8, expected output: a completed the fail-closed tenancy written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
        --    Verify: For sql-sec-01 Exercise 8, check the fail-closed tenancy written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
        --    Hint ladder, rung 1: For sql-sec-01 Exercise 8, check the fail-closed tenancy written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
        --
        -- 9. Create a narrow writer role in a scratch transaction. Grant only
        --    the columns and identity-sequence privileges needed for INSERT,
        --    prove RETURNING does not leak forbidden columns, and prove UPDATE
        --    and DELETE remain denied.
        --    Inputs: For sql-sec-01 Exercise 9, complete the narrow writer written analysis and support its claims with read-only evidence from `pg_catalog.pg_roles`, `PUBLIC`, and `TO`. Mark unverified assumptions explicitly.
        --    Expected result/shape: For sql-sec-01 Exercise 9, expected output: a completed the narrow writer written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `usage`, `insert`, and `returning`.
        --    Verify: For sql-sec-01 Exercise 9, check the narrow writer written analysis against `usage`, `insert`, and `returning`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
        --    Hint ladder, rung 1: For sql-sec-01 Exercise 9, check the narrow writer written analysis against `usage`, `insert`, and `returning`.
        --
        -- 10. Write an offboarding and incident-revocation runbook. Cover login
        --     revocation, active sessions, memberships, owned objects, default
        --     privileges, dependent grants, verification, and recoverable audit
        --     evidence; do not execute destructive cluster-wide commands here.
        --    Inputs: For sql-sec-01 Exercise 10, complete the revocation runbook written analysis and support its claims with read-only evidence from `pg_catalog.pg_roles`, `PUBLIC`, and `TO`. Mark unverified assumptions explicitly.
        --    `pg_catalog.pg_roles`, `pg_catalog.pg_auth_members`, and
        --    `information_schema.role_table_grants`; keep `rolname`,
        --    `member`, `roleid`, and the grantor/grantee identity visible.
        --    Expected result/shape: For sql-sec-01 Exercise 10, expected output: a completed the revocation runbook written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
        --    Verify: For sql-sec-01 Exercise 10, check the revocation runbook written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
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
