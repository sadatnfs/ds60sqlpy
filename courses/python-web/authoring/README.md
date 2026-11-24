# Python web authoring sources

`units.json` owns stable pyweb lesson IDs, prerequisites, observable outcomes,
framework labels, stages, runtime surfaces and primary references. Chapters and
complete finite programs live in `chapters/` and `programs/`. The subject generator
publishes guides, examples and manifests only after every unit has substantive
prose, two worked cases and its full source. Each unit's `key_terms` object holds 3
to 5 lesson-specific terms with one-sentence definitions; the generator validates
them and renders a Key terms section after the guide's starting-point section.
Each unit's `worked_examples` list holds at least one object with a `title`,
`code` (a list of Python source lines that must parse), an optional `output` (the
exact stdout lines, rendered as an expected-output block) and an `interpretation`
of at least 40 words that explains what the result shows in that lesson. Titles
must be unique within a lesson and code must not repeat across lessons. Snippets
are small, runnable and consistent with the lesson's program; when the lesson's
framework is not needed to show the point, prefer the standard library or a
lighter equivalent and say which framework behavior it mirrors. The generator
renders them as Worked example sections after the last worked case.
Run `python authoring/build.py`, then its `--check` mode, from the course directory.

The intended route has shared HTTP/browser foundations followed by independently
navigable Flask, FastAPI and Django branches, then cross-framework engineering
and owned deployment projects. Counts describe chapters, not a daily schedule.
Preserve the original Python and SQL lesson IDs and progress.

Ordinary source executes through real framework test clients in the prepared
python-web worker and exits. Larger service examples have explicit project
ownership, startup, data lifecycle, runtime and acceptance contracts. Do not
promote a test-client result into a TCP/browser or production-deployment claim.

Keep tutorial mode, complete worked answers, meaningful failure diagnosis and
answered discussions. Write exact mathematics with explicit TeX delimiters and
accurate code-fence languages. Root owns shared profile/image admission, reader
and TeX generation and release synchronization. No em dashes.

The complete course has `admitted: true`. Generation writes the maintained
`track.json` and `lessons.json`; the former draft manifests have been removed
after qualification. Future edits preserve these admitted IDs and saved state.
Keep new incomplete proposals outside the admitted registry until their source,
runtime and integration contracts are complete.

The 69 finite programs can be exercised with the explicitly prepared interpreter
through `tests/test_python_web_curriculum.py` by setting
`DS60_PYTHON_WEB_INTERPRETER`. Missing that interpreter produces explicit skips,
not successful runtime evidence. Native worker acceptance and the owned
`projects/web-lab/check_api.py` and `check_browser.py` remain separate gates.
