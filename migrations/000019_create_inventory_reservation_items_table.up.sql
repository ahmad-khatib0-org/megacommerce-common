-- Table to track individual items in a reservation
CREATE TABLE IF NOT EXISTS inventory_reservation_items (
  id VARCHAR(26) PRIMARY KEY,
  reservation_id VARCHAR(26) NOT NULL,
  inventory_item_id VARCHAR(26) NOT NULL,
  quantity INT NOT NULL CHECK (quantity > 0),
  created_at BIGINT NOT NULL,
  FOREIGN KEY (reservation_id) REFERENCES inventory_reservations (id),
  FOREIGN KEY (inventory_item_id) REFERENCES inventory_items (id)
);
