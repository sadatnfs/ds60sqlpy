# Learning paths, placement, and deliberate practice

> **Classroom entrypoint:** the browser opens `/classroom`, where Python, PostgreSQL,
> the engineering bridge and every module/book subject share one home and
> individually themed workspaces with saved code and notes.
> Start with `./classroom`; see the [classroom guide](classroom-experience.md) for reading, code,
> saved work and compatibility bookmarks.


The course has no sixty-day deadline. Its historical day IDs are stable navigation points. A named module may be a beginner practice lab, an intermediate foundation, or a multi-session advanced project. Progress comes from producing and explaining evidence, not from opening sixty files.

## Find a starting point

Use the [first-success guide](setup/first-success.md) before diagnosing a lesson. You should be able to run a small Python pad, find its output, rerun it from a fresh process, and explain the difference between the source file and the result. For SQL, you should be able to connect to the disposable database and identify its name without revealing a credential.

| Your current evidence | Starting route |
| --- | --- |
| You have not written a program | Python foundations, including the four confidence labs inserted around Days 1, 3, 8, and 10 |
| You have not queried a database | The three `sql-start` labs, then the historical SQL core |
| You know syntax but cannot diagnose failures | Trace state and debug-from-evidence practice before the next project |
| You can clean a file and explain rejected rows | Data analysis, then exact-value and calendar-boundary work |
| You can build and explain a model baseline | Machine learning with group/time evaluation and resampling |
| You write joins but cannot prove their totals | SQL bag reconciliation, fanout, and data-contract testing |
| You build applications and need safer changes | Application engineering, then the integrated data-product incident review |

Do a short placement exercise before skipping foundations. From a blank file, trace three assignments and predict the output; parse a numeric string while distinguishing blank from zero; write a function with an empty-input policy; and explain an actual exception from its traceback. For SQL, state a table's grain, distinguish `NULL` from zero, produce a stable ordering with a tie-breaker, and show a join fixture where duplicate child rows change a total. If you cannot show evidence for one of these, review its beginner guide before choosing an advanced route.

## Generate a real route

The route planner expands prerequisites from the generated catalog. A route definition names terminal goals only; it does not maintain a second lesson inventory. List available goals:

```text
python scripts/course.py plan
```

The browser classroom is the primary learner route. The commands below are
optional read-only contributor tools for the legacy Python/SQL/bridge graph:

```sh
uv run --no-sync python scripts/course.py plan --path python-foundations --weekly-hours 5
uv run --no-sync python scripts/course.py plan --path database-engineering --weekly-hours 6 --use-progress
uv run --no-sync python scripts/course.py plan python-ml-02 --json
```

Use the prepared interpreter from [CONTRIBUTING.md](../CONTRIBUTING.md), including
inside WSL 2. These CLI paths do not accept every modern module ID or read the
Docker volume implicitly. Modern subjects use their own manifest prerequisites
and the classroom's journey view; the MCP module tools expose those routes too.

Reading a plan does not write progress or execute examples. `--use-progress` explicitly reads local completion evidence and excludes those lessons. `[ready]` means that the recorded direct prerequisites are complete; it does not mean the environment has every optional dependency installed. The application offers the same goal-based route in its sidebar.

## Pace by sessions and checkpoints

A practical session is 45 to 90 minutes: retrieve the previous idea, predict a small result, run a worked example, attempt one change, and record the observation. Split long guides and projects across sessions. At five hours each week, even one core can extend over several months once review and independent exercises are included. The planner provides arithmetic from declared lesson estimates, not a guarantee about your learning speed.

After each session, write three short notes: what you predicted, what you actually observed, and what you will test next. Revisit a failed example the following day from a blank file. A week later, try an analogous input without opening the solution. This catches a common failure of tutorial study: recognizing an explanation while being unable to construct the behavior yourself.

For practice subjects, use four observations to judge readiness for the next phase:

1. Rebuild a small example from a blank file or query window.
2. Show a normal case, a boundary case, and one diagnosed failure.
3. Explain the rule and a tradeoff in your own words.
4. Identify the exact artifact or assertion that supports your explanation.

For Python foundations, that evidence is a small working program plus a clean run. For analysis, it includes row accounting, stated grain, null/duplicate policy, and a result that reconciles independently. For machine learning, it includes a baseline, an evaluation split that matches deployment, and a leakage check. For database engineering, it includes bounded work, an isolation or recovery argument, and a repeatable transcript. The integrated capstone adds a release decision, failure evidence, and a repair review.

## Go beyond the shared core

The [professional paths](professional-paths.md) retain packaging, concurrency, typed interfaces, HTTP reliability, Arrow/DuckDB, experiments, reproducible models, service operations, PostgreSQL security, migrations, recovery, temporal modelling, replication, extensions, and analytics engineering. These are separate lanes. You do not need to install every advanced library to learn core programming or querying.

The October additions concentrate on gaps that a broad survey often leaves behind: novice tracing and debugging; trustworthy records and a first investigation; Unicode, exact money and calendar boundaries; group/time leakage; restartable pipelines; SQL bag semantics, fanout, keyset pagination and concurrency traces; and an integrated incident review. Each has separate learner, guide, executable reference, and explanatory solution artifacts, with exercises that state inspectable results.

Use the catalog for the exact current modules, prerequisites, dependency groups, network labels, and file paths. Use [the classroom](classroom-experience.md) for guided practice, or [AI tutoring](mcp-tutor.md) if you want a conversational coach. The checked-in lessons remain sufficient without either.

Tutorial books, including statistics/ML, teach through complete worked examples
without mandatory exercises, exams or prediction gates. Read and revisit them at
a chosen schedule; reading markers record review status. Other language and systems
subjects have their own beginner entry points and explicit project/runtime boundaries.
Use the common subject chooser and the [documentation map](README.md) to explore them.

## Scientist and ML engineer specializations

Use [the maintained scientist roadmap](scientist-roadmap.md) for a route from
foundations through experimentation, applied scientific analysis, Bayesian
computation, data/ML engineering and LLM evaluation. It links the actual current
subjects instead of treating earlier planning proposals as missing features.
Choose the branch relevant to your work and follow its direct prerequisites;
no learner must complete every language first.
