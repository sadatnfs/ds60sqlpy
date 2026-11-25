# Pinot apache-059 command notebook

In the copied Pinot project, `table.json` declares an inverted index on `region` and a range index on `amount`. `run.sh check` then sends the selective query `region = 'east' AND amount >= 5` and accepts only the single ID 3.

```bash
cat table.json
bash run.sh check
```

The configuration prepares inverted/range indexes. The checker establishes exact selective-query results. Build separately named indexed/unindexed tables and inspect actual plans before asserting a performance difference.

The accepted Pinot gate proves the selective answer, not a speedup. QUALIFICATION.md names the indexed versus unindexed plan comparison as a separate gate that has not run.