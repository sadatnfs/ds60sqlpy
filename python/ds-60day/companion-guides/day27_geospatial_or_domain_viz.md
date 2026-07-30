# Day 27 — Geospatial or Domain-Specific Visualization

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

Install the advanced profile if those packages are not present.

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -Advanced
```

macOS/Linux:

```bash
bash scripts/setup.sh --advanced
```

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

1. Plot local city/country boundaries when a local or cached source is
   available. **Hint:** inspect `.crs`, geometry validity, and bounds before
   plotting; reproject data and basemap to a common CRS.
2. Alternatively, visualize a domain graph with NetworkX. **Hint:** define what
   nodes/edges mean, use a fixed layout seed, and encode only a small number of
   meaningful attributes.

### Additional mastery practice

Treat coordinate reference system, coordinate order, source provenance, geometry validity, and network/cache behavior as part of the visualization.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict what goes wrong when latitude/longitude degrees are overlaid on a web map measured in Web Mercator meters.
   **Progressive hint:** Layers must use compatible coordinate reference systems (CRSs).
4. **Tracing:** Trace one point represented as `(longitude, latitude)` and explain why swapping values can still create a valid but wrong location.
   **Progressive hint:** Both numbers may fall in legal ranges, so semantic order matters.
5. **Implementation:** Implement a longitude/latitude bounding-box validator with clear ordering and range checks.
   **Progressive hint:** Require west ≤ east, south ≤ north, and geographic bounds.
6. **Debugging:** Repair a spatial join or overlay attempted before CRS comparison and reprojection.
   **Progressive hint:** Inspect `.crs`; transform one layer to the other's CRS.
7. **Edge case and explanation:** Define fallback behavior for missing/invalid geometry or unavailable map data, including an offline domain-graph alternative.
   **Progressive hint:** A missing basemap should not erase the analytical data layer.

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
- [Next: Day 28 — Feature engineering](day28_feature_engineering.md)
