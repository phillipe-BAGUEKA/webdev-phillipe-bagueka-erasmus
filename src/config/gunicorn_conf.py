"""Gunicorn settings for the Render-provided HTTP port."""

import os

port = int(os.environ.get("PORT", "10000"))
if not 1 <= port <= 65535:
    raise ValueError("PORT must be between 1 and 65535.")

bind = f"0.0.0.0:{port}"
workers = 2
# Request paths can contain user data; keep the default access log disabled.
accesslog = None
errorlog = "-"
# The unneeded Gunicorn control socket defaults to $HOME, which this non-root
# image deliberately does not make writable.
control_socket_disable = True
