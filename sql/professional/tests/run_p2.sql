-- Execute the three P2 learner/solution pairs and prove cleanup.
\set ON_ERROR_STOP on

\ir ../lessons/sql_ext_01_extensions_spatial_vector.sql
\ir ../solutions/sql_ext_01_extensions_spatial_vector_solutions.sql
\ir ../lessons/sql_repl_01_cdc_high_availability.sql
\ir ../solutions/sql_repl_01_cdc_high_availability_solutions.sql
\ir ../lessons/sql_temporal_01_domain_modelling.sql
\ir ../solutions/sql_temporal_01_domain_modelling_solutions.sql
\ir verify_cleanup.sql
