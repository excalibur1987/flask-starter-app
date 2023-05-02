import os

import toml

bind = f"unix:///tmp/{toml.load(os.path.join(os.getcwd(),'pyproject.toml')).get('tool',{}).get('poetry',{}).get('name')}-nginx.socket"

workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 90
keepalive = 2

errorlog = "-"
loglevel = "info"
accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
