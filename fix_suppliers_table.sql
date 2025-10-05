
-- Script per correggere la tabella suppliers
-- Esegui questo script in Supabase SQL Editor

-- Aggiungi colonne mancanti alla tabella suppliers
ALTER TABLE suppliers 
ADD COLUMN IF NOT EXISTS notes TEXT;

ALTER TABLE suppliers 
ADD COLUMN IF NOT EXISTS phone VARCHAR(50);

ALTER TABLE suppliers 
ADD COLUMN IF NOT EXISTS address TEXT;

ALTER TABLE suppliers 
ADD COLUMN IF NOT EXISTS contact_person VARCHAR(255);

-- Verifica la struttura finale
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'suppliers' 
ORDER BY ordinal_position;
