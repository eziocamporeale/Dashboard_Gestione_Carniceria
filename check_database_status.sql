-- =====================================================
-- VERIFICA STATO DATABASE DOPO PULIZIA
-- Controlla cosa esiste e cosa manca
-- =====================================================

-- Verifica tabelle esistenti
SELECT 'TABELLE ESISTENTI NEL DATABASE:' as info;
SELECT tablename as tabella FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Verifica ruoli
SELECT 'STATO RUOLI:' as info;
SELECT 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'roles') 
         THEN (SELECT COUNT(*) FROM roles)::text
         ELSE 'Tabella roles non esiste' 
    END as conteggio_ruoli;

-- Verifica utenti
SELECT 'STATO UTENTI:' as info;
SELECT 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') 
         THEN (SELECT COUNT(*) FROM users)::text
         ELSE 'Tabella users non esiste' 
    END as conteggio_utenti;

-- Verifica impostazioni sistema
SELECT 'STATO IMPOSTAZIONI:' as info;
SELECT 
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'system_settings') 
         THEN (SELECT COUNT(*) FROM system_settings)::text
         ELSE 'Tabella system_settings non esiste' 
    END as conteggio_impostazioni;

-- Se le tabelle esistono, mostra i dettagli
DO $$
DECLARE
    rec RECORD;
BEGIN
    -- Mostra ruoli se la tabella esiste
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'roles') THEN
        RAISE NOTICE 'RUOLI PRESENTI:';
        FOR rec IN SELECT name, description FROM roles LOOP
            RAISE NOTICE '  - %: %', rec.name, rec.description;
        END LOOP;
    ELSE
        RAISE NOTICE 'TABELLA ROLES NON ESISTE';
    END IF;
    
    -- Mostra utenti se la tabella esiste
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') THEN
        RAISE NOTICE 'UTENTI PRESENTI:';
        FOR rec IN SELECT email, first_name, last_name FROM users LOOP
            RAISE NOTICE '  - %: % %', rec.email, rec.first_name, rec.last_name;
        END LOOP;
    ELSE
        RAISE NOTICE 'TABELLA USERS NON ESISTE';
    END IF;
    
    -- Mostra impostazioni se la tabella esiste
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'system_settings') THEN
        RAISE NOTICE 'IMPOSTAZIONI PRESENTI:';
        FOR rec IN SELECT key, value FROM system_settings LOOP
            RAISE NOTICE '  - %: %', rec.key, rec.value;
        END LOOP;
    ELSE
        RAISE NOTICE 'TABELLA SYSTEM_SETTINGS NON ESISTE';
    END IF;
END $$;
