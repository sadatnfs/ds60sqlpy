# Tutorial source ownership

`units.json` owns stable IDs, prerequisites and runtime contracts. `chapters/` owns original teaching prose; `programs/` owns complete executable examples. Edit those sources, then run `python courses/applied-science/authoring/build.py` and its `--check` mode. The builder does not execute code. Guides embed the exact complete program, and every admitted source is standalone.

Do not edit generated guides, examples, track.json, lessons.json or the course README directly. Preserve existing IDs and program/data meaning when formatting. Keep all answers visible in tutorial mode. Independent numerical and runtime checks remain separate from generated-byte checks. Shared TeX/readers and runtime registration belong to the integration owner.
