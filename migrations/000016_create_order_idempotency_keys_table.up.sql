-- IDEMPOTENCY KEYS: map client idempotency_key -> order_id and status
CREATE TABLE IF NOT EXISTS order_idempotency_keys (
  id VARCHAR(26) PRIMARY KEY,
  idempotency_key TEXT NOT NULL UNIQUE,
  user_id VARCHAR NOT NULL,
  order_id VARCHAR, -- created order id if completed
  status VARCHAR(32) NOT NULL, -- IN_PROGRESS, COMPLETED, FAILED
  created_at BIGINT NOT NULL,
  updated_at BIGINT,
  expires_at BIGINT NOT NULL -- TTL: when key may be cleaned up
);

CREATE INDEX IF NOT EXISTS order_idempotency_keys_idempotency_key_idx ON order_idempotency_keys (idempotency_key);
