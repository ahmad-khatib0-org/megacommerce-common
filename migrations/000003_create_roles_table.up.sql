CREATE TABLE IF NOT EXISTS roles (
  name VARCHAR(64) NOT NULL UNIQUE,
  display_name VARCHAR(256) NOT NULL,
  description VARCHAR(1024) NOT NULL,
  permissions TEXT[] NOT NULL,
  builtin BOOLEAN NOT NULL,
  created_at BIGINT NOT NULL,
  updated_at BIGINT,
  deleted_at BIGINT
);
