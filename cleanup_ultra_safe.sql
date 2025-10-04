-- =====================================================
-- PULIZIA ULTRA SICURA - SOLO TABELLE ESISTENTI
-- Elimina solo i dati dalle tabelle che esistono realmente
-- =====================================================

-- Prima mostra quali tabelle esistono
SELECT 'TABELLE ESISTENTI NEL DATABASE:' as info;

SELECT tablename as tabella_esistente
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- Ora elimina i dati solo dalle tabelle che esistono
DO $$
DECLARE
    table_exists boolean;
BEGIN
    -- Sale items
    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sale_items') INTO table_exists;
    IF table_exists THEN
        DELETE FROM sale_items;
        RAISE NOTICE 'Eliminati dati da sale_items';
    END IF;
    
    -- Sales
    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sales') INTO table_exists;
    IF table_exists THEN
        DELETE FROM sales;
        RAISE NOTICE 'Eliminati dati da sales';
    END IF;
    
    -- Customers
    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'customers') INTO table_exists;
    IF table_exists THEN
        DELETE FROM customers;
        RAISE NOTICE 'Eliminati dati da customers';
    END IF;
    
    -- Suppliers
    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'suppliers') INTO table_exists;
    IF table_exists THEN
        DELETE FROM suppliers;
        RAISE NOTICE 'Eliminati dati da suppliers';
    END IF;
    
    -- Products
    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'products') INTO table_exists;
    IF table_exists THEN
        DELETE FROM products;
        RAISE NOTICE 'Eliminati dati da products';
    END IF;
    
    -- Product categories
    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'product_categories') INTO table_exists;
    IF table_exists THEN
        DELETE FROM product_categories;
        RAISE NOTICE 'Eliminati dati da product_categories';
    END IF;
    
    -- Units of measure
    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'units_of_measure') INTO table_exists;
    IF table_exists THEN
        DELETE FROM units_of_measure;
        RAISE NOTICE 'Eliminati dati da units_of_measure';
    END IF;
    
    -- Employees
    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'employees') INTO table_exists;
    IF table_exists THEN
        DELETE FROM employees;
        RAISE NOTICE 'Eliminati dati da employees';
    END IF;
    
    -- Employee shifts
    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'employee_shifts') INTO table_exists;
    IF table_exists THEN
        DELETE FROM employee_shifts;
        RAISE NOTICE 'Eliminati dati da employee_shifts';
    END IF;
    
    -- Daily income
    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'daily_income') INTO table_exists;
    IF table_exists THEN
        DELETE FROM daily_income;
        RAISE NOTICE 'Eliminati dati da daily_income';
    END IF;
    
    -- Daily expenses
    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'daily_expenses') INTO table_exists;
    IF table_exists THEN
        DELETE FROM daily_expenses;
        RAISE NOTICE 'Eliminati dati da daily_expenses';
    END IF;
    
    -- Daily reports
    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'daily_reports') INTO table_exists;
    IF table_exists THEN
        DELETE FROM daily_reports;
        RAISE NOTICE 'Eliminati dati da daily_reports';
    END IF;
    
    -- Accounting categories
    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'accounting_categories') INTO table_exists;
    IF table_exists THEN
        DELETE FROM accounting_categories;
        RAISE NOTICE 'Eliminati dati da accounting_categories';
    END IF;
    
    -- Excel data
    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'excel_data') INTO table_exists;
    IF table_exists THEN
        DELETE FROM excel_data;
        RAISE NOTICE 'Eliminati dati da excel_data';
    END IF;
    
    -- Monthly summary
    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'monthly_summary') INTO table_exists;
    IF table_exists THEN
        DELETE FROM monthly_summary;
        RAISE NOTICE 'Eliminati dati da monthly_summary';
    END IF;
    
    -- Activity log
    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'activity_log') INTO table_exists;
    IF table_exists THEN
        DELETE FROM activity_log;
        RAISE NOTICE 'Eliminati dati da activity_log';
    END IF;
    
    -- Users
    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') INTO table_exists;
    IF table_exists THEN
        DELETE FROM users;
        RAISE NOTICE 'Eliminati dati da users';
    END IF;
    
    -- Roles
    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'roles') INTO table_exists;
    IF table_exists THEN
        DELETE FROM roles;
        RAISE NOTICE 'Eliminati dati da roles';
    END IF;
    
    -- System settings
    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'system_settings') INTO table_exists;
    IF table_exists THEN
        DELETE FROM system_settings;
        RAISE NOTICE 'Eliminati dati da system_settings';
    END IF;
    
    RAISE NOTICE 'Pulizia completata!';
END $$;

-- Verifica finale - mostra solo le tabelle che esistono con i loro conteggi
SELECT 'VERIFICA FINALE - TABELLE ESISTENTI E CONTEGGI:' as info;

DO $$
DECLARE
    rec RECORD;
    count_result INTEGER;
BEGIN
    FOR rec IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename
    LOOP
        EXECUTE format('SELECT COUNT(*) FROM %I', rec.tablename) INTO count_result;
        RAISE NOTICE 'Tabella: % - Record: %', rec.tablename, count_result;
    END LOOP;
END $$;
