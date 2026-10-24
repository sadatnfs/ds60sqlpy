-- Read-only postcondition for professional SQL modules.
\set ON_ERROR_STOP on

DO $cleanup_check$
DECLARE
    remaining_schemas text;
    remaining_roles text;
BEGIN
    SELECT string_agg(n.nspname, ', ' ORDER BY n.nspname)
    INTO remaining_schemas
    FROM pg_catalog.pg_namespace AS n
    WHERE n.nspname IN (
        'pro_relational_lab',
        'pro_migration_lab',
        'pro_security_lab',
        'pro_routines_lab',
        'pro_types_lab',
        'pro_ops_lab',
        'pro_contract_test_lab',
        'pro_analytics_lab',
        'pro_recovery_lab',
        'pro_extensions_lab',
        'pro_replication_lab',
        'pro_temporal_lab'
    );

    IF remaining_schemas IS NOT NULL THEN
        RAISE EXCEPTION
            'professional SQL schemas remain after tests: %',
            remaining_schemas;
    END IF;

    SELECT string_agg(r.rolname, ', ' ORDER BY r.rolname)
    INTO remaining_roles
    FROM pg_catalog.pg_roles AS r
    WHERE r.rolname LIKE 'ds60_sec_%';

    IF remaining_roles IS NOT NULL THEN
        RAISE EXCEPTION
            'professional SQL roles remain after tests: %',
            remaining_roles;
    END IF;
END
$cleanup_check$;

\echo 'Professional SQL cleanup verification passed'
