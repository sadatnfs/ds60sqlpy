#!/usr/bin/env sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "${script_dir}/.." && pwd)
cd "${repo_root}"

profile=core
if [ "${1:-}" = "--advanced" ]; then
  profile=advanced
elif [ -n "${1:-}" ]; then
  printf 'Usage: sh scripts/setup.sh [--advanced]\n' >&2
  exit 2
fi

bootstrap_python=
for candidate in python3.12 python3.11 python3 python; do
  if command -v "${candidate}" >/dev/null 2>&1 \
    && "${candidate}" -c 'import sys; raise SystemExit(not ((3, 11) <= sys.version_info[:2] < (3, 13)))'
  then
    bootstrap_python=${candidate}
    break
  fi
done

if [ -z "${bootstrap_python}" ]; then
  printf 'Python was not found. Install Python 3.12, then rerun this script.\n' >&2
  exit 1
fi

"${bootstrap_python}" -m venv .venv
venv_python="${repo_root}/.venv/bin/python"
"${venv_python}" -m pip install --upgrade pip
"${venv_python}" -m pip install -e ".[notebooks,data,quality]"

if [ "${profile}" = advanced ]; then
  "${venv_python}" -m pip install -e ".[ml,production,bridge,deep-learning,nlp,geo]"
fi

"${venv_python}" -m ipykernel install \
  --user \
  --name ds60sqlpy \
  --display-name "Python (ds60sqlpy)"
"${venv_python}" scripts/course.py doctor

printf '\nSetup complete. Start Jupyter with:\n'
printf '  .venv/bin/python -m jupyter lab\n'
