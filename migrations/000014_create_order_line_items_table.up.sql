CREATE TABLE IF NOT EXISTS order_line_items (
  id VARCHAR(26) PRIMARY KEY, -- unique per line
  order_id VARCHAR NOT NULL, 
  product_id VARCHAR NOT NULL, 
  variant_id TEXT, 
  sku TEXT, 
  title TEXT, -- product title snapshot
  attributes JSONB, -- snapshot attributes map
  quantity INT NOT NULL CHECK (quantity > 0), 
  unit_price_cents BIGINT NOT NULL, -- charged price per unit at order time
  list_price_cents BIGINT, -- optional
  sale_price_cents BIGINT, -- optional
  discount_cents BIGINT, -- total discount applied to this line (all units)
  tax_cents BIGINT NOT NULL, -- tax for this line (total)
  total_cents BIGINT NOT NULL, -- (quantity * unit_price) - discount + tax
  applied_offer_ids TEXT[], -- array of applied offer/promotion ids
  product_snapshot JSONB, -- full product snapshot for audit/debug
  status VARCHAR(32) NOT NULL, -- CREATED, CONFIRMED, SHIPPED, CANCELLED, REFUNDED, ...
  shipping_cents BIGINT NOT NULL, -- shipping in cents
  estimated_delivery_date BIGINT NOT NULL, -- Unix timestamp in milliseconds
  created_at BIGINT NOT NULL, 
  updated_at BIGINT, 
  FOREIGN KEY(order_id) REFERENCES orders(id)
);

CREATE INDEX IF NOT EXISTS order_line_items_order_id_idx ON order_line_items (order_id);
