# Scientific visualization in Python and JavaScript

Read the root guidance and content contract. This is a paired practice subject:
Python is canonical and JavaScript browser variants teach the same scientific
objectives. Preserve viz-NNN identities, variant namespaces and saved state.
Use only prepared Plotly packages and the browser's bundled window.Plotly.
Never fetch data, import a CDN, require Dash or start a server in a lesson.

The durable numerical sources live in authoring/python_cases.py and
authoring/browser_cases.js. Directly authored guides and explanatory solutions
must explain vocabulary, mechanisms, two contrasting worked cases, six concrete
practice tasks with hints, expected evidence, diagnosis and next steps.
The statistics book remains a separate tutorial with all answers visible.

Every chart needs a descriptive caption, units, noncolor distinctions and an
accessible data table or equivalent readable values. Python figures include
layout.meta.description and a primitive-cell table for the shared capture UI;
browser references create a native semantic table themselves. Treat source,
numerical checks, renderer execution, interaction and accessibility as distinct
evidence. Do not assert that a chart's appearance proves statistical validity.

Keep examples deterministic, offline, bounded and self-contained. Default
examples use SVG Cartesian traces, at most two figures, and less than 200 KiB
per serialized figure. No map tiles, external images, model downloads, arbitrary
HTML or embedded executable callbacks belong in Python figure metadata.
Browser listeners must be bounded and cleaned up when the preview leaves.
Do not use em dashes. Root owns shared renderer, profile and asset integration.
