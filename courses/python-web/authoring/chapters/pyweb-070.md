## Starting point and result

A Docker image contains prepared code and dependencies, while a running container has a process lifecycle and external storage holds durable data. This chapter uses the owned web lab to distinguish those layers through stop, exact resume and application-container replacement. No step rebuilds an image merely to recover a stopped service.

## Mechanism: separate preparation, migration and serving

The workshop prepare action builds a small source/static-assets layer from an already prepared python-web image. It saves the selected project, image references and ports. The start action uses those local images, starts PostgreSQL, applies the reviewed migrations and synthetic fixture preparation, then starts the three web servers and worker.

Resume starts the exact existing five containers and checks their identities. It does not pull, build, rerun migrations or change projects. Replace deliberately recreates the application and worker containers from the saved image while retaining the database service and volume. These operations serve different purposes and should not be hidden behind one ambiguous restart command.

PostgreSQL data lives in a named volume labeled for this owned project. Private settings, signing material and acceptance receipts live in .workshop. Neither is stored in a disposable application image layer. A Git clone supplies source, not the learner's database or session state.

## Worked case: stop and resume the same containers

Run workshop check once to create source-bound synthetic notes and a completed job. Stop the owned services, resume them and run verify. Verify reads the exact identifiers saved by the earlier acceptance rather than creating replacement records.

The result answers two questions separately: did the launcher retain container identity, and did the application retrieve the earlier data? A server can restart successfully while pointing to an empty database, so process readiness alone is insufficient evidence of retained state.

Startup ordering matters. PostgreSQL must become ready before dependent processes resume meaningful work. A worker that exits immediately because the database is still starting can leave an apparently running UI with no job progress. The launcher waits for the database and the service acceptance checks actual operations.

## Worked case: replace application containers and read prior records

The replace action creates new app/worker containers from the saved image, then verify reads the same prior note and job records. This demonstrates that durable data belongs outside those containers. It also exercises Django's prepared static assets and the server configuration carried by the image.

The workshop does not delete the PostgreSQL volume or private settings. Using down with volume removal, switching project names or pruning state would invalidate the recovery claim. Export evidence before cleaning only explicitly owned synthetic resources, and keep learner data unless the learner deliberately requests deletion.

A newer application image may require a migration or compatibility review. Replacing containers is not permission to apply an arbitrary incompatible schema change. Preserve immutable released images and qualify the new source/version through the repository's release process.

## Failure diagnosis and discussion

**Why does copying only the source folder not copy progress?** Database contents and private runtime state are intentionally outside source packaging. Back up and restore those through their documented storage boundaries.

**Why is a healthy process not enough?** A health check can succeed while a principal workflow fails because of schema, authorization, assets or worker state. Actual acceptance and retained-record readback establish broader behavior.

If resume tries to build, inspect the invoked action and saved selection. If records disappear, inspect project name, volume attachment and database target before rerunning creation. If static assets fail, inspect collectstatic preparation and local delivery. Continue with integration tests and the final review to map each operational claim to its evidence.
