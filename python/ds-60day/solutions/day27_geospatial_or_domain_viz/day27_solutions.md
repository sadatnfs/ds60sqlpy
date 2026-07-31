# Day 27 — Solutions: Geospatial or Domain-specific Visualization

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**geospatial semantics, coordinate reference systems, valid geometry, and offline fallback**.

Geospatial data combines ordinary attributes with geometry and a
coordinate reference system (CRS). A coordinate pair is conventionally
`(x, y)`—longitude then latitude for geographic coordinates. Values can
look numerically valid while being semantically swapped, so record
source order and bounds.

A CRS defines what coordinates mean and their units. Layers cannot be
overlaid or spatially joined honestly until their CRSs are known and
compatible. Reprojection transforms coordinates; assigning a CRS merely
labels existing coordinates and is not a substitute. Inspect validity,
emptiness, bounds, provenance, and offline availability before plotting.

### Vocabulary used in the worked answers

- **geometry:** a spatial object such as point, line, or polygon.
- **CRS:** coordinate reference system defining coordinate meaning and units.
- **reprojection:** transforming geometry coordinates from one CRS to another.
- **longitude:** east-west angular coordinate, used as x in geographic pairs.
- **latitude:** north-south angular coordinate, used as y in geographic pairs.
- **spatial join:** matching records by a geometric relationship such as within or intersects.

### Reference pattern 1 — Create known geographic points and inspect bounds

Constructed geometry avoids any network or external file.

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

**Expected observation:** The CRS is WGS 84/EPSG:4326 and bounds are approximately `[-122.4, 37.8, -73.9, 40.7]` in longitude/latitude degrees.

### Reference pattern 2 — Reproject rather than relabel

Projected coordinates use different units while representing the same places.

```python
projected = places.to_crs("EPSG:3857")
{
    "same_rows": len(projected) == len(places),
    "projected_crs": str(projected.crs),
    "x_units_are_not_degrees": abs(projected.geometry.x.iloc[0]) > 1_000,
}
```

**Expected observation:** All checks are true; the coordinates are transformed to meter-like Web Mercator values.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Using only a local or already-cached boundary/point source, create a GeoDataFrame plot. **Before plotting:** record provenance/license, CRS, geometry types, invalid/empty counts, and bounds. **Constraints:** transform all layers to one appropriate CRS and never use `set_crs` as if it reprojected coordinates. **Verify:** check a known location/bounds and confirm entity count survives reprojection.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from geospatial semantics, coordinate reference systems, valid geometry, and offline fallback.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** When location is not central or source geometry is unavailable, a deterministic domain/network visualization can teach graph structure without a misleading map.

**Edge case:** Missing CRS, invalid/self-intersecting geometry, dateline crossing, swapped axes, empty geometry, and remote basemap failure need policy.

**Solution evidence to inspect:** check a known location/bounds and confirm entity count survives reprojection.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Alternatively, construct a deterministic NetworkX domain graph where node and edge meanings are written explicitly. **Constraints:** use a fixed layout seed, encode at most a few meaningful attributes, provide labels/legend, and do not require network data. **Verify:** reconcile plotted node/edge counts to the graph and explain what spatial questions this fallback cannot answer.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies geospatial semantics, coordinate reference systems, valid geometry, and offline fallback.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** When location is not central or source geometry is unavailable, a deterministic domain/network visualization can teach graph structure without a misleading map.

**Edge case:** Missing CRS, invalid/self-intersecting geometry, dateline crossing, swapped axes, empty geometry, and remote basemap failure need policy.

**Solution evidence to inspect:** reconcile plotted node/edge counts to the graph and explain what spatial questions this fallback cannot answer.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict what goes wrong when latitude/longitude degrees are overlaid on a web map measured in Web Mercator meters. **Progressive hint:** Layers must use compatible coordinate reference systems (CRSs). **Verify:** Compare both CRS/bounds, then assert reprojection makes units compatible and the transformed layers overlap in a plausible extent.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying geospatial semantics, coordinate reference systems, valid geometry, and offline fallback.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** When location is not central or source geometry is unavailable, a deterministic domain/network visualization can teach graph structure without a misleading map.

**Edge case:** Missing CRS, invalid/self-intersecting geometry, dateline crossing, swapped axes, empty geometry, and remote basemap failure need policy.

**Solution evidence to inspect:** Compare both CRS/bounds, then assert reprojection makes units compatible and the transformed layers overlap in a plausible extent.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace one point represented as `(longitude, latitude)` and explain why swapping values can still create a valid but wrong location. **Progressive hint:** Both numbers may fall in legal ranges, so semantic order matters. **Verify:** Validate the known longitude/latitude pair against real bounds, swap it, and show why semantic checks—not only numeric ranges—detect the wrong location.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the geospatial semantics, coordinate reference systems, valid geometry, and offline fallback model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** When location is not central or source geometry is unavailable, a deterministic domain/network visualization can teach graph structure without a misleading map.

**Edge case:** Missing CRS, invalid/self-intersecting geometry, dateline crossing, swapped axes, empty geometry, and remote basemap failure need policy.

**Solution evidence to inspect:** Validate the known longitude/latitude pair against real bounds, swap it, and show why semantic checks—not only numeric ranges—detect the wrong location.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Implement a longitude/latitude bounding-box validator with clear ordering and range checks. **Progressive hint:** Require west ≤ east, south ≤ north, and geographic bounds. **Verify:** Assert a valid box passes and separately reject west>east, south>north, longitude outside ±180, and latitude outside ±90.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies geospatial semantics, coordinate reference systems, valid geometry, and offline fallback.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** When location is not central or source geometry is unavailable, a deterministic domain/network visualization can teach graph structure without a misleading map.

**Edge case:** Missing CRS, invalid/self-intersecting geometry, dateline crossing, swapped axes, empty geometry, and remote basemap failure need policy.

**Solution evidence to inspect:** Assert a valid box passes and separately reject west>east, south>north, longitude outside ±180, and latitude outside ±90.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair a spatial join or overlay attempted before CRS comparison and reprojection. **Progressive hint:** Inspect `.crs`; transform one layer to the other's CRS. **Verify:** Show the pre-reprojection CRS mismatch, transform one layer, and assert the operation now uses equal CRS while preserving row identities.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in geospatial semantics, coordinate reference systems, valid geometry, and offline fallback.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** When location is not central or source geometry is unavailable, a deterministic domain/network visualization can teach graph structure without a misleading map.

**Edge case:** Missing CRS, invalid/self-intersecting geometry, dateline crossing, swapped axes, empty geometry, and remote basemap failure need policy.

**Solution evidence to inspect:** Show the pre-reprojection CRS mismatch, transform one layer, and assert the operation now uses equal CRS while preserving row identities.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Define fallback behavior for missing/invalid geometry or unavailable map data, including an offline domain-graph alternative. **Progressive hint:** A missing basemap should not erase the analytical data layer. **Verify:** Feed missing/invalid geometry and unavailable basemap fixtures; assert analytical records remain represented by the documented local layer or graph fallback.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from geospatial semantics, coordinate reference systems, valid geometry, and offline fallback.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** When location is not central or source geometry is unavailable, a deterministic domain/network visualization can teach graph structure without a misleading map.

**Edge case:** Missing CRS, invalid/self-intersecting geometry, dateline crossing, swapped axes, empty geometry, and remote basemap failure need policy.

**Solution evidence to inspect:** Feed missing/invalid geometry and unavailable basemap fixtures; assert analytical records remain represented by the documented local layer or graph fallback.
<!-- END BEGINNER SOLUTION REVIEW -->

Two tracks depending on environment: GeoPandas map or a domain visualization with networkx.

Contents
- Exercise 1: Plot city/country boundaries (GeoPandas)
- Exercise 2: Alternative domain visualization (network graph)

---

Track A — Geospatial (GeoPandas)
```python
# Requires: geopandas, contextily, geodatasets
import contextily as cx
import geopandas as gpd
from geodatasets import get_path

world = gpd.read_file(get_path('naturalearth.land')).to_crs(3857)
ax = world.plot(figsize=(8, 6), alpha=0.6, edgecolor='k')
cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik)
ax.set(title='World basemap (Web Mercator)')
```

Track B — Domain viz (NetworkX)
```python
import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
G.add_edge('ingest','clean'); G.add_edge('clean','validate'); G.add_edge('validate','model')
G.add_edge('model','serve'); G.add_edge('serve','monitor')

pos = nx.spring_layout(G, seed=42)
plt.figure(figsize=(6,4))
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1200)
plt.title('Pipeline Stages (Network Graph)'); plt.tight_layout(); plt.show()
```
Notes
- For maps, ensure CRS is consistent; reproject to 3857 for web tiles
- `geodatasets` and contextily tiles download/cache data on first use
- For network graphs, layout algorithms (spring, kamada_kawai) affect readability

---

## Expanded mastery lab solutions

Treat coordinate reference system, coordinate order, source provenance, geometry validity, and network/cache behavior as part of the visualization.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — CRS and coordinate order

Longitude/latitude data are commonly stored as `(x, y) = (longitude, latitude)`.
Swapping them may still produce numbers inside valid ranges but a wrong place.
Degrees and projected meters cannot be overlaid without reprojection.

### Practices 3–5 — Validate spatial boundaries and degrade gracefully

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class GeographicBounds:
    west: float
    south: float
    east: float
    north: float

    def __post_init__(self) -> None:
        if not (-180 <= self.west <= self.east <= 180):
            raise ValueError("longitude bounds must satisfy -180 <= west <= east <= 180")
        if not (-90 <= self.south <= self.north <= 90):
            raise ValueError("latitude bounds must satisfy -90 <= south <= north <= 90")

    def contains(self, longitude: float, latitude: float) -> bool:
        return (
            self.west <= longitude <= self.east
            and self.south <= latitude <= self.north
        )


bounds = GeographicBounds(west=-125, south=32, east=-114, north=42)
assert bounds.contains(longitude=-122.4, latitude=37.8)
assert not bounds.contains(longitude=37.8, latitude=-122.4)
```

Before a GeoPandas operation, reject unknown CRSs and call `to_crs` so both
layers match. Filter/report empty or invalid geometries rather than silently
dropping them. If a cached basemap is unavailable, plot the local geometry
alone; if no geometry dependency is installed, a deterministic NetworkX graph
can teach domain topology without pretending it is a geographic map.
