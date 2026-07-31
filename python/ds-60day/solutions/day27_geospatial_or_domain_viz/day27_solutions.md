# Day 27 — Solutions: Geospatial or Domain-specific Visualization

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **geospatial semantics, coordinate reference systems, valid geometry, and offline fallback**. Predict each named
result before comparing your attempt with its matching assertions.

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

### How to compare an answer

For this lesson's **geospatial semantics, coordinate reference systems, valid geometry, and offline fallback** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–2 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Using only a local or already-cached boundary/point source, create a GeoDataFrame plot. **Before plotting:** record provenance/license, CRS, geometry types, invalid/empty counts, and bounds. **Constraints:** transform all layers to one appropriate CRS and never use `set_crs` as if it reprojected coordinates. **Verify:** check a known location/bounds and confirm entity count survives reprojection.

**Reasoning:** Make this boundary unambiguous in code: Using only a local or already-cached boundary/point source, create a GeoDataFrame plot. Before plotting: record provenance/license, CRS, geometry types, invalid/empty counts, and bounds. Constraints: transform all layers to one appropriate CRS and never use `set_crs` as if it reprojected coordinates. Values below, at, and above the named boundary must produce the evidence check a known location/bounds and confirm entity count survives reprojection. Those cases show how geospatial semantics, coordinate reference systems, valid geometry, and offline fallback behaves at its edge.

```python
import geopandas as gpd
from shapely.geometry import Point

places = gpd.GeoDataFrame(
    {"name": ["San Francisco", "New York"]},
    geometry=[Point(-122.4, 37.8), Point(-73.9, 40.7)],
    crs="EPSG:4326",
)
spatial_profile = {
    "provenance": "constructed course points",
    "license": "course-authored fixture; unrestricted educational reuse",
    "crs": places.crs.to_string(),
    "geometry_types": sorted(places.geom_type.unique().tolist()),
    "invalid_count": int((~places.geometry.is_valid).sum()),
    "empty_count": int(places.geometry.is_empty.sum()),
    "bounds": places.total_bounds.tolist(),
}
assert places.crs is not None
assert places.geometry.is_valid.all()
assert spatial_profile["geometry_types"] == ["Point"]
assert spatial_profile["bounds"][0] < -122
assert places.loc[
    places["name"].eq("San Francisco"), "geometry"
].iloc[0].x == -122.4
projected = places.to_crs("EPSG:3857")
assert len(projected) == len(places)
assert projected.crs == "EPSG:3857"
assert not projected.geometry.equals(places.geometry)
ax = projected.plot()
assert len(ax.collections) >= 1
```

This constructed local fixture needs no basemap or network source.
`to_crs` transforms coordinates; `set_crs` would only relabel their
meaning and would be incorrect here.

**Verification evidence:** check a known location/bounds and confirm entity count survives reprojection.

### Exercise 2 — worked answer

**Learner contract:** Alternatively, construct a deterministic NetworkX domain graph where node and edge meanings are written explicitly. **Constraints:** use a fixed layout seed, encode at most a few meaningful attributes, provide labels/legend, and do not require network data. **Verify:** reconcile plotted node/edge counts to the graph and explain what spatial questions this fallback cannot answer.

**Reasoning:** Implement this exact contract as written: Alternatively, construct a deterministic NetworkX domain graph where node and edge meanings are written explicitly. Constraints: use a fixed layout seed, encode at most a few meaningful attributes, provide labels/legend, and do not require network data. Keep the prompt's named data and constraints visible in the code, then establish this specific result: reconcile plotted node/edge counts to the graph and explain what spatial questions this fallback cannot answer. That connects the answer to geospatial semantics, coordinate reference systems, valid geometry, and offline fallback.

```python
import matplotlib.pyplot as plt
import networkx as nx

graph = nx.Graph()
graph.add_nodes_from([
    ("source", {"role": "input"}),
    ("clean", {"role": "transform"}),
    ("report", {"role": "output"}),
])
graph.add_edges_from([
    ("source", "clean", {"meaning": "feeds"}),
    ("clean", "report", {"meaning": "produces"}),
])
positions = nx.spring_layout(graph, seed=42)
fig, ax = plt.subplots(figsize=(5, 3))
role_shapes = {"input": "s", "transform": "o", "output": "^"}
for role, shape in role_shapes.items():
    nodes = [
        node for node, attributes in graph.nodes(data=True)
        if attributes["role"] == role
    ]
    nx.draw_networkx_nodes(
        graph,
        positions,
        nodelist=nodes,
        node_shape=shape,
        label=role,
        ax=ax,
    )
nx.draw_networkx_edges(graph, positions, ax=ax)
nx.draw_networkx_labels(graph, positions, ax=ax)
ax.legend(title="Node role")
ax.set_axis_off()

assert graph.number_of_nodes() == 3
assert graph.number_of_edges() == 2
assert set(positions) == set(graph)
assert sum(len(collection.get_offsets()) for collection in ax.collections[:3]) == 3
plt.close(fig)
```

A deterministic graph can show dependency relationships offline, but
it cannot answer geographic distance, containment, or coordinate
questions because its layout encodes readability, not physical space.

**Verification evidence:** reconcile plotted node/edge counts to the graph and explain what spatial questions this fallback cannot answer.

## Exercises 3–7 — Expanded mastery answers

### Exercise 3 — answer contract

**Learner contract:** **Prediction:** Predict what goes wrong when latitude/longitude degrees are overlaid on a web map measured in Web Mercator meters. **Progressive hint:** Layers must use compatible coordinate reference systems (CRSs). **Verify:** Compare both CRS/bounds, then assert reprojection makes units compatible and the transformed layers overlap in a plausible extent.

**Reasoning:** Predict this named state change before running it: Prediction: Predict what goes wrong when latitude/longitude degrees are overlaid on a web map measured in Web Mercator meters. Progressive hint: Layers must use compatible coordinate reference systems (CRSs). Then compare the prediction with this proof target: Compare both CRS/bounds, then assert reprojection makes units compatible and the transformed layers overlap in a plausible extent. This makes geospatial semantics, coordinate reference systems, valid geometry, and offline fallback observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Compare both CRS/bounds, then assert reprojection makes units compatible and the transformed layers overlap in a plausible extent.

### Exercise 4 — answer contract

**Learner contract:** **Tracing:** Trace one point represented as `(longitude, latitude)` and explain why swapping values can still create a valid but wrong location. **Progressive hint:** Both numbers may fall in legal ranges, so semantic order matters. **Verify:** Validate the known longitude/latitude pair against real bounds, swap it, and show why semantic checks—not only numeric ranges—detect the wrong location.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace one point represented as `(longitude, latitude)` and explain why swapping values can still create a valid but wrong location. Progressive hint: Both numbers may fall in legal ranges, so semantic order matters. Record the named value, shape, label, or iterator position needed to establish: Validate the known longitude/latitude pair against real bounds, swap it, and show why semantic checks—not only numeric ranges—detect the wrong location. The trace exposes geospatial semantics, coordinate reference systems, valid geometry, and offline fallback directly.

**Evidence to locate in the grouped implementation:** Validate the known longitude/latitude pair against real bounds, swap it, and show why semantic checks—not only numeric ranges—detect the wrong location.

### Exercise 5 — answer contract

**Learner contract:** **Implementation:** Implement a longitude/latitude bounding-box validator with clear ordering and range checks. **Progressive hint:** Require west ≤ east, south ≤ north, and geographic bounds. **Verify:** Assert a valid box passes and separately reject west>east, south>north, longitude outside ±180, and latitude outside ±90.

**Reasoning:** Implement this exact contract as written: Implementation: Implement a longitude/latitude bounding-box validator with clear ordering and range checks. Progressive hint: Require west ≤ east, south ≤ north, and geographic bounds. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert a valid box passes and separately reject west>east, south>north, longitude outside ±180, and latitude outside ±90. That connects the answer to geospatial semantics, coordinate reference systems, valid geometry, and offline fallback.

**Evidence to locate in the grouped implementation:** Assert a valid box passes and separately reject west>east, south>north, longitude outside ±180, and latitude outside ±90.

### Exercise 6 — answer contract

**Learner contract:** **Debugging:** Repair a spatial join or overlay attempted before CRS comparison and reprojection. **Progressive hint:** Inspect `.crs`; transform one layer to the other's CRS. **Verify:** Show the pre-reprojection CRS mismatch, transform one layer, and assert the operation now uses equal CRS while preserving row identities.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair a spatial join or overlay attempted before CRS comparison and reprojection. Progressive hint: Inspect `.crs`; transform one layer to the other's CRS. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Show the pre-reprojection CRS mismatch, transform one layer, and assert the operation now uses equal CRS while preserving row identities. The diagnosis depends on geospatial semantics, coordinate reference systems, valid geometry, and offline fallback.

**Evidence to locate in the grouped implementation:** Show the pre-reprojection CRS mismatch, transform one layer, and assert the operation now uses equal CRS while preserving row identities.

### Exercise 7 — answer contract

**Learner contract:** **Edge case and explanation:** Define fallback behavior for missing/invalid geometry or unavailable map data, including an offline domain-graph alternative. **Progressive hint:** A missing basemap should not erase the analytical data layer. **Verify:** Feed missing/invalid geometry and unavailable basemap fixtures; assert analytical records remain represented by the documented local layer or graph fallback.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Define fallback behavior for missing/invalid geometry or unavailable map data, including an offline domain-graph alternative. Progressive hint: A missing basemap should not erase the analytical data layer. Values below, at, and above the named boundary must produce the evidence Feed missing/invalid geometry and unavailable basemap fixtures; assert analytical records remain represented by the documented local layer or graph fallback. Those cases show how geospatial semantics, coordinate reference systems, valid geometry, and offline fallback behaves at its edge.

**Evidence to locate in the grouped implementation:** Feed missing/invalid geometry and unavailable basemap fixtures; assert analytical records remain represented by the documented local layer or graph fallback.

## Expanded mastery lab solutions

Treat coordinate reference system, coordinate order, source provenance, geometry validity, and network/cache behavior as part of the visualization.

### Shared implementation for Exercises 3–4 — CRS and coordinate order

Longitude/latitude data are commonly stored as `(x, y) = (longitude, latitude)`.
Swapping them may still produce numbers inside valid ranges but a wrong place.
Degrees and projected meters cannot be overlaid without reprojection.

### Shared implementation for Exercises 5–7 — Validate spatial boundaries and degrade gracefully

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
