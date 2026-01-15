# Day 26 — Interactive Viz with Plotly and Altair (Companion Guide)

## Learning objectives
- Build interactive charts with Plotly (express + graph_objects)
- Use Altair’s grammar of graphics and declarative encodings
- Add tooltips, selection, faceting, and small multiples

## Why this matters
Interactive visuals accelerate exploration and communication, enabling users to discover insights themselves.

## Mental models
- Plotly Express: quick, high-level API returning figures you can refine
- Altair: declarative chart spec; think "map data fields to encodings"

## Core concepts and examples
### Plotly Express
```python
import plotly.express as px
fig = px.scatter(df, x='sepal_width', y='sepal_length', color='species',
                 hover_data=['petal_length'])
fig.update_traces(marker=dict(size=10, opacity=0.7))
fig.update_layout(title='Iris scatter')
```

### Plotly graph_objects (fine control)
```python
from plotly import graph_objects as go
fig = go.Figure()
fig.add_trace(go.Bar(x=df['category'], y=df['value']))
fig.update_layout(barmode='group')
```

### Altair basics
```python
import altair as alt
chart = (alt.Chart(df)
    .mark_circle(size=60)
    .encode(x='x:Q', y='y:Q', color='segment:N', tooltip=['x','y','segment']))
chart.properties(width=300, height=200)
```

### Selections and faceting (Altair)
```python
brush = alt.selection_interval()
pts = chart.add_params(brush).encode(opacity=alt.condition(brush, alt.value(1), alt.value(0.2)))
(pts & pts.facet('segment'))
```

## Common pitfalls
- Overspecifying encodings; Altair expects tidy data and clear types
- Too many points without aggregation; consider density/aggregation
- Performance with huge datasets; pre-aggregate or sample

## Practice exercises
1) Recreate a static seaborn plot in Plotly with tooltips
2) Build an Altair chart with a selection brush to highlight a subset
3) Create faceted small multiples comparing segments

## Further reading
- Plotly: https://plotly.com/python/
- Altair: https://altair-viz.github.io
