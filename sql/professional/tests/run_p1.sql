-- Execute the six P1 learner/solution pairs and prove cleanup.
\set ON_ERROR_STOP on

\ir ../lessons/sql_prog_01_routines_triggers.sql
\ir ../solutions/sql_prog_01_routines_triggers_solutions.sql
\ir ../lessons/sql_types_01_native_types_search.sql
\ir ../solutions/sql_types_01_native_types_search_solutions.sql
\ir ../lessons/sql_ops_01_indexes_statistics_maintenance.sql
\ir ../solutions/sql_ops_01_indexes_statistics_maintenance_solutions.sql
\ir ../lessons/sql_test_01_contracts_migrations.sql
\ir ../solutions/sql_test_01_contracts_migrations_solutions.sql
\ir ../lessons/sql_analytics_01_query_patterns.sql
\ir ../solutions/sql_analytics_01_query_patterns_solutions.sql
\ir ../lessons/sql_ops_02_backup_restore_recovery.sql
\ir ../solutions/sql_ops_02_backup_restore_recovery_solutions.sql
\ir verify_cleanup.sql

