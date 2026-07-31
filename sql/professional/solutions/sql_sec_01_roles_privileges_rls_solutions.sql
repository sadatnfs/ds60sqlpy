-- SQL-SEC-01 executable solutions
-- SOLUTION READING MAP — sql-sec-01: Schemas, Roles, Privileges, and Row-Level Security
-- Explanation: sql/professional/solutions/sql_sec_01_roles_privileges_rls_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_sec_01_roles_privileges_rls_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
-- The optional role-admin path is fully rolled back on normal completion.

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
            'ds60_sec_south',
            'ds60_sec_auditor'
        )
    ) AS ds60_role_names_available
    \gset

    \if :ds60_role_names_available
        BEGIN;
        SET LOCAL search_path TO pg_catalog, public;

        CREATE ROLE ds60_sec_owner NOLOGIN;
        CREATE ROLE ds60_sec_north NOLOGIN;
        CREATE ROLE ds60_sec_south NOLOGIN;
        CREATE ROLE ds60_sec_auditor NOLOGIN;
        GRANT ds60_sec_owner TO CURRENT_USER WITH ADMIN OPTION;

        CREATE SCHEMA pro_security_lab AUTHORIZATION ds60_sec_owner;
        REVOKE ALL ON SCHEMA pro_security_lab FROM PUBLIC;

        SET LOCAL ROLE ds60_sec_owner;

        ALTER DEFAULT PRIVILEGES IN SCHEMA pro_security_lab
            REVOKE ALL ON TABLES FROM PUBLIC;
        ALTER DEFAULT PRIVILEGES IN SCHEMA pro_security_lab
            GRANT SELECT ON TABLES
            TO ds60_sec_north, ds60_sec_south, ds60_sec_auditor;
        ALTER DEFAULT PRIVILEGES IN SCHEMA pro_security_lab
            REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

        CREATE TABLE pro_security_lab.documents (
            document_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            tenant_key text NOT NULL
                CHECK (tenant_key IN ('north', 'south')),
            title text NOT NULL,
            body text NOT NULL
        );

        ALTER TABLE pro_security_lab.documents ENABLE ROW LEVEL SECURITY;

        CREATE POLICY tenant_read
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

        -- Exercise 2: auditor has a deliberate read-all policy.
        CREATE POLICY auditor_read
        ON pro_security_lab.documents
        FOR SELECT
        TO ds60_sec_auditor
        USING (true);

        INSERT INTO pro_security_lab.documents (tenant_key, title, body)
        VALUES
            ('north', 'North note', 'North body'),
            ('south', 'South note', 'South body');

        -- Exercise 3: created after the default privilege declaration.
        CREATE TABLE pro_security_lab.audit_notes (
            audit_note_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            note text NOT NULL
        );

        -- Exercise 4: a narrow definer function for an already read-all auditor.
        CREATE FUNCTION pro_security_lab.document_count_for_tenant(
            p_tenant_key text
        )
        RETURNS bigint
        LANGUAGE sql
        STABLE
        SECURITY DEFINER
        SET search_path = pg_catalog
        AS $function$
            SELECT COUNT(*)
            FROM pro_security_lab.documents AS d
            WHERE d.tenant_key = p_tenant_key
              AND p_tenant_key IN ('north', 'south')
        $function$;

        REVOKE ALL
        ON FUNCTION pro_security_lab.document_count_for_tenant(text)
        FROM PUBLIC;
        RESET ROLE;

        GRANT USAGE ON SCHEMA pro_security_lab
        TO ds60_sec_north, ds60_sec_south, ds60_sec_auditor;

        GRANT EXECUTE
        ON FUNCTION pro_security_lab.document_count_for_tenant(text)
        TO ds60_sec_auditor;

        -- Exercise 1: both schema and table layers are visible independently.
        SELECT
            role_name,
            pg_catalog.has_schema_privilege(
                role_name,
                'pro_security_lab',
                'USAGE'
            ) AS has_schema_usage,
            pg_catalog.has_table_privilege(
                role_name,
                'pro_security_lab.documents',
                'SELECT'
            ) AS has_document_select,
            pg_catalog.has_table_privilege(
                role_name,
                'pro_security_lab.documents',
                'INSERT'
            ) AS has_document_insert
        FROM (
            VALUES
                ('ds60_sec_north'::text),
                ('ds60_sec_south'::text),
                ('ds60_sec_auditor'::text)
        ) AS roles(role_name)
        ORDER BY role_name;

        SET LOCAL ROLE ds60_sec_auditor;
        SELECT
            CURRENT_USER AS active_role,
            d.document_id,
            d.tenant_key,
            d.title
        FROM pro_security_lab.documents AS d
        ORDER BY d.document_id;

        SELECT
            pro_security_lab.document_count_for_tenant('north')
                AS north_document_count,
            pro_security_lab.document_count_for_tenant('south')
                AS south_document_count;

        DO $solution$
        BEGIN
            BEGIN
                INSERT INTO pro_security_lab.documents (tenant_key, title, body)
                VALUES ('north', 'Forbidden write', 'Auditor is read-only');
                RAISE EXCEPTION 'auditor INSERT unexpectedly succeeded';
            EXCEPTION
                WHEN insufficient_privilege THEN
                    RAISE NOTICE 'Expected read-only auditor denial: %', SQLERRM;
            END;
        END
        $solution$;
        RESET ROLE;

        DO $solution$
        BEGIN
            IF NOT pg_catalog.has_table_privilege(
                'ds60_sec_auditor',
                'pro_security_lab.audit_notes',
                'SELECT'
            ) THEN
                RAISE EXCEPTION
                    'owner-specific default SELECT did not reach audit_notes';
            END IF;

            IF pg_catalog.has_table_privilege(
                'ds60_sec_auditor',
                'pro_security_lab.documents',
                'INSERT'
            ) THEN
                RAISE EXCEPTION 'auditor unexpectedly has INSERT';
            END IF;
        END
        $solution$;

        -- Exercise 5: run RLS assertions as low-privilege roles. Owners,
        -- superusers, and BYPASSRLS roles are not valid tenant test identities.

        -- Exercise 6: has_*_privilege reports effective access, including
        -- ownership, membership, and PUBLIC. Keep privilege kinds separate.
        SELECT
            role_name,
            pg_catalog.has_schema_privilege(
                role_name, 'pro_security_lab', 'USAGE'
            ) AS schema_usage,
            pg_catalog.has_table_privilege(
                role_name, 'pro_security_lab.documents', 'SELECT'
            ) AS table_select,
            pg_catalog.has_column_privilege(
                role_name,
                'pro_security_lab.documents',
                'title',
                'SELECT'
            ) AS title_select,
            pg_catalog.has_sequence_privilege(
                role_name,
                'pro_security_lab.documents_document_id_seq',
                'USAGE'
            ) AS identity_sequence_usage,
            pg_catalog.has_function_privilege(
                role_name,
                'pro_security_lab.document_count_for_tenant(text)',
                'EXECUTE'
            ) AS count_function_execute
        FROM (
            VALUES
                ('ds60_sec_north'::text),
                ('ds60_sec_south'::text),
                ('ds60_sec_auditor'::text)
        ) AS roles(role_name)
        ORDER BY role_name;

        -- Exercise 7: SESSION_USER remains the authenticated identity while
        -- CURRENT_USER follows SET ROLE and becomes a SECURITY DEFINER owner
        -- inside that function. Audit both identities when the distinction
        -- matters.
        SELECT
            SESSION_USER AS authenticated_identity,
            CURRENT_USER AS effective_identity;
        SET LOCAL ROLE ds60_sec_auditor;
        SELECT
            SESSION_USER AS authenticated_identity,
            CURRENT_USER AS effective_identity;
        RESET ROLE;

        -- Exercise 8: unknown/NULL identities map to NULL, so the policy
        -- predicate is not true. A pooled-session tenant setting would need the
        -- same validation plus guaranteed reset.
        SELECT
            candidate,
            candidate = CASE candidate
                WHEN 'ds60_sec_north' THEN 'ds60_sec_north'
                WHEN 'ds60_sec_south' THEN 'ds60_sec_south'
                ELSE NULL
            END AS accepted_identity
        FROM (
            VALUES
                ('ds60_sec_north'::text),
                ('DS60_SEC_NORTH'::text),
                ('unknown'::text),
                (NULL::text)
        ) AS identities(candidate)
        ORDER BY candidate NULLS LAST;

        -- Exercise 9: a production writer needs column-level INSERT, sequence
        -- USAGE, a tenant WITH CHECK policy, and SELECT only for permitted
        -- RETURNING columns. The course auditor intentionally has none.
        DO $solution$
        BEGIN
            IF pg_catalog.has_table_privilege(
                'ds60_sec_auditor',
                'pro_security_lab.documents',
                'INSERT,UPDATE,DELETE'
            ) THEN
                RAISE EXCEPTION 'auditor unexpectedly has a write privilege';
            END IF;
        END
        $solution$;

        -- Exercise 10: offboarding must cover login/session access, memberships,
        -- ownership, direct/default grants, dependent APIs, verification, audit,
        -- and a preserved recovery administrator. It is deliberately runbook
        -- text rather than destructive cluster-wide SQL.

        ROLLBACK;
        \echo 'SQL-SEC-01 solution complete: all roles and objects rolled back'
    \else
        \echo 'SAFE SKIP: course role names already exist; no objects were changed'
    \endif
\else
    \echo 'SAFE SKIP: role administration is unavailable; no objects were changed'
    SELECT
        CURRENT_USER AS connected_role,
        r.rolsuper,
        r.rolcreaterole,
        r.rolbypassrls
    FROM pg_catalog.pg_roles AS r
    WHERE r.rolname = CURRENT_USER;
\endif
