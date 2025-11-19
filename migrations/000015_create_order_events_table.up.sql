-- ORDER EVENTS (audit / state changes / domain events)
CREATE TABLE IF NOT EXISTS order_events (
  id VARCHAR(26) PRIMARY KEY,
  order_id VARCHAR NOT NULL,
  event_type VARCHAR(32) NOT NULL, -- e.g., ORDER_CREATED, PAYMENT_CAPTURED
  event_payload JSONB NOT NULL, -- arbitrary payload with details
  created_at BIGINT NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders (id)
);

CREATE INDEX IF NOT EXISTS order_events_order_id_idx ON order_events (order_id);
