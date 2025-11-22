-- Table to track inventory reservations
CREATE TABLE IF NOT EXISTS inventory_reservations (
  id VARCHAR(26) PRIMARY KEY,
  reservation_token VARCHAR(255) NOT NULL UNIQUE,
  order_id VARCHAR(26) NOT NULL,
  status VARCHAR(32) NOT NULL, -- ACTIVE, RELEASED, FULFILLED
  expires_at BIGINT NOT NULL, -- TTL for the reservation
  created_at BIGINT NOT NULL,
  updated_at BIGINT,
  FOREIGN KEY (order_id) REFERENCES orders (id)
);
