CREATE TABLE products (
    id          UUID PRIMARY KEY,
    name        TEXT NOT NULL,
    image_key   TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_product_created ON products (created_at DESC);
