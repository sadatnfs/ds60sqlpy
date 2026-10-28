# Actual reference-server preparation, separate from client execution

This route uses the Delta Sharing reference server from the Delta Lake/Linux
Foundation ecosystem. It is not an Apache Software Foundation server. The
selected1.4.1 GitHub release exposes source archives but no prebuilt server asset,
and its corresponding Docker registry tag was absent during inspection. Do not
substitute0.8.0or label it1.4.1. No local1.4.1server acceptance is claimed.

Use an explicitly owned native Linux host with Docker, compatible JVM/Scala/sbt
preparation and a disposable supported object-store path. The reference server's
CloudFileSigner supports its documented S3/Azure/GCS paths. A local file URI is
not an interchangeable signed HTTP object path. Do not implement an unrelated
Python file server and call that the reference server.

1. Resolve the officialv1.4.1tag to its immutable source revision. Download its
   complete source archive over verified TLS, retain its digest and license/notice.
   Pin build.sbt, project/build.properties and build plugins. The tag requests
   sbt 1.9.9 and server Scala/JVM packaging.
2. Build inside a native Docker JVM toolchain using the tagged documented
   `build/sbt server/universal:packageBin` operation. Record native architecture,
   JDK, toolchain and dependency resolution. Compilation is not protocol acceptance.
   Provide enough disk for source, dependency cache and packaged output.
3. Prepare a three-order Delta table at version 0using a compatible actual writer
   on a disposable supported object store. Retain transaction log, schema and
   data identities. Configure server-config.example.yaml in an untracked copy,
   including fixture-only bearer authorization and storage credentials.
4. Start the actual packaged Scala server behind a loopback/TLS proxy with
   bounded CPU/memory and retained configuration/table storage. Authenticate list,
   metadata and version-pinned query operations, then read actual signed data files.
5. Use this Docker-contained portable client for basic unpartitioned Parquet protocol reader
   version 1 only. Current official Python 1.4.2requires a native Rust wrapper without
   a published LinuxARM64wheel at inspection. Its advancedDelta/CDFfeatures are
   omitted from this portable route. Released pure-Python 1.0.5is a separately
   preparable official basic-client option, with its own dependency lock and tests.
6. Compare the same source table/version and actual rows before exact stop/resume
   and server replacement. Do not rewrite the table during readback. Test invalid
   recipient, server outage and a missing file on a separate copied fixture.
   Export receipts without bearer tokens or signed query strings.

Primary sources:

- [Tagged reference server and build instructions](https://github.com/delta-io/delta-sharing/tree/v1.4.1)
- [Tagged protocol](https://github.com/delta-io/delta-sharing/blob/v1.4.1/PROTOCOL.md)
- [Cloud signing implementation](https://github.com/delta-io/delta-sharing/blob/v1.4.1/server/src/main/scala/io/delta/sharing/server/common/CloudFileSigner.scala)
- [Pinned build](https://github.com/delta-io/delta-sharing/blob/v1.4.1/build.sbt)

All generated ownership, lock and credential state stays under `.workshop/`,
which the existing starter/Docker/source policy excludes. Only fixed public
client/configuration files and the explicit read-only recipient profile are
mounted; the whole working directory is not a container source mount.
