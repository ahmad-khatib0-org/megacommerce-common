CREATE TABLE IF NOT EXISTS orders (
  id VARCHAR(26) PRIMARY KEY, -- order id 
  user_id UUID NOT NULL,
  currency_code VARCHAR(3) NOT NULL, -- ISO 4217 e.g. "USD"
  subtotal_cents BIGINT NOT NULL, -- subtotal in cents
  shipping_cents BIGINT NOT NULL, -- shipping in cents
  tax_cents BIGINT NOT NULL, -- tax in cents
  discount_cents BIGINT NOT NULL, -- discounts applied to order
  total_cents BIGINT NOT NULL, -- grand total in cents
  payment_provider VARCHAR(64) NOT NULL, -- e.g., "stripe"
  payment_transaction_id TEXT NOT NULL, -- gateway charge id
  payment_status VARCHAR(32) NOT NULL, -- AUTHORIZED/CAPTURED/FAILED/UNKNOWN
  payment_provider_response JSONB NOT NULL, -- tokenized provider response for audit
  payment_fee_cents BIGINT NOT NULL, -- gateway fee
  inventory_reservation_status VARCHAR(32) NOT NULL, -- RESERVED/PARTIAL/NOT_RESERVED/PENDING/UNKNOWN
  product_source TEXT NOT NULL, -- product service name/version used
  shipping_address JSONB NOT NULL, -- snapshot of shipping address
  billing_address JSONB NOT NULL, -- snapshot of billing address
  metadata JSONB, -- free-form metadata map
  status VARCHAR(32) NOT NULL, -- CREATED, CONFIRMED, SHIPPED, CANCELLED, REFUNDED, ...
  created_at BIGINT NOT NULL, -- epoch ms
  updated_at BIGINT,
  deleted_at BIGINT
);

-- INDEXES for common queries
CREATE INDEX IF NOT EXISTS orders_user_created_idx ON orders (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS orders_status_created_idx ON orders (status, created_at DESC);
