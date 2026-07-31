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
            'ds60_sec_auditor',
            'ds60_sec_writer',
            'ds60_sec_other_owner'
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
        CREATE ROLE ds60_sec_writer NOLOGIN;
        CREATE ROLE ds60_sec_other_owner NOLOGIN;
        GRANT ds60_sec_owner TO CURRENT_USER WITH ADMIN OPTION;
        GRANT ds60_sec_other_owner TO CURRENT_USER WITH ADMIN OPTION;
        GRANT ds60_sec_north, ds60_sec_south, ds60_sec_auditor,
              ds60_sec_writer TO CURRENT_USER WITH ADMIN OPTION;

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
        LANGUAGE plpgsql
        STABLE
        SECURITY DEFINER
        SET search_path = pg_catalog
        AS $function$
        BEGIN
            IF p_tenant_key IS NULL
               OR p_tenant_key NOT IN ('north', 'south') THEN
                RAISE EXCEPTION 'invalid tenant key'
                    USING ERRCODE = 'invalid_parameter_value';
            END IF;

            RETURN (
                SELECT COUNT(*)
                FROM pro_security_lab.documents AS d
                WHERE d.tenant_key = p_tenant_key
            );
        END
        $function$;

        CREATE FUNCTION pro_security_lab.identity_probe(
            OUT authenticated_identity name,
            OUT effective_identity name
        )
        RETURNS record
        LANGUAGE sql
        STABLE
        SECURITY DEFINER
        SET search_path = pg_catalog
        AS $function$
            SELECT SESSION_USER, CURRENT_USER
        $function$;

        REVOKE ALL
        ON FUNCTION pro_security_lab.document_count_for_tenant(text)
        FROM PUBLIC;
        REVOKE ALL
        ON FUNCTION pro_security_lab.identity_probe()
        FROM PUBLIC;
        RESET ROLE;

        -- Exercise 1, stage A: table SELECT was granted by the owner's default
        -- privileges, but no caller can resolve/use the schema yet.
        SELECT
            'table grant without schema usage' AS evidence_stage,
            pg_catalog.has_schema_privilege(
                'ds60_sec_north', 'pro_security_lab', 'USAGE'
            ) AS has_schema_usage,
            pg_catalog.has_table_privilege(
                'ds60_sec_north',
                'pro_security_lab.documents',
                'SELECT'
            ) AS has_document_select;

        GRANT USAGE ON SCHEMA pro_security_lab
        TO ds60_sec_north, ds60_sec_south, ds60_sec_auditor,
           ds60_sec_writer;

        -- Exercise 1, stage B: prove the inverse combination too, then restore
        -- the required SELECT before the tenant-isolation tests.
        REVOKE SELECT ON pro_security_lab.documents FROM ds60_sec_south;
        SELECT
            'schema usage without table select' AS evidence_stage,
            pg_catalog.has_schema_privilege(
                'ds60_sec_south', 'pro_security_lab', 'USAGE'
            ) AS has_schema_usage,
            pg_catalog.has_table_privilege(
                'ds60_sec_south',
                'pro_security_lab.documents',
                'SELECT'
            ) AS has_document_select;
        GRANT SELECT ON pro_security_lab.documents TO ds60_sec_south;

        GRANT EXECUTE
        ON FUNCTION pro_security_lab.document_count_for_tenant(text)
        TO ds60_sec_auditor;
        GRANT EXECUTE
        ON FUNCTION pro_security_lab.identity_probe()
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
                PERFORM pro_security_lab.document_count_for_tenant('unknown');
                RAISE EXCEPTION 'invalid tenant unexpectedly succeeded';
            EXCEPTION
                WHEN invalid_parameter_value THEN
                    RAISE NOTICE 'Expected invalid-tenant rejection: %', SQLERRM;
            END;
        END
        $solution$;

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

        -- Exercise 3: default privileges are owner-specific. Give a second
        -- owner CREATE authority, then prove ds60_sec_owner's defaults do not
        -- leak onto the second owner's future table.
        GRANT USAGE, CREATE ON SCHEMA pro_security_lab
        TO ds60_sec_other_owner;
        SET LOCAL ROLE ds60_sec_other_owner;
        CREATE TABLE pro_security_lab.other_owner_notes (
            note_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            note text NOT NULL
        );
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

            IF pg_catalog.has_table_privilege(
                'ds60_sec_auditor',
                'pro_security_lab.other_owner_notes',
                'SELECT'
            ) THEN
                RAISE EXCEPTION
                    'one owner''s default privileges leaked to another owner';
            END IF;
        END
        $solution$;

        -- Exercise 4: inspect the actual definer boundary, not only its DDL.
        SELECT
            p.proname,
            pg_catalog.pg_get_function_identity_arguments(p.oid)
                AS identity_arguments,
            pg_catalog.pg_get_userbyid(p.proowner) AS owner_name,
            p.prosecdef AS security_definer,
            p.proconfig AS routine_settings,
            p.proacl AS execute_acl
        FROM pg_catalog.pg_proc AS p
        JOIN pg_catalog.pg_namespace AS n
          ON n.oid = p.pronamespace
        WHERE n.nspname = 'pro_security_lab'
        ORDER BY p.proname, identity_arguments;

        -- Exercise 5: prove each tenant sees its own row and no cross-tenant
        -- row. SET ROLE removes owner/superuser bypass from the test identity.
        SET LOCAL ROLE ds60_sec_north;
        SELECT CURRENT_USER AS active_role, d.document_id, d.tenant_key, d.title
        FROM pro_security_lab.documents AS d
        ORDER BY d.document_id;
        DO $solution$
        BEGIN
            IF (SELECT COUNT(*) FROM pro_security_lab.documents) <> 1
               OR EXISTS (
                   SELECT 1
                   FROM pro_security_lab.documents
                   WHERE tenant_key <> 'north'
               ) THEN
                RAISE EXCEPTION 'north tenant isolation failed';
            END IF;
        END
        $solution$;
        RESET ROLE;

        SET LOCAL ROLE ds60_sec_south;
        SELECT CURRENT_USER AS active_role, d.document_id, d.tenant_key, d.title
        FROM pro_security_lab.documents AS d
        ORDER BY d.document_id;
        DO $solution$
        BEGIN
            IF (SELECT COUNT(*) FROM pro_security_lab.documents) <> 1
               OR EXISTS (
                   SELECT 1
                   FROM pro_security_lab.documents
                   WHERE tenant_key <> 'south'
               ) THEN
                RAISE EXCEPTION 'south tenant isolation failed';
            END IF;
        END
        $solution$;
        RESET ROLE;

        ALTER TABLE pro_security_lab.documents FORCE ROW LEVEL SECURITY;
        SET LOCAL ROLE ds60_sec_owner;
        SELECT
            CURRENT_USER AS forced_owner_role,
            COUNT(*) AS rows_visible_after_force
        FROM pro_security_lab.documents;
        DO $solution$
        BEGIN
            IF EXISTS (SELECT 1 FROM pro_security_lab.documents) THEN
                RAISE EXCEPTION 'FORCE RLS did not constrain the table owner';
            END IF;
        END
        $solution$;
        RESET ROLE;

        SELECT
            r.rolname,
            r.rolsuper,
            r.rolbypassrls,
            CASE
                WHEN r.rolsuper OR r.rolbypassrls
                    THEN 'always bypasses RLS; never use for tenant tests'
                ELSE 'subject to RLS unless table owner without FORCE RLS'
            END AS rls_effect
        FROM pg_catalog.pg_roles AS r
        WHERE r.rolname IN (
            CURRENT_USER,
            'ds60_sec_owner',
            'ds60_sec_north',
            'ds60_sec_south'
        )
        ORDER BY r.rolname;

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
            ) AS count_function_execute,
            CASE role_name
                WHEN 'ds60_sec_auditor'
                    THEN 'owner default SELECT + direct function EXECUTE'
                ELSE 'owner default SELECT; no PUBLIC grants'
            END AS effective_source
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
        SELECT *
        FROM pro_security_lab.identity_probe();
        RESET ROLE;

        -- Exercise 8: unknown/NULL identities map to NULL, so the policy
        -- predicate is not true. A pooled-session tenant setting would need the
        -- same validation plus guaranteed reset.
        SELECT
            candidate_role,
            CASE candidate_role
                WHEN 'ds60_sec_north' THEN 'north'
                WHEN 'ds60_sec_south' THEN 'south'
                ELSE NULL
            END AS derived_tenant,
            candidate_role IN ('ds60_sec_north', 'ds60_sec_south')
                IS TRUE AS accepted_identity
        FROM (
            VALUES
                ('ds60_sec_north'::text),
                ('DS60_SEC_NORTH'::text),
                ('unknown'::text),
                (NULL::text)
        ) AS identities(candidate_role)
        ORDER BY candidate_role NULLS LAST;

        -- Exercise 9: use one coherent API-only writer model. The writer gets
        -- neither table nor identity-sequence privileges; a hardened definer
        -- API validates input and returns only its inserted north row.
        CREATE POLICY owner_north_api_read
        ON pro_security_lab.documents
        FOR SELECT
        TO ds60_sec_owner
        USING (tenant_key = 'north');

        CREATE POLICY owner_north_api_insert
        ON pro_security_lab.documents
        FOR INSERT
        TO ds60_sec_owner
        WITH CHECK (tenant_key = 'north');

        SET LOCAL ROLE ds60_sec_owner;
        CREATE FUNCTION pro_security_lab.insert_north_document(
            p_title text,
            p_body text
        )
        RETURNS TABLE (
            document_id bigint,
            tenant_key text,
            title text
        )
        LANGUAGE plpgsql
        VOLATILE
        SECURITY DEFINER
        SET search_path = pg_catalog
        AS $function$
        BEGIN
            IF p_title IS NULL OR btrim(p_title) = ''
               OR p_body IS NULL OR btrim(p_body) = '' THEN
                RAISE EXCEPTION 'title and body must not be blank'
                    USING ERRCODE = 'invalid_parameter_value';
            END IF;

            RETURN QUERY
            INSERT INTO pro_security_lab.documents AS d (
                tenant_key,
                title,
                body
            )
            VALUES ('north', p_title, p_body)
            RETURNING d.document_id, d.tenant_key, d.title;
        END
        $function$;
        REVOKE ALL
        ON FUNCTION pro_security_lab.insert_north_document(text, text)
        FROM PUBLIC;
        RESET ROLE;

        GRANT EXECUTE
        ON FUNCTION pro_security_lab.insert_north_document(text, text)
        TO ds60_sec_writer;

        DO $solution$
        BEGIN
            IF pg_catalog.has_table_privilege(
                'ds60_sec_writer',
                'pro_security_lab.documents',
                'INSERT'
            ) OR pg_catalog.has_sequence_privilege(
                'ds60_sec_writer',
                'pro_security_lab.documents_document_id_seq',
                'USAGE'
            ) THEN
                RAISE EXCEPTION
                    'API-only writer unexpectedly has direct table/sequence access';
            END IF;
        END
        $solution$;

        SET LOCAL ROLE ds60_sec_writer;
        SELECT *
        FROM pro_security_lab.insert_north_document(
            'Writer-created note',
            'Narrow insert path'
        );

        DO $solution$
        BEGIN
            BEGIN
                INSERT INTO pro_security_lab.documents (tenant_key, title, body)
                VALUES ('south', 'Cross-tenant write', 'Must fail');
                RAISE EXCEPTION 'cross-tenant writer INSERT unexpectedly succeeded';
            EXCEPTION
                WHEN insufficient_privilege THEN
                    RAISE NOTICE 'Expected writer tenant rejection: %', SQLERRM;
            END;

            BEGIN
                UPDATE pro_security_lab.documents SET title = title;
                RAISE EXCEPTION 'writer UPDATE unexpectedly succeeded';
            EXCEPTION
                WHEN insufficient_privilege THEN
                    RAISE NOTICE 'Expected writer UPDATE denial: %', SQLERRM;
            END;

            BEGIN
                DELETE FROM pro_security_lab.documents;
                RAISE EXCEPTION 'writer DELETE unexpectedly succeeded';
            EXCEPTION
                WHEN insufficient_privilege THEN
                    RAISE NOTICE 'Expected writer DELETE denial: %', SQLERRM;
            END;

            BEGIN
                PERFORM 1 FROM pro_security_lab.documents;
                RAISE EXCEPTION 'writer table read unexpectedly succeeded';
            EXCEPTION
                WHEN insufficient_privilege THEN
                    RAISE NOTICE 'Expected writer table-read denial: %', SQLERRM;
            END;
        END
        $solution$;
        RESET ROLE;

        -- Exercise 10: an executable plan matrix, not destructive cluster-wide
        -- offboarding SQL.
        SELECT *
        FROM (
            VALUES
                (1, 'fence login and terminate reviewed sessions', 'session inventory and incident owner'),
                (2, 'reassign owned objects', 'REASSIGN OWNED dry-run inventory'),
                (3, 'remove direct and inherited memberships', 'role-membership diff'),
                (4, 'remove current grants and default privileges', 'object/default ACL diff'),
                (5, 'rotate dependent credentials and APIs', 'secret-owner confirmation'),
                (6, 'verify denied access and application health', 'negative login/query plus smoke tests'),
                (7, 'retain a separate recovery administrator', 'break-glass test and audit record')
        ) AS offboarding(step_number, action, required_evidence)
        ORDER BY step_number;

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
