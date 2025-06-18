-- Idempotent table creation: 10 generic columns + created_at
CREATE TABLE IF NOT EXISTS public.records (
    id           BIGINT PRIMARY KEY,
    col2         TEXT  NOT NULL,
    col3         TEXT  NOT NULL,
    col4         TEXT  NOT NULL,
    col5         TEXT  NOT NULL,
    col6         TEXT  NOT NULL,
    col7         TEXT  NOT NULL,
    col8         TEXT  NOT NULL,
    col9         TEXT  NOT NULL,
    col10        TEXT  NOT NULL,
    created_at   TIMESTAMPTZ DEFAULT now()
);
