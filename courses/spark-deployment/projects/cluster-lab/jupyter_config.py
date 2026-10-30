"""Private token is read inside the notebook container, not put in argv."""

from pathlib import Path

c = get_config()  # noqa: F821
c.ServerApp.ip = "0.0.0.0"
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.root_dir = "/notebooks"
c.ServerApp.allow_remote_access = False
c.ServerApp.log_level = "WARNING"
c.IdentityProvider.token = Path("/private/notebook-token").read_text().strip()
