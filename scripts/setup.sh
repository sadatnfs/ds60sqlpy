#!/usr/bin/env sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "${script_dir}/.." && pwd)
cd "${repo_root}"

usage() {
  printf 'Usage: sh scripts/setup.sh [--advanced] [--dependency-mode auto|locked|project]\n'
}

profile=core
dependency_mode=auto
while [ "$#" -gt 0 ]; do
  case "$1" in
    --advanced) profile=advanced; shift ;;
    --dependency-mode)
      if [ "$#" -lt 2 ]; then usage >&2; exit 2; fi
      dependency_mode=$2
      shift 2
      ;;
    --help|-h) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done
case "$dependency_mode" in
  auto|locked|project) ;;
  *) usage >&2; exit 2 ;;
esac

# Never let an inherited uv environment setting select another project's
# environment. A uv executable inside the environment being synced is also
# unsuitable: exact synchronization may remove the running executable.
uv_path=$(command -v uv || true)
case "$uv_path" in
  "${repo_root}/.venv/"*) uv_path= ;;
esac
if [ "$dependency_mode" = auto ]; then
  if [ -n "$uv_path" ]; then dependency_mode=locked; else dependency_mode=project; fi
fi
if [ "$dependency_mode" = locked ] && [ -z "$uv_path" ]; then
  printf 'Locked mode requires uv installed outside .venv. Install uv, or choose --dependency-mode project.\n' >&2
  exit 1
fi

venv_python="${repo_root}/.venv/bin/python"
if [ -e "${repo_root}/.venv" ] || [ -L "${repo_root}/.venv" ]; then
  if [ ! -x "$venv_python" ] || ! "$venv_python" -c '
import sys
from pathlib import Path
valid = ((3, 11) <= sys.version_info[:2] < (3, 13)
         and Path(sys.prefix).resolve() == Path(sys.argv[1]).resolve()
         and sys.prefix != sys.base_prefix)
raise SystemExit(not valid)
' "${repo_root}/.venv"; then
    printf 'The existing .venv is not a usable local Python 3.11-3.12 environment.\n' >&2
    printf 'Preserve any work, rename this repository .venv, then rerun. It was not deleted automatically.\n' >&2
    exit 1
  fi
  printf 'Reusing %s\n' "$venv_python"
else
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
    printf 'A supported Python was not found. Install Python 3.12 (3.11 also works), then rerun.\n' >&2
    exit 1
  fi

  if ! "${bootstrap_python}" -m venv "${repo_root}/.venv"; then
    printf 'Could not create .venv. On Debian/Ubuntu install the matching python3.12-venv or python3.11-venv package.\n' >&2
    printf 'No environment was deleted. See docs/troubleshooting.md before repairing a partial .venv.\n' >&2
    exit 1
  fi
fi

# Core matches the Windows Core bootstrap and the packages checked by doctor.
extras=notebooks,data,quality,bridge,professional,sql-notebooks
if [ "${profile}" = advanced ]; then
  extras="${extras},ml,production,deep-learning,nlp,geo"
fi
printf 'Installing the %s profile (%s mode). This step needs network access unless its packages are cached.\n' "$profile" "$dependency_mode"
if [ "$dependency_mode" = locked ]; then
  set -- sync --locked --python "$venv_python"
  saved_ifs=$IFS
  IFS=,
  for extra in $extras; do set -- "$@" --extra "$extra"; done
  IFS=$saved_ifs
  UV_PROJECT_ENVIRONMENT="${repo_root}/.venv" UV_PYTHON="$venv_python" \
    "$uv_path" "$@"
else
  "${venv_python}" -m ensurepip --upgrade
  "${venv_python}" -m pip --disable-pip-version-check install -e ".[${extras}]"
fi

"${venv_python}" -m ipykernel install \
  --user \
  --name ds60sqlpy \
  --display-name "Python (ds60sqlpy)"
"${venv_python}" scripts/course.py doctor --no-database

printf '\nSetup complete. Start Jupyter with:\n'
printf '  .venv/bin/python -m jupyter lab\n'
printf 'Start the learning dashboard with:\n'
printf '  .venv/bin/python scripts/learning_portal.py\n'
printf 'No database was contacted or modified. Continue with your OS setup guide for SQL.\n'
