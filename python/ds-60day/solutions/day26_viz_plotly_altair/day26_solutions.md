# Day 26 — Solutions: Interactive Visualization (Plotly / Altair)

We create an interactive histogram with dynamic bins and save to HTML.

Contents
- Exercise 1: Interactive histogram with dynamic bins
- Exercise 2: Save to HTML and open in a browser

---

Plotly Express approach
```python
import plotly.express as px
import seaborn as sns

df = sns.load_dataset('tips')
fig = px.histogram(df, x='total_bill', nbins=40, color='time', marginal='rug',
                   title='Interactive Total Bill Histogram')
fig.update_layout(bargap=0.05)
fig.show()
fig.write_html('reports/figures/total_bill_hist_interactive.html', include_plotlyjs='cdn')
```

Altair approach (requires vega)
```python
import altair as alt, pandas as pd, seaborn as sns

df = sns.load_dataset('tips')
slider = alt.binding_range(min=10, max=80, step=5, name='Bins: ')
select_bins = alt.selection_point(bind=slider, fields=['bins'], value={'bins':40})

hist = (alt.Chart(df)
  .transform_bin('binned', field='total_bill', bin={'maxbins': {'expr': 'bins'}}, as_=['lo','hi'])
  .mark_bar()
  .encode(x='lo:Q', x2='hi:Q', y='count()', color='time:N', tooltip=['count()'])
  .add_params(select_bins))

hist.properties(width=500, height=300)
```
Notes
- For Plotly, write_html saves a self-contained report friendly for sharing
- Altair interactive binning shown via a bound parameter
