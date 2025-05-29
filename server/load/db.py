from urllib.parse import urlparse

from utils.db import DatabasePool


def init_db(sql):
  try:
    parsed = urlparse(sql.data_source)
  except Exception as e:
    raise RuntimeError("failed to parse sql dsn", e)

  DatabasePool.initialize(
      host=parsed.hostname,
      dbname=parsed.path.lstrip("/"),
      user=parsed.username,
      password=parsed.password,
  )
