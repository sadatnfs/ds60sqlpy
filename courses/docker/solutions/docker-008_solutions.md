# docker-008: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-008.md).

## Exercise 1: Distinguish Compose interpolation from container environment.

**Expected answer:** Model rendering versus process input.

**Why:** A value used to choose a host port need not appear inside the container. Conversely, a container environment entry can be literal and independent of a host variable.

**Approach:** Ask who reads each value: Compose substitutes ${VAR} while rendering compose.yaml on the host, while the environment: block becomes input to the python process.

**Why this is correct:** Interpolation finishes before any container exists, so a ${HOST_PORT} used in ports never reaches server.py, and the literal APP_MESSAGE needs no host variable.

**A plausible wrong approach:** Exporting APP_MESSAGE in the host shell and expecting server.py to see it fails unless the model forwards it, because the container does not inherit the host shell.

**How to verify:** docker compose config prints the rendered model with substitutions applied, and the GET / response shows the APP_MESSAGE string the process actually received.

## Exercise 2: Predict the type of APP_MESSAGE.

**Expected answer:** A string, even when its contents look numeric.

**Why:** Environment values do not carry a native integer or Boolean type. The application must parse and validate domain-specific meanings before using them.

**Approach:** Follow the value into server.py, which reads os.environ.get("APP_MESSAGE") and places it straight into the JSON response.

**Why this is correct:** The process environment is a list of byte strings. Setting APP_MESSAGE to 42 still delivers the characters 4 and 2, and the JSON message field is a string.

**A plausible wrong approach:** Expecting a YAML integer such as APP_MESSAGE: 42 to arrive as a number fails, because Compose converts the value to text before starting the process.

**How to verify:** Run worked example 2 with -e APP_MESSAGE=42 and print type(os.environ['APP_MESSAGE']); python reports str.

## Exercise 3: Design defaults and validation for a timeout variable.

**Expected evidence:** A documented default plus finite positive bounded numeric parsing.

**Why:** Configuration is external input. Rejecting malformed or excessive values at startup gives a clearer failure than a later hang caused by an unintended timeout.

**Approach:** Define REQUEST_TIMEOUT_SECONDS with a documented default, parse it as a number at startup, and reject values that are not finite or fall outside a stated range.

**Why this is correct:** Validating once at startup makes a bad deployment fail immediately with a clear message, before any request depends on a zero, negative or huge timeout.

**A plausible wrong approach:** Passing the raw string to a socket timeout fails late and unclearly: an empty value raises inside a request, and 99999 silently turns a stuck call into a hang.

**How to verify:** Start the container with a missing, valid, nonnumeric and oversized value in turn; only the default and the valid value reach a ready /healthz.

## Exercise 4: Diagnose an exec array containing literal $PORT.

**Expected answer:** No shell expansion occurs in an argument array.

**Why:** The runtime passes the characters directly. Add explicit application parsing rather than introducing a shell merely to conceal that the command contract was misunderstood.

**Approach:** Read the exec array ["python", "server.py", "--port", "$PORT"] literally: each element goes to the program as written, with no shell in between.

**Why this is correct:** Only a shell expands $PORT. In exec form the program receives the five characters $PORT, so it must read os.environ itself.

**A plausible wrong approach:** Switching to the shell form just to expand one variable makes /bin/sh the parent process and can block SIGTERM from reaching python.

**How to verify:** Print sys.argv inside the container for the exec form; the last element is the literal $PORT, confirming that no expansion happened.

## Exercise 5: Explain why restart may not apply changed Compose environment.

**Expected answer:** Existing container configuration and recreation differ.

**Why:** Restart starts the same configured object again. Applying a changed service model may require recreation, so confirm the observed environment and container identity.

**Approach:** Separate the edited YAML from the container's stored configuration: docker compose restart restarts the existing container with the environment it was created with.

**Why this is correct:** Environment is fixed at container creation. docker compose up -d compares the model with the running container and recreates the service when they differ.

**A plausible wrong approach:** Running restart repeatedly and concluding the app ignores configuration fails, because the new value never reached a container.

**How to verify:** After docker compose up -d, ps -q app prints a new container ID and GET / returns the edited message.

## Exercise 6: Write a public configuration evidence record.

**Expected evidence:** Name, safe synthetic value, source of override and observed response.

**Why:** Evidence should prove the intended precedence without leaking secrets. A response demonstrating the public message connects model rendering to actual application behavior.

**Approach:** Record the variable name, a synthetic value, where it was set (compose.yaml, an override file or -e), the container ID and the response body.

**Why this is correct:** Those fields link the configured source to the observed application output, and a public greeting can be logged without exposing anything private.

**A plausible wrong approach:** Pasting a real API token as the sample value proves precedence just as well but copies a secret into notes, screenshots and shell history.

**How to verify:** Someone else can repeat the record: change the value at the stated source, recreate, and see the same message in the JSON response.

## Check your transfer

In the first run, arguments after the image name replace CMD, so the container runs `python server.py --port 9090`; the entrypoint stays. In the second, `--entrypoint python` replaces the entrypoint, and setting the entrypoint also resets the default CMD, so the container runs `python -V` and prints a version instead of starting the server. `docker inspect` on each container shows the effective `Path` and `Args`. If the second container started the server, the entrypoint override was not applied, perhaps because it was placed after the image name, where it becomes an argument instead.
