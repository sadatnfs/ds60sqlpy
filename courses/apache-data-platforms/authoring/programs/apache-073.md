# Atlas apache-073 prepared command notebook

In the copied Atlas project, `client.py` reads credentials only from the untracked environment file and refuses an endpoint URL carrying a user, password, path or query. `plan` needs no credentials at all.

```bash
bash run.sh prepare
bash run.sh plan
```

With fixture credentials for a prepared owned server, `check` also repeats one type lookup with a deliberately wrong password and expects 401 or 403:

```bash
bash run.sh apply
bash run.sh check
```

Check requires an actual 401 or 403 for a deliberately invalid fixture credential. A valid-principal authorization comparison and actual denied data-engine query remain independent tests.

A rejected bad password shows that authentication works. It does not show what a valid but unprivileged user may do, and an Atlas metadata policy is not a data-engine denial.