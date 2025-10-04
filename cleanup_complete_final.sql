-- =====================================================
-- PULIZIA COMPLETA DATABASE - SOLO ELIMINAZIONE
-- Elimina TUTTI i dati senza reinserire nulla
-- Creato da: Ezio Camporeale
-- Data: 2024-12-19
-- =====================================================

-- ATTENZIONE: Questa query eliminerà TUTTI i dati dal database
-- Non reinserisce nessun dato predefinito
-- Tutti i dati dovranno essere inseriti manualmente dall'utente

-- ==================== ELIMINAZIONE COMPLETA ====================

-- Tabelle principali del sistema
DELETE FROM sale_items;
DELETE FROM sales;
DELETE FROM customer_orders;
DELETE FROM customers;
DELETE FROM suppliers;
DELETE FROM products;
DELETE FROM product_categories;
DELETE FROM units_of_measure;
DELETE FROM employees;
DELETE FROM employee_shifts;

-- Tabelle contabilità giornaliera
DELETE FROM daily_income;
DELETE FROM daily_expenses;
DELETE FROM daily_reports;
DELETE FROM accounting_categories;

-- Tabelle dati importati e riepiloghi
DELETE FROM excel_data;
DELETE FROM monthly_summary;

-- Tabelle log e attività
DELETE FROM activity_log;

-- Tabelle utenti e ruoli
DELETE FROM user_roles;
DELETE FROM users;
DELETE FROM roles;

-- Tabelle impostazioni sistema
DELETE FROM system_settings;

-- ==================== VERIFICA PULIZIA ====================
-- Verifica che TUTTE le tabelle siano completamente vuote
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
SELECT 'product_categories', COUNT(*) FROM product_categories
UNION ALL
SELECT 'units_of_measure', COUNT(*) FROM units_of_measure
UNION ALL
SELECT 'employees', COUNT(*) FROM employees
UNION ALL
SELECT 'employee_shifts', COUNT(*) FROM employee_shifts
UNION ALL
SELECT 'daily_income', COUNT(*) FROM daily_income
UNION ALL
SELECT 'daily_expenses', COUNT(*) FROM daily_expenses
UNION ALL
SELECT 'daily_reports', COUNT(*) FROM daily_reports
UNION ALL
SELECT 'accounting_categories', COUNT(*) FROM accounting_categories
UNION ALL
SELECT 'excel_data', COUNT(*) FROM excel_data
UNION ALL
SELECT 'monthly_summary', COUNT(*) FROM monthly_summary
UNION ALL
SELECT 'activity_log', COUNT(*) FROM activity_log
UNION ALL
SELECT 'user_roles', COUNT(*) FROM user_roles
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'roles', COUNT(*) FROM roles
UNION ALL
SELECT 'system_settings', COUNT(*) FROM system_settings
ORDER BY tabella;

-- ==================== MESSAGGIO FINALE ====================
SELECT '✅ PULIZIA COMPLETA TERMINATA!' as messaggio,
       'Database completamente vuoto - Pronto per inserimento dati manuale' as dettaglio;
