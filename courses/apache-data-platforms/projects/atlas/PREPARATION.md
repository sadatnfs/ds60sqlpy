# Separately prepared native Atlas server

This is a preparation runbook, not a local acceptance receipt. Use a dedicated
Linux host whose CPU architecture, compatible Java 8 distribution and graph/index
components have been validated. Keep learner/shared servers outside the experiment.
The Atlas 2.5.0 release POM pins HBase2.6.4 and Solr8.11.3 and targets Java 8.
Read its exact installation instructions and build profiles before choosing an
embedded development stack or external HBase/Solr. No hook compatibility with
Hive 4.2 is inferred.

1. Download the official apache-atlas-2.5.0-sources.tar.gz and its SHA512 from
   the Apache release directory. Verify the complete archive before extracting;
   inspect path traversal, links and allowed extraction roots. Record source
   digest, native platform, JDK and Maven versions.
2. Follow the tagged InstallationInstruction.md to build the selected distribution
   and its actual graph/index backend. All compilers/downloads belong to explicit
   preparation, not lesson opening. Preserve Apache license/notice files.
3. Configure fixture-only authentication, an isolated listener, backend state
   directories, resource limits and an explicit backup procedure. Expose only the
   chosen loopback/TLS route. Do not use example admin credentials on public ports.
4. Start actual backing services and Atlas, require authenticated API readiness
   and invalid-credential rejection, then run this owned client plan/apply/check.
5. Record stable entity GUIDs and lineage before exact process stop/resume and
   replacement over retained graph/index storage. Run only check after lifecycle
   transitions. Never apply during retention readback.
6. Test graph/index backup and restore on a separate owned target, including
   direct entity reads and bounded discovery polling. A graph read does not prove
   that its search index is current. Keep original evidence if a stage fails.

If no supported native route is available, omit server execution and use the
complete payloads and chapter explanations. Prepared requests are not actual
Atlas observations. Do not solve a missing architecture by silently emulating it.

Primary sources:

- [Atlas 2.5.0 release](https://downloads.apache.org/atlas/2.5.0/)
- [Pinned installation source](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/Setup/InstallationInstruction.md)
- [Pinned build/dependencies](https://github.com/apache/atlas/blob/release-2.5.0/pom.xml)
- [Atlas v2 API](https://atlas.apache.org/api/v2/index.html)

All generated ownership, lock and credential state stays under `.workshop/`,
which the existing starter/Docker/source policy excludes. Only the fixed public
client file is mounted; the strict private environment cannot replace the owner.
The whole working directory is not a container source mount.
