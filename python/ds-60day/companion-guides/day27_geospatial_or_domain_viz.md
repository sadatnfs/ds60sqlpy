# Day 27: Geospatial or Domain-Specific Visualization

**Level:** Intermediate

Geospatial work adds coordinate reference systems and map layers. The offline
alternative uses NetworkX to visualize a domain relationship graph.

## Learning objectives

By the end of this lesson, you can:

- explain geometry columns and coordinate reference systems (CRS);
- build an offline GeoDataFrame from known coordinates;
- reproject data only when source CRS is known;
- distinguish data layers from network-fetched basemap tiles;
- create a deterministic network graph when map dependencies/data are absent.

## Prerequisites

Complete Day 26 (`python-26`). This optional lesson uses the `geo` dependency
group (`geopandas`, `geodatasets`, `contextily`, and `networkx`).

Prepare the declared `geo` group only if the selected example needs it.
For a local Docker build, retain any other package groups you need and rebuild
the app/Core image deliberately; see [runtime profiles](../../../docs/docker-profiles.md):

```bash
DS60_DOCKER_PROFILES=geo ./classroom --starter --local-build --rebuild
```

For an optional contributor notebook, first follow
[CONTRIBUTING](../../../CONTRIBUTING.md), then retain the Core extras and add
`geo` in that host environment. Run from the repository root in Bash on
Linux/macOS or Windows WSL 2:

```bash
uv sync --frozen --extra notebooks --extra data --extra bridge --extra quality --extra professional --extra sql-notebooks --extra geo
```

The host sync does not modify Docker workers. Dataset or basemap downloads
remain separately disclosed by the example; installing a package does not cache
its external data. Keep the lesson's offline fallback available.

<!-- BEGIN HOW TO RUN -->
## How to run this lesson

**Primary browser route:** run `./classroom` from the repository root and
choose **Python and data science** on `/classroom`. Open this lesson in the
shared workspace, read its capability notice and use its supported coding or
reading workflow. The [classroom guide](../../../docs/classroom-experience.md)
explains saved work, runtimes and switching subjects. No host notebook setup
is needed for this route.

### Optional contributor notebook route

Use a separately prepared POSIX environment on Linux/macOS or Ubuntu in
Windows WSL 2. Complete [contributor setup](../../../CONTRIBUTING.md) once,
including the notebook and data dependencies. Docker's Python worker does not
install packages into this host interpreter. Run the following commands from
the repository root using that prepared environment.

1. Check the interpreter and register its notebook kernel. Registration is
   needed once for this environment, or again after moving/replacing it:

   ```bash
   uv run --no-sync python scripts/course.py doctor --no-database
   uv run --no-sync python -m ipykernel install --user --name ds60sqlpy --display-name "Python (ds60sqlpy)"
   ```

   `--no-database` keeps this Python setup check local and does not require
   PostgreSQL. Do not install packages with `%pip` in a lesson. Use the
   declared dependency group when an optional import needs preparation.
2. Read `python/ds-60day/companion-guides/day27_geospatial_or_domain_viz.md`, then launch the notebook directory:

   ```bash
   uv run --no-sync python -m jupyter lab python/ds-60day/notebooks
   ```

   Open `python/ds-60day/notebooks/day27_geospatial_or_domain_viz.ipynb` and select **Python (ds60sqlpy)**. The friendly name alone
   is insufficient if you use several checkouts: confirm that the kernel's
   `sys.executable` points to this checkout's `.venv/bin/python`.
   [VS Code guidance](../../../docs/vscode.md) explains the alternative editor
   route; Windows users open that editor in WSL with the same Linux environment.
3. Restart the kernel and run cells from the top. Notebook cells share kernel
   state; each browser Run starts a fresh process. Before every example,
   predict its result, then compare the actual value, type, shape or side effect.
4. Attempt the numbered exercises in your own work cells and keep a backup of
   your notebook edits. Follow each example's file and working-directory
   instructions. Keep `solutions/` separate until you want reference comparison.

Notebook files and contributor CLI progress belong to this host checkout.
They are separate from the browser's saved pads, notes and progress in Docker
volumes. Neither route automatically copies attempts or completion markers to
the other; record progress in the interface you actually used.

**Lesson outcome:** use day 27; geospatial or domain-specific visualization to practice geospatial semantics, coordinate reference systems, valid geometry, and offline fallback
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive: build the idea before the syntax

### Start with one mental picture

Geospatial data combines ordinary attributes with geometry and a
coordinate reference system (CRS). A coordinate pair is conventionally
`(x, y)`, longitude then latitude for geographic coordinates. Values can
look numerically valid while being semantically swapped, so record
source order and bounds.

A CRS defines what coordinates mean and their units. Layers cannot be
overlaid or spatially joined honestly until their CRSs are known and
compatible. Reprojection transforms coordinates; assigning a CRS merely
labels existing coordinates and is not a substitute. Inspect validity,
emptiness, bounds, provenance, and offline availability before plotting.

### Vocabulary in plain language

- **geometry:** a spatial object such as point, line, or polygon.
- **CRS:** coordinate reference system defining coordinate meaning and units.
- **reprojection:** transforming geometry coordinates from one CRS to another.
- **longitude:** east-west angular coordinate, used as x in geographic pairs.
- **latitude:** north-south angular coordinate, used as y in geographic pairs.
- **spatial join:** matching records by a geometric relationship such as within or intersects.

### Syntax anatomy

`GeoDataFrame(data, geometry=..., crs="EPSG:4326")` declares that the
supplied longitude/latitude coordinates already use WGS 84.
`.to_crs("EPSG:3857")` transforms them to Web Mercator meters. In
contrast, `.set_crs(...)` labels coordinates without moving them and
should be used only when the original CRS is known but missing.

### Worked example 1: Create known geographic points and inspect bounds

Constructed geometry avoids any network or external file. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
import geopandas as gpd
from shapely.geometry import Point

places = gpd.GeoDataFrame(
    {"name": ["A", "B"]},
    geometry=[Point(-122.4, 37.8), Point(-73.9, 40.7)],
    crs="EPSG:4326",
)
(str(places.crs), places.total_bounds.round(1).tolist())
```

**Expected observation**

```text
The CRS is WGS 84/EPSG:4326 and bounds are approximately `[-122.4, 37.8, -73.9, 40.7]` in longitude/latitude degrees.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2: Reproject rather than relabel

Projected coordinates use different units while representing the same places. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
projected = places.to_crs("EPSG:3857")
{
    "same_rows": len(projected) == len(places),
    "projected_crs": str(projected.crs),
    "x_units_are_not_degrees": abs(projected.geometry.x.iloc[0]) > 1_000,
}
```

**Expected observation**

```text
All checks are true; the coordinates are transformed to meter-like Web Mercator values.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Inspect `.crs`, geometry types, `.is_valid`, `.is_empty`, and `.total_bounds` before plotting.
2. Verify coordinate order with known places or realistic bounds.
3. Use `.to_crs` to transform; use `.set_crs` only to label coordinates whose source CRS is known.
4. Keep an offline analytical layer or domain-graph alternative when basemap data is unavailable.

### Practice ramp

Work through the numbered exercises in five modes rather than treating all
of them as blank-code prompts:

1. **Prediction:** state the value, type, shape, rows, or side effect before
   execution.
2. **Guided modification:** change one part of a worked example and explain
   which part of the result must change.
3. **Independent application:** implement the same idea with a new input and
   an explicit contract.
4. **Debugging and edge cases:** reproduce a failure, identify the violated
   assumption, and prove the repair at a boundary.
5. **Retrieval:** close the guide and explain the core model from memory
   before moving on.

**Useful alternative:** When location is not central or source geometry is unavailable, a deterministic domain/network visualization can teach graph structure without a misleading map.

**Boundary to remember:** Missing CRS, invalid/self-intersecting geometry, dateline crossing, swapped axes, empty geometry, and remote basemap failure need policy.
<!-- END BEGINNER DEEP DIVE -->

## Vocabulary and mental model

- **Geometry:** point, line, or polygon associated with a row.
- **CRS:** rules translating coordinates to locations on Earth.
- **EPSG code:** identifier for a defined CRS, such as longitude/latitude
  `EPSG:4326`.
- **Projection:** transformation from Earth's surface to a planar map.
- **Basemap tile:** background image usually fetched from a web service.
- **Graph:** nodes connected by edges; a domain visualization, not necessarily
  geographic.

Coordinates without a known CRS are numbers, not trustworthy locations.

## Worked example

```python
import geopandas as gpd
import pandas as pd

cities = pd.DataFrame(
    {
        "city": ["San Francisco", "New York"],
        "longitude": [-122.4194, -74.0060],
        "latitude": [37.7749, 40.7128],
    }
)
points = gpd.GeoDataFrame(
    cities,
    geometry=gpd.points_from_xy(cities["longitude"], cities["latitude"]),
    crs="EPSG:4326",
)
ax = points.plot(figsize=(7, 4), column="city", legend=True)
ax.set(title="Example city coordinates", xlabel="Longitude", ylabel="Latitude")
```

This example is deterministic and makes no network request. It shows points,
not city boundaries.

## Download/cache note

The notebook's `geodatasets.get_path(...)` example downloads and caches Natural
Earth data on first use. `contextily` basemaps also require tile-network access
unless separately cached. Prime approved caches while online, use a local
GeoJSON file, or choose the NetworkX exercise for fully offline work.

## Exercises and progressive hints

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Using only a local or already-cached boundary/point source, create a GeoDataFrame plot. **Before plotting:** record provenance/license, CRS, geometry types, invalid/empty counts, and bounds. **Constraints:** transform all layers to one appropriate CRS and never use `set_crs` as if it reprojected coordinates.
   **Verify:** check a known location/bounds and confirm entity count survives reprojection.

2. Alternatively, construct a deterministic NetworkX domain graph where node and edge meanings are written explicitly. **Constraints:** use a fixed layout seed, encode at most a few meaningful attributes, provide labels/legend, and do not require network data.
   **Verify:** reconcile plotted node/edge counts to the graph and explain what spatial questions this fallback cannot answer.

### Additional mastery practice

Treat coordinate reference system, coordinate order, source provenance, geometry validity, and network/cache behavior as part of the visualization.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict what goes wrong when latitude/longitude degrees are overlaid on a web map measured in Web Mercator meters.
   **Progressive hint:** Layers must use compatible coordinate reference systems (CRSs).
   **Verify:** Compare both CRS/bounds, then assert reprojection makes units compatible and the transformed layers overlap in a plausible extent.
4. **Tracing:** Trace one point represented as `(longitude, latitude)` and explain why swapping values can still create a valid but wrong location.
   **Progressive hint:** Both numbers may fall in legal ranges, so semantic order matters.
   **Verify:** Validate the known longitude/latitude pair against real bounds, swap it, and show why semantic checks, not only numeric ranges, detect the wrong location.
5. **Implementation:** Implement a longitude/latitude bounding-box validator with clear ordering and range checks.
   **Progressive hint:** Require west ≤ east, south ≤ north, and geographic bounds.
   **Verify:** Assert a valid box passes and separately reject west>east, south>north, longitude outside ±180, and latitude outside ±90.
6. **Debugging:** Repair a spatial join or overlay attempted before CRS comparison and reprojection.
   **Progressive hint:** Inspect `.crs`; transform one layer to the other's CRS.
   **Verify:** Show the pre-reprojection CRS mismatch, transform one layer, and assert the operation now uses equal CRS while preserving row identities.
7. **Edge case and explanation:** Define fallback behavior for missing/invalid geometry or unavailable map data, including an offline domain-graph alternative.
   **Progressive hint:** A missing basemap should not erase the analytical data layer.
   **Verify:** Feed missing/invalid geometry and unavailable basemap fixtures; assert analytical records remain represented by the documented local layer or graph fallback.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.

## Self-check

- Why is assigning a CRS different from reprojecting?
- Which CRS is appropriate for longitude/latitude input?
- Why can a basemap fail while local geometries still plot?
- What real-world concepts do the nodes and edges in your alternative mean?

Expected behavior: layers align in a common CRS or the graph layout is
repeatable, and offline/network requirements are explicit.

## Common pitfalls and diagnosis

- **Features appear in the wrong location:** inspect CRS and coordinate order;
  longitude is x, latitude is y.
- **Layers do not align:** reproject from correctly assigned source CRSs to one
  common CRS.
- **Basemap fails offline:** omit the basemap; cached vector data can still be
  plotted.
- **Geo packages fail to import:** rerun the advanced setup and verify the
  notebook uses the `.venv` kernel.
- **Network graph changes every run:** supply a fixed seed to stochastic layout
  algorithms.

## Continue

- [Open the learner notebook](../notebooks/day27_geospatial_or_domain_viz.ipynb)
- [Check the separate solution](../solutions/day27_geospatial_or_domain_viz/day27_solutions.md)
- [Next: Day 28; Feature engineering](day28_feature_engineering.md)

## Ask an AI tutor about this lesson

AI coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-27`
(Day 27 — Geospatial or Domain-Specific Visualization). Direct catalog prerequisites: `python-26`.
I have completed the direct prerequisites: `python-26`. Emphasize geospatial semantics, coordinate reference systems, valid geometry, and offline fallback.
Read `python/ds-60day/companion-guides/day27_geospatial_or_domain_viz.md` and use the learner notebook
`python/ds-60day/notebooks/day27_geospatial_or_domain_viz.ipynb`. Do not open or quote anything under `solutions/` unless
I explicitly ask after making an honest attempt. Use these visible phases:
Explain, Predict, Attempt, Hint, Evidence, and Retrieval. First explain one
concept in plain language, then ask me to predict a small example and wait
for my attempt. Give only one progressive hint at a time. Help me run or
inspect my actual notebook evidence, adapt commands to my operating system,
and do not treat the rendered HTML preview as executable. Finish with 2-3
retrieval questions and one next step. Done when I can explain the mental
model without the guide, complete one independent exercise, and show the
prompt's verification evidence from my notebook.
```
