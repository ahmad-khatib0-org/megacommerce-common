CREATE TABLE IF NOT EXISTS users (
  id VARCHAR(26) PRIMARY KEY,
  username VARCHAR(256) NOT NULL UNIQUE,
  first_name VARCHAR(64),
  last_name VARCHAR(64),
  email VARCHAR(256) NOT NULL UNIQUE,
  user_type VARCHAR(24) NOT NULL,
  membership VARCHAR(24) NOT NULL,
  image VARCHAR(256),
  image_metadata JSONB,
  is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
  password VARCHAR(128) NOT NULL,
  auth_data VARCHAR(128),
  auth_service VARCHAR(32),
  roles TEXT[] NOT NULL,
  props JSONB,
  notify_props JSONB,
  last_password_update BIGINT,
  last_picture_update BIGINT,
  failed_attempts INT,
  locale VARCHAR(5),
  is_mfa_active BOOLEAN,
  mfa_secret VARCHAR(128),
  last_activity_at BIGINT,
  last_login BIGINT,
  created_at BIGINT NOT NULL,
  updated_at BIGINT,
  deleted_at BIGINT
);

CREATE INDEX IF NOT EXISTS users_email_idx ON users (email);

CREATE INDEX IF NOT EXISTS users_username_idx ON users (username);
