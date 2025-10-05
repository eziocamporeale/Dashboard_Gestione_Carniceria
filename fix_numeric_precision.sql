-- Fix per errore numeric field overflow
-- Aumenta la precisione dei campi amount per supportare importi maggiori

-- Aggiorna tabella daily_income
ALTER TABLE daily_income 
ALTER COLUMN amount TYPE NUMERIC(10,2);

-- Aggiorna tabella daily_expenses  
ALTER TABLE daily_expenses
ALTER COLUMN amount TYPE NUMERIC(10,2);

-- Verifica le modifiche
SELECT 
    table_name,
    column_name,
    data_type,
    numeric_precision,
    numeric_scale
FROM information_schema.columns 
WHERE table_name IN ('daily_income', 'daily_expenses') 
AND column_name = 'amount'
ORDER BY table_name;

-- Test con un importo grande
INSERT INTO daily_expenses (
    date, amount, category, description, supplier, payment_method
) VALUES (
    '2025-01-05', 8498.42, 'Compra Carnes', 'Test importo grande', 'Test Supplier', 'Efectivo'
);

-- Se il test funziona, rimuovi il record di test
DELETE FROM daily_expenses WHERE description = 'Test importo grande';
