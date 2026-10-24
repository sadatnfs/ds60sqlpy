# Docker: from the first container to a recoverable application

Run `./classroom` from the repository root and choose Docker in the unified
subject directory. All 42 lessons include a detailed guide, two worked examples,
six progressive evidence tasks, an answer-free worksheet and separate solutions.
The classroom saves reading notes and progress. It does not execute Docker
engine commands or receive a Docker socket.

Start with [containers, images and processes](guides/docker-001.md). Follow the
beginner sequence through a visible local build, loopback browser request and
volume-preserving replacement. Continue into BuildKit, multi-stage and
multi-platform builds, networking, permissions, backup/restore, resource limits,
security, registries, supply-chain evidence, CI, operations and architecture.

The [maintained compose-lab project](fixtures/compose-lab/README.md) is a small
standard-library Python app with health, public message and persistent counter
endpoints. Copy it into a new learner directory before optional host practice.
Its README gives exact commands, expected observations, a peer-network check,
independent restore experiment and cleanup scoped to that disposable project.
The first build needs the base image; prepared runs stay local and never push.
Use Bash on Linux/macOS or Ubuntu inside WSL 2 on Windows.

## Lesson route

| Lesson | Topic | Stage |
| --- | --- | --- |
| [docker-001](guides/docker-001.md) | Containers, images and the process model | beginner |
| [docker-002](guides/docker-002.md) | The Linux engine, WSL 2 and your first inspection | beginner |
| [docker-003](guides/docker-003.md) | The filesystem, writable layers and container lifetime | beginner |
| [docker-004](guides/docker-004.md) | Processes, PID 1, signals and graceful shutdown | beginner |
| [docker-005](guides/docker-005.md) | Dockerfile instructions and the first reproducible image | beginner |
| [docker-006](guides/docker-006.md) | Build context, .dockerignore and accidental data exposure | beginner |
| [docker-007](guides/docker-007.md) | Layers, cache invalidation and efficient rebuilds | beginner |
| [docker-008](guides/docker-008.md) | Environment variables, command arguments and configuration | beginner |
| [docker-009](guides/docker-009.md) | Ports, loopback and the first browser request | beginner |
| [docker-010](guides/docker-010.md) | Logs, exit status and observation before repair | beginner |
| [docker-011](guides/docker-011.md) | Compose services, projects and a complete application | beginner |
| [docker-012](guides/docker-012.md) | Health checks, startup order and real readiness | beginner |
| [docker-013](guides/docker-013.md) | Named volumes, bind mounts and persistence experiments | beginner |
| [docker-014](guides/docker-014.md) | First capstone: build, serve, replace and explain | beginner |
| [docker-015](guides/docker-015.md) | BuildKit, cache mounts and build secrets | intermediate |
| [docker-016](guides/docker-016.md) | Multi-stage builds and runtime dependency boundaries | intermediate |
| [docker-017](guides/docker-017.md) | CPU architectures, image indexes and cross-platform builds | intermediate |
| [docker-018](guides/docker-018.md) | Bridge networks, service DNS and container-to-container traffic | intermediate |
| [docker-019](guides/docker-019.md) | Network isolation, gateways and outbound connectivity | intermediate |
| [docker-020](guides/docker-020.md) | Users, UID ownership and writable data paths | intermediate |
| [docker-021](guides/docker-021.md) | Backups, restores and proving data recovery | intermediate |
| [docker-022](guides/docker-022.md) | Resource limits, contention and honest performance experiments | intermediate |
| [docker-023](guides/docker-023.md) | Read-only filesystems, capabilities and least privilege | intermediate |
| [docker-024](guides/docker-024.md) | Rootless engines, user namespaces and host trust | intermediate |
| [docker-025](guides/docker-025.md) | Image names, digests and an offline transfer | intermediate |
| [docker-026](guides/docker-026.md) | Compose overrides, profiles and configuration review | intermediate |
| [docker-027](guides/docker-027.md) | Intermediate capstone: a recoverable two-tier teaching system | intermediate |
| [docker-028](guides/docker-028.md) | Registries, tags, digests and deliberate publication | intermediate |
| [docker-029](guides/docker-029.md) | Software bills of materials and image provenance | advanced |
| [docker-030](guides/docker-030.md) | Vulnerability findings, patching and dependency updates | advanced |
| [docker-031](guides/docker-031.md) | CI builds, test layers and artifact promotion | advanced |
| [docker-032](guides/docker-032.md) | Debugging minimal images without changing the contract | advanced |
| [docker-033](guides/docker-033.md) | Restart policies, failure loops and idempotent startup | advanced |
| [docker-034](guides/docker-034.md) | Application migrations and durable state versioning | advanced |
| [docker-035](guides/docker-035.md) | Image size, startup latency and measurement | advanced |
| [docker-036](guides/docker-036.md) | Compose on one host and the limits of orchestration | advanced |
| [docker-037](guides/docker-037.md) | TLS, reverse proxies and publishing responsibly | advanced |
| [docker-038](guides/docker-038.md) | Incident response, disk pressure and scoped cleanup | advanced |
| [docker-039](guides/docker-039.md) | Namespaces, cgroups, OCI and the runtime beneath Docker | advanced |
| [docker-040](guides/docker-040.md) | Runtime secrets, configuration files and controlled disclosure | advanced |
| [docker-041](guides/docker-041.md) | Scaling replicas, shared state and concurrency traps | advanced |
| [docker-042](guides/docker-042.md) | Advanced capstone: a release, recovery and teaching handoff | advanced |

## Evidence and authoring

A parsed Compose file, a successful image build, an actual HTTP response and a
verified restore are different observations. Record what you actually performed.
The fixture inventory lists intended cases and does not manufacture runtime
acceptance. Its process-local counter lock is intentionally not a replicated
database design; the scaling chapter explains that limit.

[Authoring instructions](authoring/README.md) describe regeneration from the
original chapter specifications. Preserve stable IDs, host ownership and named
volumes. The course never uses a global prune as routine learner cleanup.
