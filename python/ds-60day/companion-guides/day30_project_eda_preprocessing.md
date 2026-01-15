# Day 30 — Project: EDA and Preprocessing (Companion Guide)

## Goal
Apply EDA and cleaning to a real dataset; produce a tidy training set and a brief report.

## Deliverables
- Reproducible notebook with clear sections and checkpoints
- Cleaned dataset with documented schema and dtypes
- Short write-up summarizing questions, findings, and next steps

## Suggested checklist
1) Define the problem and questions
2) Load data with explicit dtypes; validate schema
3) Profile nulls, dtypes, duplicates, outliers
4) Clean and transform: standardize strings, types, dates
5) Exploratory visuals; segment by key categories
6) Split train/test before target-aware transforms
7) Save processed dataset (Parquet) and data dictionary

## Stretch goals
- Parameterize the notebook (papermill) for multiple datasets
- Package transforms as functions and unit-test them
