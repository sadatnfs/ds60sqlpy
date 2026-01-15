# Day 27 — Geospatial and Domain-Specific Visualization (Companion Guide)

## Learning objectives
- Plot geospatial data with GeoPandas, contextily, and Plotly choropleths
- Understand projections (CRS) and when to reproject
- Apply domain-appropriate visuals (maps, network graphs, Sankey)

## Why this matters
Spatial data requires specialized tooling and careful interpretation. Correct projections and choices make or break insights.

## Core concepts and examples
### GeoPandas + contextily
```python
import geopandas as gpd, contextily as cx
roads = gpd.read_file('roads.geojson').to_crs(3857)
ax = roads.plot(figsize=(6,6), linewidth=1, alpha=0.8)
cx.add_basemap(ax, source=cx.providers.Stamen.TonerLite)
```

### Choropleth (Plotly)
```python
import plotly.express as px
fig = px.choropleth(df, geojson=counties_geojson, locations='fips', color='rate',
                    color_continuous_scale='Viridis', scope='usa')
fig.update_geos(fitbounds="locations", visible=False)
```

### CRS and buffering
```python
g = gdf.to_crs(3857)
g['buffer_1km'] = g.geometry.buffer(1000)
```

### Domain visuals
- Networks: use networkx for graph layouts and centrality plots
- Flows: Sankey diagrams (plotly) for process/energy flows

## Common pitfalls
- Mixing lat/lon (EPSG:4326) with web-mercator (EPSG:3857) without reprojection
- Visualizing counts instead of rates per population/area
- Overplotting points; hexbin or density maps help

## Practice exercises
1) Join metrics to shapefiles and draw a choropleth
2) Compute distances after projecting to a metric CRS
3) Create a small Sankey diagram for a process pipeline

## Further reading
- GeoPandas: https://geopandas.org
- CRS basics: https://epsg.io
