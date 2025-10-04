-- =====================================================
-- VERIFICA TABELLE ESISTENTI PRIMA DELLA PULIZIA
-- Mostra quali tabelle esistono realmente nel database
-- =====================================================

-- Mostra tutte le tabelle esistenti nel database
SELECT 
    tablename as tabella_esistente,
    'EXISTS' as status
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- Mostra il conteggio dei record per ogni tabella esistente
SELECT 
    'sale_items' as tabella,
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sale_items') 
         THEN (SELECT COUNT(*) FROM sale_items) ELSE NULL END as registri
UNION ALL
SELECT 'sales', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sales') 
         THEN (SELECT COUNT(*) FROM sales) ELSE NULL END
UNION ALL
SELECT 'customer_orders', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'customer_orders') 
         THEN (SELECT COUNT(*) FROM customer_orders) ELSE NULL END
UNION ALL
SELECT 'customers', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'customers') 
         THEN (SELECT COUNT(*) FROM customers) ELSE NULL END
UNION ALL
SELECT 'suppliers', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'suppliers') 
         THEN (SELECT COUNT(*) FROM suppliers) ELSE NULL END
UNION ALL
SELECT 'products', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'products') 
         THEN (SELECT COUNT(*) FROM products) ELSE NULL END
UNION ALL
SELECT 'product_categories', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'product_categories') 
         THEN (SELECT COUNT(*) FROM product_categories) ELSE NULL END
UNION ALL
SELECT 'units_of_measure', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'units_of_measure') 
         THEN (SELECT COUNT(*) FROM units_of_measure) ELSE NULL END
UNION ALL
SELECT 'employees', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'employees') 
         THEN (SELECT COUNT(*) FROM employees) ELSE NULL END
UNION ALL
SELECT 'employee_shifts', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'employee_shifts') 
         THEN (SELECT COUNT(*) FROM employee_shifts) ELSE NULL END
UNION ALL
SELECT 'daily_income', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'daily_income') 
         THEN (SELECT COUNT(*) FROM daily_income) ELSE NULL END
UNION ALL
SELECT 'daily_expenses', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'daily_expenses') 
         THEN (SELECT COUNT(*) FROM daily_expenses) ELSE NULL END
UNION ALL
SELECT 'daily_reports', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'daily_reports') 
         THEN (SELECT COUNT(*) FROM daily_reports) ELSE NULL END
UNION ALL
SELECT 'accounting_categories', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'accounting_categories') 
         THEN (SELECT COUNT(*) FROM accounting_categories) ELSE NULL END
UNION ALL
SELECT 'excel_data', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'excel_data') 
         THEN (SELECT COUNT(*) FROM excel_data) ELSE NULL END
UNION ALL
SELECT 'monthly_summary', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'monthly_summary') 
         THEN (SELECT COUNT(*) FROM monthly_summary) ELSE NULL END
UNION ALL
SELECT 'activity_log', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'activity_log') 
         THEN (SELECT COUNT(*) FROM activity_log) ELSE NULL END
UNION ALL
SELECT 'user_roles', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_roles') 
         THEN (SELECT COUNT(*) FROM user_roles) ELSE NULL END
UNION ALL
SELECT 'users', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') 
         THEN (SELECT COUNT(*) FROM users) ELSE NULL END
UNION ALL
SELECT 'roles', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'roles') 
         THEN (SELECT COUNT(*) FROM roles) ELSE NULL END
UNION ALL
SELECT 'system_settings', 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'system_settings') 
         THEN (SELECT COUNT(*) FROM system_settings) ELSE NULL END
ORDER BY tabella;
