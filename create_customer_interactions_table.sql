-- Script per creare la tabella customer_interactions
-- Esegui questo script in Supabase SQL Editor

-- Crea la tabella customer_interactions
CREATE TABLE IF NOT EXISTS customer_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    description TEXT,
    outcome VARCHAR(100),
    notes TEXT,
    employee VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crea un indice per migliorare le performance
CREATE INDEX IF NOT EXISTS idx_customer_interactions_customer_id ON customer_interactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_interactions_date ON customer_interactions(date);

-- Aggiungi trigger per updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_customer_interactions_updated_at 
    BEFORE UPDATE ON customer_interactions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Verifica che la tabella sia stata creata
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'customer_interactions' 
ORDER BY ordinal_position;
