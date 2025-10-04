-- =====================================================
-- PULIZIA SICURA DATABASE - CON VERIFICA ESISTENZA TABELLE
-- Elimina solo le tabelle che esistono realmente
-- Creato da: Ezio Camporeale
-- Data: 2024-12-19
-- =====================================================

-- ATTENZIONE: Questa query eliminerà TUTTI i dati dalle tabelle esistenti
-- Non reinserisce nessun dato predefinito
-- Tutti i dati dovranno essere inseriti manualmente dall'utente

-- ==================== ELIMINAZIONE SICURA ====================

-- Tabelle principali del sistema (elimina solo se esistono)
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sale_items') THEN
        DELETE FROM sale_items;
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sales') THEN
        DELETE FROM sales;
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'customer_orders') THEN
        DELETE FROM customer_orders;
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'customers') THEN
        DELETE FROM customers;
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'suppliers') THEN
        DELETE FROM suppliers;
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'products') THEN
        DELETE FROM products;
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'product_categories') THEN
        DELETE FROM product_categories;
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'units_of_measure') THEN
        DELETE FROM units_of_measure;
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'employees') THEN
        DELETE FROM employees;
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'employee_shifts') THEN
        DELETE FROM employee_shifts;
    END IF;
    
    -- Tabelle contabilità giornaliera
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'daily_income') THEN
        DELETE FROM daily_income;
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'daily_expenses') THEN
        DELETE FROM daily_expenses;
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'daily_reports') THEN
        DELETE FROM daily_reports;
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'accounting_categories') THEN
        DELETE FROM accounting_categories;
    END IF;
    
    -- Tabelle dati importati e riepiloghi
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'excel_data') THEN
        DELETE FROM excel_data;
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'monthly_summary') THEN
        DELETE FROM monthly_summary;
    END IF;
    
    -- Tabelle log e attività
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'activity_log') THEN
        DELETE FROM activity_log;
    END IF;
    
    -- Tabelle utenti e ruoli
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_roles') THEN
        DELETE FROM user_roles;
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') THEN
        DELETE FROM users;
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'roles') THEN
        DELETE FROM roles;
    END IF;
    
    -- Tabelle impostazioni sistema
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'system_settings') THEN
        DELETE FROM system_settings;
    END IF;
    
    RAISE NOTICE 'Pulizia completata per tutte le tabelle esistenti';
END $$;

-- ==================== VERIFICA PULIZIA ====================
-- Mostra solo le tabelle che esistono realmente
SELECT 
    t.tablename as tabella,
    COALESCE(c.count, 0) as registri
FROM (
    SELECT tablename 
    FROM pg_tables 
    WHERE schemaname = 'public'
    AND tablename IN (
        'sale_items', 'sales', 'customer_orders', 'customers', 'suppliers',
        'products', 'product_categories', 'units_of_measure', 'employees',
        'employee_shifts', 'daily_income', 'daily_expenses', 'daily_reports',
        'accounting_categories', 'excel_data', 'monthly_summary', 'activity_log',
        'user_roles', 'users', 'roles', 'system_settings'
    )
) t
LEFT JOIN (
    SELECT 'sale_items' as tablename, COUNT(*) as count FROM sale_items
    UNION ALL SELECT 'sales', COUNT(*) FROM sales
    UNION ALL SELECT 'customer_orders', COUNT(*) FROM customer_orders
    UNION ALL SELECT 'customers', COUNT(*) FROM customers
    UNION ALL SELECT 'suppliers', COUNT(*) FROM suppliers
    UNION ALL SELECT 'products', COUNT(*) FROM products
    UNION ALL SELECT 'product_categories', COUNT(*) FROM product_categories
    UNION ALL SELECT 'units_of_measure', COUNT(*) FROM units_of_measure
    UNION ALL SELECT 'employees', COUNT(*) FROM employees
    UNION ALL SELECT 'employee_shifts', COUNT(*) FROM employee_shifts
    UNION ALL SELECT 'daily_income', COUNT(*) FROM daily_income
    UNION ALL SELECT 'daily_expenses', COUNT(*) FROM daily_expenses
    UNION ALL SELECT 'daily_reports', COUNT(*) FROM daily_reports
    UNION ALL SELECT 'accounting_categories', COUNT(*) FROM accounting_categories
    UNION ALL SELECT 'excel_data', COUNT(*) FROM excel_data
    UNION ALL SELECT 'monthly_summary', COUNT(*) FROM monthly_summary
    UNION ALL SELECT 'activity_log', COUNT(*) FROM activity_log
    UNION ALL SELECT 'user_roles', COUNT(*) FROM user_roles
    UNION ALL SELECT 'users', COUNT(*) FROM users
    UNION ALL SELECT 'roles', COUNT(*) FROM roles
    UNION ALL SELECT 'system_settings', COUNT(*) FROM system_settings
) c ON t.tablename = c.tablename
ORDER BY t.tablename;

-- ==================== MESSAGGIO FINALE ====================
SELECT '✅ PULIZIA SICURA COMPLETATA!' as messaggio,
       'Database pulito - Solo tabelle esistenti sono state pulite' as dettaglio;
