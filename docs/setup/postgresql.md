# PostgreSQL in the Docker classroom

The supported classroom starts PostgreSQL with the application. Use
`./classroom` or `./classroom --starter`; no host PostgreSQL installation,
pgAdmin setup or native Windows password file is required.

The course targets the disposable database `advanced_sql_training`. Its fresh
Docker learner login is `admin` with password `admin`. A separate bootstrap
role performs container initialization. The classroom supplies the connection
internally, so ordinary SQL source should contain no connection string.

The `admin` login cannot create roles. For the security lesson `sql-sec-01`,
`./classroom` prepares six plain NOLOGIN roles on every start (new and existing
volumes alike) and lets `admin` adopt them only with `SET ROLE`. They have no
password, login or administrative attribute, and the lesson rolls back every
object it creates as them.

A database volume created by this release also requires the course password for
every TCP connection, including loopback inside the app container, so lesson code
cannot sign in as the bootstrap administrator. Administrative maintenance uses
the PostgreSQL container's local socket, for example
`docker compose exec postgres psql -U ds60_admin -d advanced_sql_training`.

## Confirm the connection from the SQL pad

Open **PostgreSQL**, choose the first on-ramp lesson and select SQL snippet
mode when offered. Run:

```sql
SELECT
  current_database() AS database_name,
  current_user AS learner_role;
```

On a fresh default installation, expect `advanced_sql_training` and `admin`.
A deliberately configured existing course login can differ. Keep the query
result with your notes; a running container alone does not prove a query works.

## Choose the correct execution mode

| Mode | Intended artifact |
| --- | --- |
| SQL snippet | Ordinary SQL statements entered in the browser |
| Whole SQL lesson (psql) | The selected lesson script, including reviewed psql directives and relative fixture references |

Read the lesson before switching modes. A psql backslash command is not
ordinary SQL and should not be pasted into an incompatible client. Whole-script
execution preserves the course's declared transaction and include behavior;
it does not grant arbitrary access to host files.

Start with `sql-start-01`, `sql-start-02` and `sql-start-03`. Their small
temporary fixtures introduce rows, filtering and aggregation before the
numbered sequence.

## Training data and permissions

Most lessons read the course-owned `training` schema. You never load it by
hand. When you open a SQL lesson or a Python-to-PostgreSQL bridge lesson, its
**Course database** panel checks the schema, and the first run loads it if it
is missing, using the same `sql/postgres-60day/00_setup.sql` and
`00_verify.sql` scripts as the course checks. Loading only creates what is
absent; it never replaces existing data. You can also choose
**Load course tables** before running anything.

If your own changes leave the tables different from the original data, the
panel says so and offers **Reset training data**. After you confirm, it drops
and recreates only that schema; saved code, notes and run history are kept.
Resetting is not a general repair for a failed query.

Keep lesson work inside the local disposable course database. Ordinary
learner credentials do not imply permission for server administration,
extensions, replication or physical recovery. Advanced lessons identify
separate capability requirements and useful reading/default exercises.

Most exercises use transactions that roll back their changes. The warehouse
lessons, SQL Days 52 through 54, deliberately keep a `dwh` schema that Day 52
builds. Opening Day 53 or 54 first is fine: the panel offers to build that
schema, and the first run builds it automatically.

## Ports and stopping

The database listens on its container port inside the project. The launcher
publishes a separate loopback host port and can choose it automatically.
Use `./classroom status` instead of assuming the host port is 5432 or 55432.

```sh
./classroom stop
./classroom resume
```

These commands retain PostgreSQL's named data volume. A new image or container
does not replace its stored tables. Deleting the volume is a separate reset.
Changing a database password setting does not automatically rewrite an already
initialized database's roles.

## Back up the right data

SQL tables live in the database volume. Browser drafts, notes and saved query
output live in the learning volume. Back up both when you want the complete
workspace. A saved SQL receipt is useful evidence of an earlier query, but it
is not a database backup.

Follow [the classroom export procedure](../docker-classroom.md#5-export-learning-work-and-the-database)
and use a deliberate restore target. Never restore over unrelated data.
Keep the same project name when identifying volumes and containers.

## Optional notebook work

A separately prepared contributor environment can use
[the guided PostgreSQL notebook workflow](jupyter-postgresql.md). That is an
explicit alternative for notebook work, not an additional setup requirement
for the Docker browser. Windows contributors use WSL 2 for the Linux tooling.
