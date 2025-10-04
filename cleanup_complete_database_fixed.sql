-- =====================================================
-- PULIZIA COMPLETA DATABASE DASHBOARD GESTIONE MACELLERIA
-- Versione: 1.0 FIXED
-- Creato da: Ezio Camporeale
-- Data: 2024-12-19
-- =====================================================

-- ATTENZIONE: Questa query eliminerà TUTTI i dati dal database
-- Eseguire solo se si è sicuri di voler pulire completamente la dashboard

-- ==================== DISABILITAZIONE TRIGGER ====================
-- Disabilita temporaneamente i trigger per evitare errori durante la pulizia
SET session_replication_role = replica;

-- ==================== ELIMINAZIONE DATI DAI TABELLE ====================

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

-- Tabelle utenti e ruoli (versioni alternative)
DELETE FROM user_roles;

-- Tabelle utenti e ruoli (mantenere solo admin se necessario)
-- ATTENZIONE: Decommentare solo se si vogliono eliminare anche gli utenti
-- DELETE FROM users WHERE role_id != '00000000-0000-0000-0000-000000000001';
-- DELETE FROM roles WHERE id != '00000000-0000-0000-0000-000000000001';

-- Tabelle impostazioni sistema (mantenere le impostazioni base)
-- DELETE FROM system_settings WHERE key NOT IN ('app_name', 'app_version', 'currency', 'timezone');

-- ==================== RIABILITAZIONE TRIGGER ====================
-- Riabilita i trigger
SET session_replication_role = DEFAULT;

-- ==================== VERIFICA PULIZIA ====================
-- Verifica che tutte le tabelle siano vuote
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
ORDER BY tabella;

-- ==================== REINSERIMENTO DATI BASE ====================
-- Reinserisce le categorie di prodotti predefinite
INSERT INTO product_categories (id, name, description, color) VALUES 
('00000000-0000-0000-0000-000000000101', 'Carnes', 'Carnes frescas', '#DC3545'),
('00000000-0000-0000-0000-000000000102', 'Aves', 'Pollo y otras aves', '#FFC107'),
('00000000-0000-0000-0000-000000000103', 'Embutidos', 'Embutidos y fiambres', '#6F42C1'),
('00000000-0000-0000-0000-000000000104', 'Pescados', 'Pescados frescos', '#17A2B8'),
('00000000-0000-0000-0000-000000000105', 'Verduras', 'Verduras frescas', '#28A745'),
('00000000-0000-0000-0000-000000000106', 'Otros', 'Otros productos', '#6C757D')
ON CONFLICT (id) DO NOTHING;

-- Reinserisce le unità di misura predefinite
INSERT INTO units_of_measure (id, name, symbol, description) VALUES 
('00000000-0000-0000-0000-000000000201', 'Kilogramo', 'kg', 'Peso en kilogramos'),
('00000000-0000-0000-0000-000000000202', 'Gramo', 'g', 'Peso en gramos'),
('00000000-0000-0000-0000-000000000203', 'Unidad', 'un', 'Cantidad en unidades'),
('00000000-0000-0000-0000-000000000204', 'Libra', 'lb', 'Peso en libras'),
('00000000-0000-0000-0000-000000000205', 'Onza', 'oz', 'Peso en onzas')
ON CONFLICT (id) DO NOTHING;

-- Reinserisce le categorie contabili predefinite
INSERT INTO accounting_categories (name, type, color, icon) VALUES
('Ventas Carnes', 'income', '#00CC96', '🥩'),
('Ventas Embutidos', 'income', '#00CC96', '🌭'),
('Ventas Pollo', 'income', '#00CC96', '🐔'),
('Ventas Varios', 'income', '#00CC96', '🛒'),
('Otros Ingresos', 'income', '#00CC96', '💰'),
('Compra Carnes', 'expense', '#FF6692', '🥩'),
('Compra Embutidos', 'expense', '#FF6692', '🌭'),
('Compra Pollo', 'expense', '#FF6692', '🐔'),
('Gastos Operativos', 'expense', '#FF6692', '⚙️'),
('Servicios Públicos', 'expense', '#FF6692', '💡'),
('Alquiler', 'expense', '#FF6692', '🏠'),
('Sueldos', 'expense', '#FF6692', '👥'),
('Otros Gastos', 'expense', '#FF6692', '💸')
ON CONFLICT (name) DO NOTHING;

-- ==================== VERIFICA FINALE ====================
-- Verifica finale che i dati base siano stati reinseriti
SELECT 'product_categories' as tabella, COUNT(*) as registri FROM product_categories
UNION ALL
SELECT 'units_of_measure', COUNT(*) FROM units_of_measure
UNION ALL
SELECT 'accounting_categories', COUNT(*) FROM accounting_categories
ORDER BY tabella;

-- ==================== MESSAGGIO FINALE ====================
SELECT '✅ PULIZIA COMPLETATA CON SUCCESSO!' as messaggio,
       'Database pulito e pronto per nuovi dati' as dettaglio;
