CREATE TABLE IF NOT EXISTS payment_methods (
  id VARCHAR(26) PRIMARY KEY,
  user_id VARCHAR(26) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type VARCHAR(32) NOT NULL, -- 'card', 'paypal', 'apple', 'google'
  name VARCHAR(256) NOT NULL,
  last_four VARCHAR(4),
  expiry_date VARCHAR(5), -- MM/YY format
  token VARCHAR(512) NOT NULL, -- Encrypted/tokenized payment information
  is_default BOOLEAN NOT NULL DEFAULT FALSE,
  created_at BIGINT NOT NULL,
  updated_at BIGINT,
  deleted_at BIGINT
);

CREATE INDEX IF NOT EXISTS payment_methods_user_id_idx ON payment_methods (user_id);
CREATE INDEX IF NOT EXISTS payment_methods_user_id_deleted_idx ON payment_methods (user_id, deleted_at);
