# js-062: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

GeoJSON represents geographic features using geometry and properties. Geographic coordinates conventionally use longitude then latitude in degrees. Swapping them can produce plausible but incorrect locations. A map projection converts positions on the globe into a flat display, introducing distortion because a sphere cannot be flattened without tradeoffs.

Different projections preserve different properties locally or globally. A map for comparing area should not casually use a projection that strongly distorts area. A map for route direction has another purpose. State the geographic scope and the projection’s relevance to the analytical question.

The reference uses a tiny original synthetic point collection, so it needs no external map download or geographic dataset license. It demonstrates coordinate conversion and path creation without pretending that dots alone are a detailed basemap. Real geographic boundaries also require source, date and topology review.

A FeatureCollection contains Feature objects with geometry and properties. `d3.geoMercator` returns a projection callable on `[longitude,latitude]`. `d3.geoPath(projection)` converts GeoJSON into SVG path data. Fitting a projection to data chooses scale and translation for a view, not an analytical normalization of values.

Check that all projected coordinates are finite and within the intended view. A coordinate can be valid globally yet outside your chosen region. Handle antimeridian crossings and polygon winding deliberately for actual region datasets; those cases are not solved by swapping arbitrary signs until a map looks right.

## Exercise 1: Identify longitude and latitude positions.

GeoJSON order is part of the data contract. A swapped pair can still fall within numeric bounds and silently map the wrong place.

**Expected:** The first coordinate is longitude and the second latitude.

## Exercise 2: Change a longitude while holding latitude fixed.

Use a known anchor to reason about direction before interpreting an unfamiliar region.

**Expected:** The projected horizontal location changes under this projection.

## Exercise 3: Render the synthetic point collection.

Keep feature identity and geometry separate from visual styling. No external fetch is required.

**Expected:** One finite path per feature with descriptive labels.

## Exercise 4: Diagnose a misplaced but numerically valid point.

Visual plausibility is not enough. Use known landmarks or synthetic anchors to localize the mismatch.

**Expected:** Check coordinate order, units, projection and source reference system.

## Exercise 5: Explain projection distortion.

Choose the property relevant to the task and state the tradeoff. A familiar projection is not automatically appropriate for area comparison.

**Expected:** A flat map cannot preserve every geographic property simultaneously.

## Exercise 6: Plan a real boundary-data integration.

The map must be reproducible and legally distributable. Offline packaging needs deliberate acquisition and attribution, not a hidden runtime download.

**Expected:** Source/license, date, stable IDs, topology and projection checks.
