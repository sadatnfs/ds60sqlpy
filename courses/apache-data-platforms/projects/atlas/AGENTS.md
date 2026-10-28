# Atlas prepared native-server route

This directory contains a real Atlas REST client, not an Atlas replacement. No
local server image is qualified. Atlas 2.5.0 targets Java 8 and warns that Java 9+
is untested. Do not silently run the existing Java 17/21 classroom images as a
supported Atlas server. Use a separately owned compatible native host and its
actual graph/index backups. Never send credentials in command lines, receipts or
logs. Every written qualified name/type belongs to the saved random owner. No
ambient/shared production endpoint, global delete, emulation or TLS bypass.

All generated ownership, lock and credential state stays under `.workshop/`,
which the existing starter/Docker/source policy excludes. Only the fixed public
client file is mounted; the strict private environment cannot replace the owner.
The whole working directory is not a container source mount.
