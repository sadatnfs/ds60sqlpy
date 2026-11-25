# DAX study guide

This page holds the routine shared by every DAX lesson. Each guide links here instead of repeating it, and keeps its own question, model notes, worked cases, misconception, practice and self-check. Return to the [course map](README.md) to choose a lesson.

## Offline study boundary

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

Each lesson has three files. The editable starter lives in `lessons/`, and the named reference (`.dax`) and explained reasoning (`.md`) live in `solutions/`. Read the mechanisms, trace the worked cases and retain your own draft before you open the reference. Every worked table is hand-derived for the named reference and fixture, so editing a draft never recalculates it.

## The retail star

The ordinary star follows Product → Sales, Customer → Sales and Date → Sales through OrderDate. The ShipDate relationship is inactive unless a case explicitly activates it. Filters flow from the one side to the many side. Additional analytical tables have only the relationships declared in their named model; a similar column name does not create a relationship.

```text
Product (one)  --> Sales (many) <-- Customer (one)
                       ^
                       | active OrderDate
                    Date (one)
                       | inactive ShipDate
                       +------> Sales
```

All amounts in ordinary Sales are USD after the line discount, before tax and returns. The Date fixture is complete for 2024 and 2025; a short result table is a selected slice, not the whole calendar. JSON `null` in the worked-results sidecar means DAX BLANK, not the text "null".

Each lesson links its model specification, which identifies every fixture table, column type, key and relationship. The [fixture handbook](models/README.md) displays the original data and explains each table grain.

## Practice routine

Retain your formula or written reasoning, the stated context, contributing rows or values, and a conclusion with its unit. These notes are your own study record; they do not show that a formula ran. Read the progressive hints one at a time and retry between them.

## Self-check routine

Explain one changed result without quoting the formula alone. Identify which rows, filters, relationship or evaluation scope changed, then construct a counterexample to a plausible wrong interpretation. Keep your draft separate from the supplied reference. A small correct derivation does not certify performance, model security or broad expertise.

## Answers and references

Each lesson's solutions page reconciles the worked cases and explains every practice answer. The complete reference source and the named model belong together. The [reference-results sidecar](reference-results.json) binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## References and evidence limits

Documentation was reviewed for this original course on 2026-10-25. Version-sensitive features have explicit notes in their lessons. Source/model checks and independent fixture arithmetic are not a DAX parser, compiler, semantic engine, real RLS test or performance measurement.

## Tutor guidance

Each guide ends with a prompt for `$guide-ds60sqlpy-learning`. The tutor reviews your draft and prediction, asks you to enumerate rows and context, and gives one progressive hint before any reference comparison. It must not claim to execute or compile DAX, connect to Power BI or mark mastery from a matching source string.
