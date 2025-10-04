-- =====================================================
-- PULIZIA TABELLE BASE - SOLO TABELLE CERTE
-- Elimina dati dalle tabelle che sicuramente esistono
-- =====================================================

-- Mostra le tabelle esistenti
SELECT 'TABELLE DISPONIBILI:' as info;
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Elimina solo dalle tabelle base che dovrebbero esistere sempre
DELETE FROM sale_items;
DELETE FROM sales;
DELETE FROM customers;
DELETE FROM suppliers;
DELETE FROM products;
DELETE FROM product_categories;
DELETE FROM units_of_measure;
DELETE FROM employees;
DELETE FROM daily_income;
DELETE FROM daily_expenses;
DELETE FROM daily_reports;
DELETE FROM accounting_categories;
DELETE FROM excel_data;
DELETE FROM monthly_summary;
DELETE FROM activity_log;
DELETE FROM users;
DELETE FROM roles;
DELETE FROM system_settings;

-- Verifica finale
SELECT 'VERIFICA FINALE:' as info;
SELECT 'sale_items' as tabella, COUNT(*) as registri FROM sale_items
UNION ALL SELECT 'sales', COUNT(*) FROM sales
UNION ALL SELECT 'customers', COUNT(*) FROM customers
UNION ALL SELECT 'suppliers', COUNT(*) FROM suppliers
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'product_categories', COUNT(*) FROM product_categories
UNION ALL SELECT 'units_of_measure', COUNT(*) FROM units_of_measure
UNION ALL SELECT 'employees', COUNT(*) FROM employees
UNION ALL SELECT 'daily_income', COUNT(*) FROM daily_income
UNION ALL SELECT 'daily_expenses', COUNT(*) FROM daily_expenses
UNION ALL SELECT 'daily_reports', COUNT(*) FROM daily_reports
UNION ALL SELECT 'accounting_categories', COUNT(*) FROM accounting_categories
UNION ALL SELECT 'excel_data', COUNT(*) FROM excel_data
UNION ALL SELECT 'monthly_summary', COUNT(*) FROM monthly_summary
UNION ALL SELECT 'activity_log', COUNT(*) FROM activity_log
UNION ALL SELECT 'users', COUNT(*) FROM users
UNION ALL SELECT 'roles', COUNT(*) FROM roles
UNION ALL SELECT 'system_settings', COUNT(*) FROM system_settings
ORDER BY tabella;
