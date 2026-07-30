# Day 27 — Solutions: Geospatial or Domain-specific Visualization

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

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Plot local city/country boundaries when a local or cached source is available. **Hint:** inspect `.crs`, geometry validity, and bounds before plotting; reproject data and basemap to a common CRS.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Alternatively, visualize a domain graph with NetworkX. **Hint:** define what nodes/edges mean, use a fixed layout seed, and encode only a small number of meaningful attributes.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Prediction

**Prompt:** Predict what goes wrong when latitude/longitude degrees are overlaid on a web map measured in Web Mercator meters.

**Reasoning checkpoint:** Layers must use compatible coordinate reference systems (CRSs). The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 4 — Tracing

**Prompt:** Trace one point represented as `(longitude, latitude)` and explain why swapping values can still create a valid but wrong location.

**Reasoning checkpoint:** Both numbers may fall in legal ranges, so semantic order matters. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Implementation

**Prompt:** Implement a longitude/latitude bounding-box validator with clear ordering and range checks.

**Reasoning checkpoint:** Require west ≤ east, south ≤ north, and geographic bounds. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Debugging

**Prompt:** Repair a spatial join or overlay attempted before CRS comparison and reprojection.

**Reasoning checkpoint:** Inspect `.crs`; transform one layer to the other's CRS. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Edge case and explanation

**Prompt:** Define fallback behavior for missing/invalid geometry or unavailable map data, including an offline domain-graph alternative.

**Reasoning checkpoint:** A missing basemap should not erase the analytical data layer. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

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
