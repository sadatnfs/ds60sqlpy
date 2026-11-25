# web-017: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-017.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Predict the base layout below the breakpoint.

**Expected answer:** The layout stays in one column.

**Approach:** Read the base rule outside the media query: it sets grid with a gap but no columns, so one implicit column holds every section.

**Why:** Rules outside the query apply at every width, and the min-width query only adds the two-column layout when there is room.

**Plausible wrong approach:** Predicting two columns because the stylesheet mentions them fails because that rule only applies when the `min-width` query matches.

**How to verify:** Below 48rem wide, the grid overlay shows one column and the Styles panel shows the media rule as inactive.

## Exercise 2: Choose a breakpoint by resizing actual content.

**Expected answer:** Record where labels or article width become uncomfortable rather than choosing a device name.

**Approach:** Slowly narrow the preview and write down the width where labels wrap awkwardly or the article column becomes too narrow.

**Why:** Content-driven breakpoints follow the design's real limits, while device-named widths go out of date as screens change.

**Plausible wrong approach:** Choosing 768px because it matches a tablet fails because your content may break earlier or later than that device.

**How to verify:** Your recorded breakpoint, converted to rem, matches the width where you saw the layout become cramped.

## Exercise 3: Build a responsive course outline with a readable article.

**Expected evidence:** The page adapts between stacked and two-column layouts without losing content.

**Approach:** Write a single-column base, then add a `min-width` query that places navigation in a bounded column beside a flexible article.

**Why:** A small-screen baseline works everywhere, and the enhancement applies only when the measured space allows it.

**Plausible wrong approach:** Starting from the desktop layout and hiding parts with `max-width` queries fails because narrow screens may lose content entirely.

**How to verify:** Below the breakpoint, navigation and article stack; above it, they sit side by side with every link still present.

## Exercise 4: Diagnose a mobile page rendered as a tiny desktop screenshot.

**Expected answer:** Check viewport metadata and inflexible widths.

**Approach:** Check the head for viewport metadata, then look for fixed widths such as `width: 1024px` on wrappers.

**Why:** Without width=device-width the mobile browser lays out a wide virtual page and scales it down, and fixed widths prevent reflow.

**Plausible wrong approach:** Adding more media queries fails when the metadata is missing, because the browser still pretends the screen is wide.

**How to verify:** After adding viewport metadata, a phone emulation shows the base layout and `window.innerWidth` matches the device width.

## Exercise 5: Test narrow width together with enlarged text.

**Expected evidence:** All controls and text remain reachable with no required two-axis page scrolling.

**Approach:** Combine the narrow preset with 200 percent zoom and scroll through the page in both directions.

**Why:** Larger text needs more space, so a layout that fits at default size can force horizontal scrolling when zoomed.

**Plausible wrong approach:** Testing narrow width at default text size fails because enlarged text often reveals fixed widths that force sideways scrolling.

**How to verify:** At narrow width and 200 percent zoom, reading requires only vertical scrolling and every control is reachable.

## Exercise 6: Explain why responsive design is more than media queries.

**Expected answer:** Intrinsic sizing, wrapping, content order and user settings are fundamental parts of the behavior.

**Approach:** List behaviors that work without any query: wrapping flex rows, `minmax` grid tracks, `max-inline-size` and user font settings.

**Why:** Intrinsic sizing, wrapping, flexible units and source order already respond to space and user settings; media queries only adjust the remaining cases.

**Plausible wrong approach:** Treating breakpoints as the whole design fails because between breakpoints the layout can still overflow when nothing else is intrinsic.

**How to verify:** Remove all media queries temporarily; the page still remains readable at narrow widths, only less polished.

## Reference comparison

The reference only checks that a meta element named viewport exists, which catches the classic missing tag. It does not read its content, test your breakpoint, or check that sections stack below it, so compare the layout at a phone width, at your breakpoint and with text enlarged.

Open `courses/web-development/solutions/web-017_solution.html` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
