-- =====================================================
-- VERIFICA SEMPLICE STATO DATABASE
-- Controlla cosa esiste senza errori di tipo
-- =====================================================

-- Mostra tutte le tabelle esistenti
SELECT 'TABELLE ESISTENTI:' as info;
SELECT tablename as tabella FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Verifica esistenza tabelle principali
SELECT 'VERIFICA TABELLE PRINCIPALI:' as info;
SELECT 
    'roles' as tabella,
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'roles') 
         THEN 'ESISTE' ELSE 'NON ESISTE' END as stato;

SELECT 
    'users' as tabella,
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') 
         THEN 'ESISTE' ELSE 'NON ESISTE' END as stato;

SELECT 
    'system_settings' as tabella,
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'system_settings') 
         THEN 'ESISTE' ELSE 'NON ESISTE' END as stato;

SELECT 
    'products' as tabella,
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'products') 
         THEN 'ESISTE' ELSE 'NON ESISTE' END as stato;

SELECT 
    'sales' as tabella,
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sales') 
         THEN 'ESISTE' ELSE 'NON ESISTE' END as stato;

-- Conta record solo se le tabelle esistono
DO $$
DECLARE
    count_roles INTEGER;
    count_users INTEGER;
    count_settings INTEGER;
    count_products INTEGER;
    count_sales INTEGER;
BEGIN
    RAISE NOTICE 'CONTEGGI RECORD:';
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'roles') THEN
        SELECT COUNT(*) INTO count_roles FROM roles;
        RAISE NOTICE '  Ruoli: %', count_roles;
    ELSE
        RAISE NOTICE '  Ruoli: Tabella non esiste';
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') THEN
        SELECT COUNT(*) INTO count_users FROM users;
        RAISE NOTICE '  Utenti: %', count_users;
    ELSE
        RAISE NOTICE '  Utenti: Tabella non esiste';
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'system_settings') THEN
        SELECT COUNT(*) INTO count_settings FROM system_settings;
        RAISE NOTICE '  Impostazioni: %', count_settings;
    ELSE
        RAISE NOTICE '  Impostazioni: Tabella non esiste';
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'products') THEN
        SELECT COUNT(*) INTO count_products FROM products;
        RAISE NOTICE '  Prodotti: %', count_products;
    ELSE
        RAISE NOTICE '  Prodotti: Tabella non esiste';
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sales') THEN
        SELECT COUNT(*) INTO count_sales FROM sales;
        RAISE NOTICE '  Vendite: %', count_sales;
    ELSE
        RAISE NOTICE '  Vendite: Tabella non esiste';
    END IF;
END $$;
