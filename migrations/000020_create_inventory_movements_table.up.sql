-- Table to track inventory movements (for audit trail)
CREATE TABLE IF NOT EXISTS inventory_movements (
  id VARCHAR(26) PRIMARY KEY,
  inventory_item_id VARCHAR(26) NOT NULL,
  movement_type VARCHAR(32) NOT NULL, -- IN, OUT, ADJUSTMENT, RESERVATION, RELEASE
  quantity INT NOT NULL,
  reference_id VARCHAR(26), -- Can reference order_id, reservation_id, etc.
  reason VARCHAR(255),
  metadata JSONB,
  created_at BIGINT NOT NULL,
  FOREIGN KEY (inventory_item_id) REFERENCES inventory_items (id)
);
