# Day 27 — Solutions: Geospatial or Domain-specific Visualization

Two tracks depending on environment: GeoPandas map or a domain visualization with networkx.

Contents
- Exercise 1: Plot city/country boundaries (GeoPandas)
- Exercise 2: Alternative domain visualization (network graph)

---

Track A — Geospatial (GeoPandas)
```python
# Requires: geopandas, contextily
import geopandas as gpd, contextily as cx
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres')).to_crs(3857)
ax = world.plot(figsize=(8,6), alpha=0.6, edgecolor='k')
cx.add_basemap(ax, source=cx.providers.Stamen.TonerLite)
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
- For network graphs, layout algorithms (spring, kamada_kawai) affect readability
