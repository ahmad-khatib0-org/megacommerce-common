CREATE TABLE IF NOT EXISTS categories (
  id VARCHAR(64) PRIMARY KEY,
  name VARCHAR(64) NOT NULL,
  image VARCHAR(256) NOT NULL,
  subcategories JSONB NOT NULL,
  translations JSONB NOT NULL,
  edits JSONB NOT NULL,
  version SMALLINT NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP
);
