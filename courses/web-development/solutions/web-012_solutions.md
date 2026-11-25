# web-012: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-012.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Explain the reference for rem and a typical em use.

**Expected answer:** Rem uses the root font size; em commonly scales with the relevant element's font size.

**Approach:** Name the reference element for each unit: `rem` reads the root font size, while `em` reads the current element's font size (or the parent's when used in `font-size`).

**Why:** rem always refers to the root element's font size, while em refers to the current element's font size, or to the parent's when it is used in font-size itself.

**Plausible wrong approach:** Using `em` for nested list text fails in a different way than expected, because each level multiplies the inherited size and text keeps shrinking or growing.

**How to verify:** Set `html { font-size: 20px; }` and confirm in Computed that `2rem` resolves to 40px regardless of the parent's size.

## Exercise 2: Apply a system font stack without network dependencies.

**Expected evidence:** The page remains readable offline on different operating systems.

**Approach:** Set `font-family: system-ui, sans-serif` so each operating system uses its installed interface font without any download.

**Why:** A system font stack uses fonts that are already installed, so text renders offline without network requests.

**Plausible wrong approach:** Linking a hosted web font fails in this pad because external requests are blocked, so the fallback appears with an unexpected layout shift.

**How to verify:** The Network panel shows no font requests, and the Computed panel lists a rendered local font family.

## Exercise 3: Build a reading page with bounded measure and scalable headings.

**Expected evidence:** Text stays comfortable at wide and narrow sizes without fixed-height clipping.

**Approach:** Combine a `.prose` column with `max-inline-size: 65ch`, a unitless line height and the clamped heading rule from worked example 2.

**Why:** A bounded measure keeps line length readable, and clamp scales headings between safe limits while respecting the reader's font size.

**Plausible wrong approach:** Giving the reading column a fixed `height` fails because longer content or larger text then overflows or is clipped.

**How to verify:** At wide, narrow and enlarged sizes the column stays narrow enough to read and no paragraph is clipped.

## Exercise 4: Diagnose text that overlaps after zooming.

**Expected answer:** Inspect fixed heights, line heights and positioned containers rather than disabling zoom.

**Approach:** Zoom until overlap appears, then inspect the overlapping elements for fixed heights, pixel line heights or absolute positioning.

**Why:** Zoom enlarges text but fixed boxes keep their size, so content spills out and overlaps.

**Plausible wrong approach:** Adding `maximum-scale=1` to the viewport meta tag fails because it blocks the reader's zoom instead of fixing the layout.

**How to verify:** After replacing fixed heights with content-driven sizing, the same zoom level shows no overlapping lines.

## Exercise 5: Test at increased browser zoom with long content.

**Expected evidence:** Reading order, text visibility and controls remain intact.

**Approach:** Paste several long paragraphs, then step browser zoom up to 200 percent and scroll through the whole page.

**Why:** Text must remain usable when resized to 200 percent, which reveals fixed-size assumptions in the layout.

**Plausible wrong approach:** Checking only the top of the page fails because clipping often appears lower, inside cards or footers with fixed sizes.

**How to verify:** At 200 percent every paragraph is readable in order and every link and button can still be reached with Tab.

## Exercise 6: Explain why ch is a useful approximation rather than a word-count guarantee.

**Expected answer:** It measures the font's zero glyph, and actual character widths vary.

**Approach:** Compare a line of digits with a line of mixed letters at `65ch` and note how many characters actually fit.

**Why:** 1ch is the advance width of the 0 glyph, so a line of narrow letters fits more characters and a line of wide letters fewer.

**Plausible wrong approach:** Promising exactly 65 letters per line fails because `ch` is the width of 0, and narrow letters like i let more characters fit.

**How to verify:** Counting characters on two different lines of the same column gives different totals near, but not equal to, 65.

## Reference comparison

The reference checks that the prose container has a max-inline-size other than none, so it catches a page whose lines run the full width. It does not test the line height, the heading clamp or behavior at 200 percent zoom, so enlarge the text yourself and compare where lines wrap.

Open `courses/web-development/solutions/web-012_solution.html` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
