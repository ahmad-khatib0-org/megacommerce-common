CREATE TABLE IF NOT EXISTS products (
  id VARCHAR(26) PRIMARY KEY,
  user_id VARCHAR NOT NULL,
  sku VARCHAR(64) NOT NULL,
  version SMALLINT NOT NULL DEFAULT 1,
  status VARCHAR(64) NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  slug TEXT NOT NULL,
  price NUMERIC(12, 3) NOT NULL,
  currency_code CHAR(3) NOT NULL,
  tags JSONB NOT NULL,
  metadata JSONB,
  ar_enabled BOOLEAN DEFAULT FALSE,
  created_at BIGINT NOT NULL,
  published_at BIGINT,
  updated_at BIGINT,
  FOREIGN KEY (user_id) REFERENCES users (id)
);
