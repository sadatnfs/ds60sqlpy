# Delta Sharing prepared reference-server route

Delta Sharing is part of Delta Lake/Linux Foundation, not an Apache project.
The actual reference server and table store must be separately prepared and
qualified. No corresponding1.4.1 prebuilt image/tag or release package was found.
Do not call an older image latest, implement a fake server or point a file URI
at a reference server that only signs supported cloud storage paths. The portable
client is explicitly limited to basic unpartitioned Parquet protocol reader version 1. Keep
bearer tokens and signed URLs out of output/evidence. No TLS bypass, emulation,
ambient cloud resources, destructive cleanup or publication.

All generated ownership, lock and credential state stays under `.workshop/`,
which the existing starter/Docker/source policy excludes. Only fixed public
client/configuration files and the explicit read-only recipient profile are
mounted; the whole working directory is not a container source mount.
