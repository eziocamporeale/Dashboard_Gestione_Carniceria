-- =====================================================
-- PULIZIA SICURA DATABASE DASHBOARD GESTIONE MACELLERIA
-- Versione: 1.0 (SICURA - Mantiene utenti e impostazioni)
-- Creato da: Ezio Camporeale
-- Data: $(date)
-- =====================================================

-- ATTENZIONE: Questa query eliminerà SOLO i dati operativi
-- MANTIENE: Utenti, ruoli, impostazioni sistema e dati base

-- ==================== DISABILITAZIONE TRIGGER ====================
-- Disabilita temporaneamente i trigger per evitare errori durante la pulizia
SET session_replication_role = replica;

-- ==================== ELIMINAZIONE DATI OPERATIVI ====================

-- Tabelle dati operativi (vendite, ordini, ecc.)
DELETE FROM sale_items;
DELETE FROM sales;
DELETE FROM customer_orders;  -- Tabella ordini clienti
DELETE FROM customers;
DELETE FROM suppliers;
DELETE FROM products;
DELETE FROM employee_shifts;

-- Tabelle contabilità giornaliera
DELETE FROM daily_income;
DELETE FROM daily_expenses;
DELETE FROM daily_reports;

-- Tabelle dati importati e riepiloghi
DELETE FROM excel_data;
DELETE FROM monthly_summary;

-- Tabelle log e attività
DELETE FROM activity_log;

-- ==================== MANTENIMENTO DATI BASE ====================
-- MANTIENE: product_categories, units_of_measure, accounting_categories
-- MANTIENE: employees (struttura), users, roles, system_settings

-- ==================== RIABILITAZIONE TRIGGER ====================
-- Riabilita i trigger
SET session_replication_role = DEFAULT;

-- ==================== VERIFICA PULIZIA ====================
-- Verifica che le tabelle operative siano vuote
SELECT 'sale_items' as tabella, COUNT(*) as registri FROM sale_items
UNION ALL
SELECT 'sales', COUNT(*) FROM sales
UNION ALL
SELECT 'customer_orders', COUNT(*) FROM customer_orders
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'suppliers', COUNT(*) FROM suppliers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'employee_shifts', COUNT(*) FROM employee_shifts
UNION ALL
SELECT 'daily_income', COUNT(*) FROM daily_income
UNION ALL
SELECT 'daily_expenses', COUNT(*) FROM daily_expenses
UNION ALL
SELECT 'daily_reports', COUNT(*) FROM daily_reports
UNION ALL
SELECT 'excel_data', COUNT(*) FROM excel_data
UNION ALL
SELECT 'monthly_summary', COUNT(*) FROM monthly_summary
UNION ALL
SELECT 'activity_log', COUNT(*) FROM activity_log
ORDER BY tabella;

-- ==================== VERIFICA DATI MANTENUTI ====================
-- Verifica che i dati base siano ancora presenti
SELECT 'product_categories' as tabella, COUNT(*) as registri FROM product_categories
UNION ALL
SELECT 'units_of_measure', COUNT(*) FROM units_of_measure
UNION ALL
SELECT 'accounting_categories', COUNT(*) FROM accounting_categories
UNION ALL
SELECT 'employees', COUNT(*) FROM employees
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'roles', COUNT(*) FROM roles
UNION ALL
SELECT 'system_settings', COUNT(*) FROM system_settings
ORDER BY tabella;

-- ==================== MESSAGGIO FINALE ====================
SELECT '✅ PULIZIA SICURA COMPLETATA!' as messaggio,
       'Dati operativi eliminati, struttura e utenti mantenuti' as dettaglio;
