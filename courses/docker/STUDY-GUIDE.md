# Docker study guide: how every lesson works

Each Docker lesson links here instead of repeating the same operating rules. Read this page once
before docker-001 and return to the section a lesson names when you need it. The lessons
themselves keep the teaching that is specific to one chapter: its mental model, worked examples,
host lab, exercises, diagnosis and transfer case.

## Host-lab setup

The classroom displays each guide and saves your worksheet under `courses/docker/lessons/`. Its
Run button does not control a Docker engine. Engine access is powerful host access, so the
classroom deliberately receives no engine socket. Work through the worked examples by reading and
predicting first. Reading a command, parsing YAML and actually running the project are different
forms of evidence, and a worksheet should say which one it contains.

The optional host lab runs only on your own machine, in your own disposable project:

- Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs
  Linux containers.
- The maintained fixture is [`fixtures/compose-lab/`](fixtures/compose-lab/README.md). Its README
  explains copying it into a new ignored learner directory, checking the engine, building locally
  with visible logs, and using the fixed project name `ds60-docker-study` on host loopback port
  18080.
- Stop if that project name or port belongs to unrelated work. Choose a new project name and port
  consistently in your own copy instead of stopping someone else's service.
- Never run a command against a remote Docker context simply because it is currently selected.
  Check `docker context show` before anything that creates, stops or deletes objects.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets
describe a fragment unless a lesson calls them a complete file. Text transcripts in the guides are
synthetic illustrations, not claims about your machine. Do not substitute a real password, token
or private registry into an example you keep in a repository.

## Exercise rules

Each lesson has six progressive exercises. Before changing anything, name the object involved
(image, container, volume, network, project, registry reference) and the phase of its lifetime
(build, create, start, run, stop, remove). Then vary only the condition the exercise names, so one
observation answers one question.

Exercises that ask you to predict, explain, compare, classify or diagnose keep their answers in
the lesson's solutions file. The guide shows only the prompt and a hint for those. Exercises that
ask you to produce something show the evidence to look for in the guide, because you can check
that evidence yourself.

Write a prediction in the worksheet before any optional host run. Keep the exact project name,
engine identity and timestamps next to any runtime observation, and record failures as carefully
as successes.

## Safety rules

These rules hold in every lesson, including when an example fails and you are tempted to force it
through:

- Preserve the original failure and the exact field you changed before retrying.
- Do not make a container privileged, mount the engine socket, disable all checks or delete every
  volume to make an example succeed. Each of those hides the evidence the lesson is about and can
  damage unrelated work on the same engine.
- Do not publish a port on all interfaces when loopback is enough, and do not push an image to a
  registry unless a lesson explicitly asks you to and you own that repository.

## Retrieval and cleanup

Each lesson ends with a retrieval prompt and a transfer case. Close the guide and the solutions
before answering. Then reconstruct one worked example with a single changed value, predict what
changes, and name which of the lesson's concepts the change touches. Compare with the solutions
only after you have written your own answer, and record any gap as a question for the next study
session.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy.
It removes the project's containers and network but keeps named volumes. Deleting a volume is a
separate, deliberate reset described in the fixture README; do it only when a lesson asks for a
fresh counter or you no longer need the data.

## Solutions and the AI tutor

Solutions explain the supplied teaching fixtures; they are not engine results from your machine.
Compare with them only after your own attempt or an explicit reveal. Each solution ends with a
transfer answer that names the object, the phase when a setting takes effect, the expected normal
result and an observation that would disprove it. A production system additionally needs ownership,
lifecycle, data recovery and operational review, which no single lesson claims to provide.

Every guide ends with a copyable AI tutor prompt. It asks the tutor to coach one hint at a time,
to keep `courses/docker/solutions/` closed until you attempt or ask, and never to execute host
commands, change Docker contexts or delete volumes on your behalf.
