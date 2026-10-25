# Your first successful classroom session

You can begin without knowing Python, SQL or Git. The first goal is modest:
open the classroom, run one Python example, run one SQL query, save a draft
and return to it after stopping the containers.

## Prepare the host once

Follow the guide for [Windows with WSL 2](windows.md),
[macOS](macos.md) or [Linux](linux.md). Start the Linux-container engine and open
a Bash terminal in the extracted course directory. On Windows, use Ubuntu in
WSL 2 for the course commands.

| Term | Meaning here |
| --- | --- |
| Course folder | The source files, guides and launcher you downloaded |
| Docker image | Prepared application code and dependencies |
| Container | A running or stopped instance created from an image |
| Runtime profile | The prepared environment a lesson needs, such as Python or C++ |
| Named volume | Engine-managed storage retained across container replacement |
| Browser pad | Your editable source for the selected lesson and language |
| Saved run | The source and output recorded for a particular execution |

## Open a small first classroom

```sh
./classroom doctor
./classroom --starter
```

The first command checks prerequisites. The second prepares the app, PostgreSQL
and Python Core, then prints and opens the actual local URL. A new bare
`./classroom` prepares the full ordinary set instead. Both choices keep every
subject readable. Read the build output and wait for the ready address.

If execution permissions were lost during ZIP extraction, use `bash classroom`
in place of `./classroom`. If the browser does not open, copy the printed URL.
Use `./classroom status` to retrieve it later.

## Run Python in its own workspace

1. Choose **Python and data science** and its first lesson.
2. Read the guide. Use **Show code and notes** if reading focus hides the pad.
3. Keep the starter or save a copy before replacing its text for this small
   experiment.
4. Enter this ordinary Python program:

```python
learner = "Ada"
study_minutes = 20
print(f"Hello, {learner}. Today I studied for {study_minutes} minutes.")
print(2 + 3)
```

5. Predict the output, then choose **Run code**. Expect the greeting and `5`.
6. Add a note explaining which values changed and choose **Save work**. Wait for
   the saved confirmation before closing the page.

A Run starts a fresh process. A variable from an earlier Run is not still in
memory, so retain the definitions you need in the source. Notebook-style
`# %%` cells share state within a single Run; the next Run starts over.
Do not paste an entire `.ipynb` JSON file into the pad.

## Run a first SQL query

Switch to **PostgreSQL** and start with `sql-start-01`. Choose **SQL snippet**
when the workspace offers a mode selector and enter:

```sql
SELECT 1 AS first_result, 2 + 3 AS total;
```

Expect one row with `first_result = 1` and `total = 5`. This query needs no
training-table reset. The Docker classroom supplies its local database
connection; you do not need a host database or a password in the SQL pad.

Continue through `sql-start-02` and `sql-start-03` before `sql-01`.
When a later lesson needs the training schema, read its setup instructions.
Resetting that schema replaces course data and is a deliberate action, not a
routine startup step.

## Save, switch and inspect history

Return to the Python lesson. Its draft and notes should still be separate from
SQL. **Saved runs** displays a run's recorded source and output without running
it again or replacing your current edit. A run can describe an older source
version than the draft you are currently editing.

Python/SQL workspaces also expose earlier saved pad versions where supported.
Copying or restoring source is different from reading past output. Follow the
button's description before choosing either action.

## Stop and resume

After saving, return to the terminal:

```sh
./classroom stop
./classroom resume
```

Stopping keeps named volumes. Resume uses prepared images without rebuilding
or pulling. Open the newly printed URL and return to the same lessons.
If you chose a custom project, repeat its name on both commands, for example
`./classroom resume --project my-study`.

Your course folder, installed images and saved learning volumes are separate.
Keep the same engine and project. Copying a checkout or a ZIP alone does not
copy saved progress.

## Choose the next useful step

Open **All learning paths** or use **Switch subject**. Pick a beginner lesson,
review a prerequisite or combine complementary paths. HTML/CSS and browser
JavaScript/D3 can use the optional Live preview studio; PHP, compiled
languages and framework lessons use their declared workers. A missing worker
has setup instructions in the capability notice.

Use the [classroom guide](../classroom-experience.md) for study habits and
preview controls, and the [one-command guide](../one-command-classroom.md)
for updates, profiles, backups and recovery. A completed example is a starting
point for learning, not a certification of mastery.
