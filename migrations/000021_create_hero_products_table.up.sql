CREATE TABLE IF NOT EXISTS hero_products (
  id VARCHAR(26) NOT NULL PRIMARY KEY,
  products_data JSONB NOT NULL,
  created_at BIGINT NOT NULL,
  updated_at BIGINT
);
