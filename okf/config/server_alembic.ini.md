---
type: Configuration
description: "[alembic]"
resource: server/alembic.ini
timestamp: 2026-07-09T13:54:49Z
---

# alembic

Source path: `server/alembic.ini`

## Content

```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql+asyncpg://remember:bk7BuKoRou1pmZUkXm3dDQm9TSZpxNhDyd6QiR0BZJqEVGaURbl8eF0AP3e7XAux@remember-db-rw.remember.svc.cluster.local:5432/remember

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S

```
