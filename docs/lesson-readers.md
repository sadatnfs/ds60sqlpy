# Reading lessons in the classroom and offline

Use `./classroom` for every subject, guide, coding or reading workspace, notes
and saved work. Generated `START_HERE.html` and reader pages provide a portable
reading library when the server is not running.

## What gets rendered

Legacy Python, SQL and bridge entries have pages under `lesson-pages/`. Module
guides, source listings and linked documentation have deterministic pages under
`reference-pages/`. Loaders and manifests determine this inventory.

Markdown becomes semantic HTML; notebook cells become read-only previews; source
files become escaped, highlighted listings. Even an HTML lesson is shown as source
in a reader. It executes only in the explicit browser preview. Building or opening
a reader never executes code or notebook outputs.

Explicit TeX is compiled during the build into offline KaTeX HTML and accessible
MathML. Prose uses bundled Latin Modern fonts. Display equations have sequence
numbers and an expandable TeX source view. Syntax highlighting is local, and
copying code preserves its characters. See [textbook rendering](textbook-rendering.md). Maintainer-only Markdown HTML comments
are omitted while code comments remain escaped text. Unsafe URL schemes and source
outside the repository are rejected.

## Reading and saved-work boundaries

| Surface | Capability | Storage |
| --- | --- | --- |
| Docker classroom | All subjects, actual readiness, pads, notes and durable results | Project learning volume |
| Static dashboard/readers | Offline explanations, source previews and reading navigation | Browser-local preferences/markers where supported |

Static pages cannot start compilers, PostgreSQL or arbitrary native programs.
They show source paths for a deliberately prepared editor. They do not synchronize
browser-local markers with Docker volumes. Use the classroom for server-backed
progress and [backup instructions](docker-classroom.md) for complete workspaces.

The historical `/learn`, `/journeys` and `/journey-preview` URLs remain aliases
of `/classroom`. There is one application interface. The former prototype and
native editor-launch bridge have been removed.

## Tutoring and solutions

Practice guides include an optional **Ask an AI tutor about this lesson** prompt.
The authored guide owns its ID, paths, prerequisites and teaching context. The depth
audit rejects missing practice prompts. Read and attempt practice before comparing
solutions, unless you explicitly want a worked answer. Tutorial books expose their
examples directly without exams or hidden answers. See [AI tutoring](learning-with-an-ai-tutor.md).

## Maintain the readers

Edit durable subject sources, then regenerate shared views in a prepared environment:

```sh
make generate
uv run --no-sync python scripts/build_course_guide.py --check
uv run --no-sync python scripts/build_lesson_readers.py --check
uv run --no-sync python scripts/compile_lesson_tex.py --check
uv run --no-sync python scripts/check_content_rendering.py
uv run --no-sync python scripts/check_published_links.py
```

`make generate` does not run every subject authoring pipeline. Follow the subject's
`authoring/README.md` first. Never hand-edit generated readers. Their generator
rewrites local links and removes only stale HTML inside its owned output directories.
Keep these outputs in source archives so reading remains available offline.
