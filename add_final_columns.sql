-- Aggiungere le ultime 2 colonne mancanti alla tabella employees
-- Eseguire questo script per completare la tabella

-- Aggiungi colonna name (OBBLIGATORIA)
ALTER TABLE employees 
ADD COLUMN IF NOT EXISTS name VARCHAR(255) NOT NULL DEFAULT 'Sin Nombre';

-- Aggiungi colonna status
ALTER TABLE employees 
ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'Activo';

-- Verifica la struttura finale della tabella
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'employees' 
ORDER BY ordinal_position;

-- Mostra il numero totale di colonne
SELECT COUNT(*) as total_columns FROM information_schema.columns WHERE table_name = 'employees';

-- Test inserimento record di esempio
INSERT INTO employees (name, email, phone, position, department, salary, hire_date, status) 
VALUES ('Test Final', 'test.final@example.com', '+54 11 0000-0000', 'Test Position', 'Test Department', 1000.00, '2024-01-01', 'Activo')
ON CONFLICT (email) DO NOTHING;

-- Verifica che l'inserimento sia riuscito
SELECT COUNT(*) as total_employees FROM employees WHERE email = 'test.final@example.com';

-- Elimina il record di test
DELETE FROM employees WHERE email = 'test.final@example.com';

-- Conferma eliminazione
SELECT COUNT(*) as employees_after_cleanup FROM employees;
