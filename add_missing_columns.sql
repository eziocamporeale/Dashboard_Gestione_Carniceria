-- Aggiungere colonne mancanti alla tabella employees
-- Eseguire questo script se la tabella employees esiste ma mancano alcune colonne

-- Aggiungi colonna address se non esiste
ALTER TABLE employees 
ADD COLUMN IF NOT EXISTS address TEXT;

-- Aggiungi colonna contract_type se non esiste
ALTER TABLE employees 
ADD COLUMN IF NOT EXISTS contract_type VARCHAR(100) DEFAULT 'Tiempo Completo';

-- Aggiungi colonna emergency_contact se non esiste
ALTER TABLE employees 
ADD COLUMN IF NOT EXISTS emergency_contact TEXT;

-- Aggiungi colonna emergency_phone se non esiste
ALTER TABLE employees 
ADD COLUMN IF NOT EXISTS emergency_phone VARCHAR(50);

-- Aggiungi colonna notes se non esiste
ALTER TABLE employees 
ADD COLUMN IF NOT EXISTS notes TEXT;

-- Aggiungi colonna created_at se non esiste
ALTER TABLE employees 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Aggiungi colonna updated_at se non esiste
ALTER TABLE employees 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Verifica la struttura della tabella
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'employees' 
ORDER BY ordinal_position;

-- Mostra il numero di colonne
SELECT COUNT(*) as total_columns FROM information_schema.columns WHERE table_name = 'employees';
