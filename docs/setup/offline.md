# Prepare the classroom for offline study

The ordinary classroom can run offline after its selected images and required
lesson assets are prepared. Reading a guide, rendering its mathematics and
highlighting its code do not require a CDN. Optional model downloads, external
services, cluster setup and GPU hosts have their own requirements.

## Prepare while connected

In the course directory, choose your needed runtime set:

```sh
./classroom --starter
```

Or prepare every ordinary worker:

```sh
./classroom --all
```

These choices are remembered for the project. Run representative lessons from
the paths you intend to study and inspect their capability notices. A completed
image build is useful evidence, but a real reference attempt also exposes
missing local assets or an unprepared external dependency.

Keep the downloaded source folder, including generated readers and fixtures.
A ZIP is source delivery, not a copy of installed images or saved work.

## Return without downloads

With the same local engine running, use:

```sh
./classroom resume
```

Strict resume never builds or pulls. If an image is missing, it reports the
missing preparation rather than silently downloading it. Use normal startup
while connected to finish preparation.

After disconnecting, repeat one small Python example, one SQL query and any
specialized runtime you plan to use. Browser Live preview also works with
bundled HTML/CSS/JavaScript/D3 inputs. External scripts and network data remain
outside that preview's contract.

## Package installation and lesson assets are different

| Resource | Preparation boundary |
| --- | --- |
| Runtime/compiler packages | Built into a selected image, or obtained from a matching published Hub tag |
| Synthetic data and checked-in fixtures | Included with course sources and images |
| Pretrained weights, tokenizer files or extra datasets | Downloaded only through the specific lesson's explicit preparation route |
| Remote service or cluster | Requires a separately available and deliberately selected environment |
| NVIDIA device | Requires compatible hardware, drivers and an explicitly enabled GPU profile |

A library import does not prove that model weights or sample datasets are
cached. Some legacy notebooks offer external dataset examples or offline
fallbacks; read their requirements before disconnecting. Downloads into a
temporary worker job directory do not become durable assets automatically.
Use the preparation path and storage location declared by that lesson.

## Move prepared images to another machine

Use a supported image-transfer route deliberately:

- After the owner publishes matching tags, the destination can use
  `./classroom --from-hub PUBLISHER --tag VERSION` while connected.
- For a disconnected transfer, Docker can save local images to an archive and
  load them into another engine. Follow Docker's
  [image save](https://docs.docker.com/reference/cli/docker/image/save/) and
  [image load](https://docs.docker.com/reference/cli/docker/image/load/) commands.
  Preserve the exact required tags and architecture.

An ARM64 image is not automatically an AMD64 image. The course source ZIP,
image archive and learning-data backup solve different problems. Loading images
does not restore browser drafts or PostgreSQL tables.

See [Docker Hub distribution](../dockerhub.md) for image names and architecture
tags, and [backup and transfer](../one-command-classroom.md#backup-and-transfer)
for saved learning data. Do not include private runtime credentials or model
cache credentials in a shared archive.

## Static reading without an engine

Open `START_HERE.html` from the extracted source folder for the generated
reading library. Keep the folder structure intact so local links work.
Static readers display content; they do not execute programs or connect to a
database. Return to `./classroom` when you want the interactive workspace.

An optional AI tutor has its own connectivity requirements. The curriculum
and MCP content server do not bundle an offline language model.
