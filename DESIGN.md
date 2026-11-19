---
name: DS60 Classroom
description: A two-color technical manual you can run.
colors:
  house-ultramarine: "#2f3fb3"
  ultramarine-wash: "#ebedfb"
  light-table: "#f3f4f7"
  page-white: "#ffffff"
  margin-grey: "#eef0f4"
  press-black: "#15181e"
  graphite: "#535a68"
  hairline: "#d9dde4"
  rule-grey: "#c3c8d2"
  listing-slate: "#111d32"
  listing-ink: "#e8efff"
  listing-rule: "#2a3954"
  proof-red: "#b4232f"
  proof-red-wash: "#fdeced"
  pass-green: "#1f7a3a"
  pass-green-wash: "#e7f5ec"
  caution-amber: "#c27c0e"
  proof-red-deep: "#9b1d28"
  listing-deep: "#0d1626"
  listing-panel: "#182540"
  listing-selection: "#4a6aa880"
  listing-selection-match: "#4a6aa84d"
  listing-search: "#ffd39b40"
  listing-search-current: "#ffd39b80"
  syntax-keyword: "#cbb5ff"
  syntax-string: "#a9e6b1"
  syntax-number: "#ffd39b"
  syntax-comment: "#a4b3ca"
  syntax-function: "#91d8fc"
  syntax-type: "#f8b6d5"
  syntax-property: "#f7df96"
  syntax-operator: "#b6e4f5"
  syntax-punctuation: "#c5cfe0"
  syntax-invalid: "#ffadb3"
  ink-start: "#1d4fb8"
  ink-analysis: "#0e6f66"
  ink-statistics: "#6a3d9a"
  ink-ml-ai: "#9b2463"
  ink-data-engineering: "#9a4510"
  ink-languages: "#2f6a1c"
  ink-infrastructure: "#3a4a66"
typography:
  display:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "2.5rem"
    fontWeight: 720
    lineHeight: 1.08
    letterSpacing: "-0.035em"
  display-compact:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "2rem"
    fontWeight: 720
    lineHeight: 1.08
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 720
    letterSpacing: "-0.025em"
  title:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.1875rem"
    fontWeight: 720
    letterSpacing: "-0.015em"
  lead:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.65
  body:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 600
    lineHeight: 1.3
  chapter:
    fontFamily: "Latin Modern, STIX Two Text, Georgia, serif"
    fontSize: "1.15rem"
    fontWeight: 400
    lineHeight: 1.7
  chapter-section:
    fontFamily: "Latin Modern, STIX Two Text, Georgia, serif"
    fontSize: "1.15em"
    fontWeight: 700
    lineHeight: 1.3
  folio:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "3rem"
    fontWeight: 760
    lineHeight: 0.95
    letterSpacing: "-0.04em"
    fontFeature: "tnum"
  listing:
    fontFamily: "ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, monospace"
    fontSize: "0.8125rem"
rounded:
  mark: "2px"
  control: "4px"
  panel: "8px"
spacing:
  hair: "2px"
  tight: "6px"
  base: "8px"
  comfortable: "14px"
  section: "26px"
components:
  button-default:
    backgroundColor: "{colors.page-white}"
    textColor: "{colors.press-black}"
    rounded: "{rounded.control}"
    padding: "8px 14px"
    height: "40px"
  button-default-hover:
    backgroundColor: "{colors.ultramarine-wash}"
  button-primary:
    backgroundColor: "{colors.house-ultramarine}"
    textColor: "{colors.page-white}"
    rounded: "{rounded.control}"
    padding: "8px 14px"
    height: "40px"
  input-field:
    backgroundColor: "{colors.page-white}"
    textColor: "{colors.press-black}"
    rounded: "{rounded.control}"
    padding: "8px 10px"
    height: "40px"
  thumb-tab:
    backgroundColor: "{colors.page-white}"
    textColor: "{colors.press-black}"
    rounded: "{rounded.control}"
    padding: "6px 12px"
    height: "36px"
  badge:
    backgroundColor: "{colors.page-white}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.control}"
    padding: "2px 8px"
  panel:
    backgroundColor: "{colors.page-white}"
    rounded: "{rounded.panel}"
  result-console:
    backgroundColor: "{colors.listing-slate}"
    textColor: "{colors.listing-ink}"
    rounded: "{rounded.panel}"
    padding: "12px 14px"
---

# Design System: DS60 Classroom

## Overview

**Creative North Star: "The Technical Manual You Can Run"**

The classroom is printed like a two-color engineering manual. White pages sit on
a cool light-table ground; the text is press black; one spot ink marks each
part of the library, with a house ultramarine for the catalog and the
interface. Every subject is a thumb-indexed part, and every lesson is a spread:
the chapter on the left page, a runnable listing and its printed result on the
right. Learners read, predict, run and read the result without losing their
place.

Density is that of a reference book, not a marketing site: hairline rules,
tabular folio numerals and compact 4px controls carry the structure. Code and
output are set on dark slate, like listings in a printed manual, so they read
as a different material from the prose. The interface speaks in the system
grotesque; chapters speak in Latin Modern, the typeface of a typeset textbook.

The world deliberately refuses the course-platform card grid with progress
rings, gradient heroes and decorative glass.

**Key Characteristics:**
- Two inks per surface: press black plus one spot ink (house ultramarine or a subject area's ink).
- Pages, not cards: hairline rules and 3px part rules divide content.
- Tabular numerals for folios, counts and timings.
- Dark slate listings and results under light pages.
- Latin Modern chapters, system grotesque interface.

## Colors

A restrained two-ink palette: neutral paper and black ink everywhere, with a single spot ink per context.

### Primary
- **House Ultramarine**: the interface's one voice. Primary buttons, focus rings, folio numerals, links and the active state of controls. In dark appearance it lightens to a pale periwinkle (#aab4ff) so it keeps contrast on dark pages.
- **Ultramarine Wash**: the hover fill of default buttons and the tile behind subject monograms. Never a large background.

### Secondary
Subject-area spot inks mark one part of the library each: thumb tabs, the 3px rule above a contents part and that part's counts. Each has a lighter dark-appearance partner set in `classroom.js`.
- **Start Blue** (ink-start): Start here.
- **Analysis Teal** (ink-analysis): data analysis.
- **Statistics Violet** (ink-statistics): statistics.
- **ML Magenta** (ink-ml-ai): machine learning and AI.
- **Engineering Rust** (ink-data-engineering): data engineering.
- **Languages Green** (ink-languages): programming languages.
- **Infrastructure Slate Blue** (ink-infrastructure): web and infrastructure.

### Tertiary
- **Proof Red** and **Proof Red Wash**: errors, failed runs and changed course data. Error messages stay visible until replaced.
- **Pass Green** and **Pass Green Wash**: successful runs, completed lessons and a ready course database.
- **Caution Amber**: the status dot when course data is missing or a project schema still has to be built. Never text.
- **Proof Red Deep**: the background of persistent error slugs, dark enough for white text.

### Neutral
- **Light Table**: the page ground behind every surface.
- **Page White**: panels, controls, the header and the catalog's open pages.
- **Margin Grey**: secondary bands such as the reader tools and the database status panel.
- **Press Black**: body text and headings.
- **Graphite**: supporting text, captions, metadata and placeholders.
- **Hairline**: 1px dividers between list rows and panel heads.
- **Rule Grey**: control borders and the stronger rules under page titles.
- **Listing Slate**, **Listing Ink** and **Listing Rule**: the code editor, the run result console and its border. **Listing Deep** and **Listing Panel** sit beneath and above it for editor inputs, search panels and tooltips; **Listing Selection** and **Listing Search** tints mark selections and search matches. In a code comparison the same two tints mark the two sides: search amber for lines only in the learner's code, selection blue for lines only in the worked solution. Syntax Invalid at 16 percent opacity marks an error line in the editor.
- **Syntax inks**: pale pastels set on listing slate, shared by the code editor and rendered code blocks: keyword violet, string green, number amber, comment slate, function cyan, type pink, property yellow, operator ice and punctuation grey, with a pale red for invalid code. They appear only on listing slate.

### Named Rules
**The One Spot Ink Rule.** A surface uses press black plus exactly one spot ink: house ultramarine on the catalog and interface, or the current subject's ink on its part. Two spot inks never compete on one surface.

**The Color Is Never Alone Rule.** Every subject ink travels with a text label (thumb tab text, part heading, subject name), so color never carries meaning by itself.

## Typography

**Display Font:** system grotesque (system-ui, with Segoe UI, Roboto, Helvetica Neue and Arial fallbacks)
**Body Font:** the same system grotesque for the interface
**Chapter Font:** Latin Modern (bundled locally, with Iowan Old Style and Georgia fallbacks)
**Label/Mono Font:** ui-monospace (SF Mono, Menlo, Consolas fallbacks)

**Character:** an engineer's grotesque for everything you operate, paired with the textbook serif for everything you read, so the boundary between doing and studying is visible in the type itself.

### Hierarchy
- **Display** (720, 2.5rem, 1.08; 2rem below 800px): the catalog title on the home page only.
- **Headline** (720, 1.75rem, -0.025em): section titles such as the contents heading.
- **Title** (720, 1.1875rem): part headings in the contents and lesson titles in lists.
- **Lead** (400, 1.0625rem, 1.65): the catalog introduction and the search palette's query field.
- **Body** (400, 1rem, 1.55): interface prose and descriptions.
- **Label** (600, 0.8125rem): buttons, tabs, badges and form labels.
- **Chapter** (400, 1.15rem, 1.7, max 78ch): lesson guides. The size is the `--reading-size` variable: 1.0625rem below 800px and 1.25rem in reading focus.
- **Chapter Section** (700, 1.15em of the reading size, 1.3): a guide's sections, with a hairline above; subsections are bold at the reading size. Headings use `em` so they follow the reading size.
- **Folio** (760, 3rem, tabular): the lesson's position number beside its title, in house ultramarine.
- **Listing** (monospace, 0.8125rem): code, results and inline code.

### Named Rules
**The Doing and Reading Rule.** Anything you operate is set in the grotesque; anything you study is set in Latin Modern. Never set a control in the serif or a chapter paragraph in the grotesque.

**The Tabular Figures Rule.** Folios, counts, timings and progress use tabular numerals so columns of numbers align like a printed index.

## Layout

The home page is a contents page: a title block with the library colophon and Continue or Start actions, a thumb index of seven subject areas, then contents parts. Each part is a two-column grid (part head of 180 to 250px, then its subject list) under a 3px rule in the part's ink. The page is centered at a maximum width of 1320px.

A lesson is a spread. The header is sticky at 56px (52px on small screens). The lesson list sits in a left sidebar that can be hidden. The two pages share a resizable split (default 56% for the chapter, adjustable from 30% to 72%, remembered locally) with a 14px gutter; at 1100px and wider both pages scroll independently and stay in view. Results print directly under the run controls.

Below 800px the spread becomes a single column: the header keeps only the brand, search and an icon-only appearance toggle, the folio is dropped from the lesson heading, and Lesson, Code and Result buttons jump between the parts.

The code page reads top to bottom as the learning loop: course database slip (SQL and bridge lessons), the Exercises panel, the prediction, the listing, the run bar, then the result. **Focus on code** gives the code page the whole workspace; from 1100px the listing column and a sticky result column sit side by side. The listing height has a drag and keyboard handle, and A− and A+ set the `--code-size` of the editor, result console and comparison listings from 12 to 20px (14px by default). Both choices are remembered on the learner's computer.

Spacing follows a small 2/6/8/14px control rhythm with 26px section breaks; vertical rhythm inside chapters comes from the 1.75 line height.

## Elevation & Depth

Depth is mostly tonal: white pages on the cool light-table ground, separated by hairlines. Two soft shadows exist, and both are structural rather than decorative.

### Shadow Vocabulary
- **Page** (`box-shadow: 0 1px 2px #15181e0f, 0 8px 24px -12px #15181e29`): resting panels and the contents row under the pointer.
- **Lift** (`box-shadow: 0 2px 4px #15181e14, 0 18px 40px -18px #15181e40`): floating surfaces only, such as the search palette.

### Named Rules
**The Paper Not Glass Rule.** Surfaces are opaque paper. No blur, no translucency, no glow; a floating dialog earns the lift shadow and nothing more.

## Shapes

Corners are crisp: 2px on small marks (swatches, the divider grip, keyboard keys and inline code), 4px on every control (buttons, inputs, tabs, badges, monograms) and 8px on panels, the palette and the result console. Borders are 1px hairlines or rule grey; the only heavy line is the 3px part rule above each contents part. Status dots are 9px circles, and thumb-tab swatches are 9px squares with 2px corners.

## Components

### Buttons
- **Shape:** crisp 4px corners, at least 40px tall.
- **Default:** page white with press black label (600, 0.875rem) and a rule-grey border; hover adds the ultramarine wash and an ultramarine border; press shows a faint inset shadow.
- **Primary:** house ultramarine fill with a white label; hover darkens by brightness, never by a gradient.
- **Quiet:** transparent, for secondary actions such as Check again.
- **Focus:** a 2px house-ultramarine outline offset by 2px on every focusable element.

### Chips (thumb tabs and badges)
- **Thumb tab:** page white, 36px tall, with a 9px square swatch in the area ink and a tabular count; the selected tab is filled solid with its ink and white text.
- **Badge:** page white with graphite text and a hairline border for subject, level, kind and study time.

### Cards / Containers
- **Corner Style:** 8px panels.
- **Background:** page white on the light table.
- **Shadow Strategy:** the page shadow at rest (see Elevation & Depth).
- **Border:** 1px hairline.
- **Internal Padding:** sticky panel heads, with 14 to 26px content padding.

### Inputs / Fields
- **Style:** page white, rule-grey border, 4px corners, 40px tall, graphite placeholders.
- **Hover / Focus:** the border darkens to graphite on hover; focus uses the ultramarine outline.

### Navigation
- **Header:** sticky page-white bar with a hairline base, the "d." brand mark, a search field that opens the Ctrl+K palette, and quiet text links. On phones only the brand, search and an icon-only appearance toggle remain.
- **Lesson list:** numbered rows with tabular numbers, lesson ID, level and study time. A completed lesson's number turns pass green; the current lesson sits on the ultramarine wash with an ultramarine number.
- **Pager:** Previous and Next with a tabular "33 of 86" position.

### Signature Components
- **Chapter opener:** a large tabular folio in house ultramarine beside the badges, title, subtitle, prerequisites and pager.
- **Result console:** listing slate with listing ink, unwrapped monospace output that scrolls horizontally so psql and pandas tables keep their columns; a status line with a pass or proof dot sits above it.
- **Course database panel:** a margin-grey slip at the top of the code page for SQL and bridge lessons, with a status dot (pass green ready, amber missing, proof red changed, pulsing ultramarine while checking) and at most one primary action.
- **Run bar:** the primary Run button with its keyboard shortcut set as a key cap and a tabular elapsed timer while a run is active; the time limit, Save and runtime check follow as secondary controls.
- **Run explanation:** a proof-red-wash slip directly above the result console after a failed run: a plain-language title, one next step, the original error line in monospace, and Show line N, which marks that line in the editor.
- **Exercises panel:** a page-white section on the code page under a margin-grey head (Exercises, a tabular "n of N solved" count, Hide). The problem index is a row of 36px numbered buttons like thumb tabs: the current problem is filled with house ultramarine, and a solved problem's number turns pass green with a check. Problem text, facts and hints are set in the chapter serif; labels such as Expected result are graphite grotesque labels. Hints open one at a time on margin-grey slips, and "How to check your answer" stays folded until asked for. A worked solution opens only after an inline try-first slip on the ultramarine wash. Its tools run the solution without changing the learner's code, compare it with the learner's code, and put it in the editor as one undoable step.
- **Comparison listing:** listing slate with a tag column. Lines only in the learner's code carry the search tint and an amber Yours tag; lines only in the solution carry the selection tint and a cyan Solution tag; long runs of matching lines fold to a count. The summary above it reminds the learner that different is not wrong.
- **Search palette:** a lifted 680px dialog listing subjects and lessons with keyboard selection.

## Do's and Don'ts

### Do:
- **Do** keep each surface to press black plus one spot ink (The One Spot Ink Rule).
- **Do** pair every subject ink with its text label.
- **Do** set chapters in Latin Modern at 1.0625rem/1.75 within 78ch, and interface text in the system grotesque.
- **Do** use tabular numerals for folios, counts, timings and progress.
- **Do** print run output on listing slate directly under the run controls, unwrapped.
- **Do** keep controls at 4px corners and 40px minimum height, panels at 8px.
- **Do** keep worked solutions behind an explicit choice, and change the learner's code only as one undoable step they chose.

### Don't:
- **Don't** build uniform card grids, progress rings or gradient heroes; the home page is a contents page.
- **Don't** add eyebrow or kicker labels above headings.
- **Don't** use colored side borders thicker than 1px on cards or callouts.
- **Don't** use blur, translucency or glow (The Paper Not Glass Rule).
- **Don't** let two subject inks share one surface.
