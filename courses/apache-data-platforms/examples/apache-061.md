# Pinot apache-061 command notebook

`client.py` in the copied Pinot project holds every query the checker sends, and `run.sh check` runs it. Its `query` helper raises as soon as a broker response carries an `exceptions` entry, so a failed join cannot pass silently.

```bash
cat client.py
bash run.sh check
```

The default checker inspects response exceptions and bounded results. A multistage join needs the supported engine configured and separately qualified, with unique-dimension and duplicate-dimension oracles.

The multistage engine is outside the accepted Pinot gate. QUALIFICATION.md keeps multistage joins as a prepared extension, so a join receipt needs its own engine setting and both dimension oracles.