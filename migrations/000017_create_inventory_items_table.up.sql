-- Table to track inventory levels for products/variants
CREATE TABLE IF NOT EXISTS inventory_items (
  id VARCHAR(26) PRIMARY KEY,
  product_id VARCHAR(26) NOT NULL,
  variant_id VARCHAR(26) NOT NULL,
  sku VARCHAR(255) NOT NULL,
-- Inventory available for new orders (quantity_total - quantity_reserved)
  quantity_available INT NOT NULL CHECK (quantity_available >= 0),
-- Inventory reserved for existing orders but not yet fulfilled
  quantity_reserved INT NOT NULL CHECK (quantity_reserved >= 0),
-- Total physical inventory you have in stock
  quantity_total INT NOT NULL CHECK (quantity_total >= 0),
  location_id VARCHAR(26), -- Optional: for multi-warehouse support
  metadata JSONB, -- Additional inventory data
  created_at BIGINT NOT NULL,
  updated_at BIGINT,
  FOREIGN KEY (product_id) REFERENCES products (id)
);
