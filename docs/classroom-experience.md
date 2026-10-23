# Your classroom, your learning path

Start the local engine, run `./classroom` from the course folder, and use the
browser address it prints. The opening `/classroom` page is the home for every
subject. You can return to it whenever you want to change what you study.

## Choose a subject and a starting point

Python, PostgreSQL, the Python/PostgreSQL engineering bridge, statistics and
machine learning, C++, Java, JavaScript/TypeScript, Kubernetes, Scala/Spark,
TensorFlow, PyTorch, NLP, LLM theory and applied LLM systems all belong to the
same classroom. Subject names and individual color themes help you recognize
where you are. The name remains visible alongside the color.

Choose a beginner lesson when the vocabulary is new. Use prerequisites to
review a missing concept before a harder chapter. If you already know the
foundations, you can open an intermediate or advanced lesson directly. You
can follow one path, alternate complementary subjects, or pause a path and
return later. The historical sixty-day names are an ordering convention.
Estimated study times are planning aids, not deadlines or a required pace.

The [learning paths](learning-paths.md) suggest useful combinations. The
[LLM textbook route](learning/llm-textbook.md) connects 48 mechanism chapters
with 24 applied chapters. The statistics book is a reference as well as a
sequential course, so you can return to a method when a project needs it.

## Read the explanation and inspect the example

The lesson workspace contains its guide and the tools appropriate to that
lesson. Mathematical expressions use typeset fractions, powers, indices,
vectors and matrices. A formula is accompanied by its assumptions and symbol
definitions; rendering does not replace an explanation. Code blocks use their
stated language for syntax highlighting and remain copyable. Mathematical
rendering and highlighting use local resources, so reading needs no CDN.

Reading focus gives long explanations more space. You can switch back to the
coding view when an example calls for execution. Keep the example's declared
input, expected observation and limitation together. A small deterministic
calculation explains a mechanism; it does not establish a model's real-world
accuracy or a system's production capacity.

## Use the lesson's execution contract

The capability notice tells you what the selected lesson can run. A compiler
lesson, a PostgreSQL script, a notebook and a theory worksheet have different
requirements. Do not paste a whole notebook JSON document into a Python pad.
Read SQL preparation and transaction notes before running a script, and use
only the disposable course database. Kubernetes operations and optional model
downloads remain explicit, bounded lesson workflows.

C++ and Java compile before they run. Read compiler diagnostics from the first
error, make one correction, and run again. Node runs JavaScript; TypeScript
undergoes type checking and compilation first. Framework and Spark lessons
use their declared Docker workers. A readiness failure identifies an unavailable
runtime; it does not mean your written answer is wrong.

The default launcher prepares all ten ordinary workers. For a smaller build,
use `./classroom --starter` and follow a lesson's runtime preparation notice
when you need another profile. The [startup guide](one-command-classroom.md)
explains profile selection and how to see the real build logs.

## Keep your own evidence and pace

Save your code and notes before changing direction. For programming practice,
write a prediction, attempt the task, inspect its output and record what you
learned. Hints and separate solutions support comparison after an attempt.
The statistics and machine learning book is a tutorial: examples and interview
answers are complete, without exams, withheld answers or a prediction gate.

A progress marker is your record of study, not a certification of expertise.
You can revisit an earlier chapter or experiment with a new example whenever
it helps. Changing subjects does not rename the lesson or intentionally reset
its saved work. Old lesson identifiers remain stable through the UI migration.

The normal Docker classroom stores progress and working data in named Docker
volumes. `./classroom stop` preserves those volumes; rebuilding images also
preserves them. Deleting volumes is different from pruning unused images.
Follow [backup and transfer instructions](one-command-classroom.md) before
moving between machines or between the old host-folder workflow and the
standard Docker classroom.

## Existing bookmarks and offline reading

`/learn`, `/journeys` and `/journey-preview` are compatibility entrypoints for
the same classroom. Use `/classroom` in new bookmarks and documentation. A
previous subject or lesson identifier can still identify saved work even
though the opening page has changed.

`START_HERE.html` and the generated readers remain useful as a static offline
library. They cannot start a compiler or database from a browser file URL.
Native editor/Jupyter launchers are optional tools for a separately prepared
environment. They are not additional required steps after `./classroom`.
