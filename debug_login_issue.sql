-- =====================================================
-- DEBUG LOGIN ISSUE - ANALISI DETTAGLIATA
-- Analizza tutti i possibili problemi di login
-- =====================================================

-- ==================== VERIFICA STRUTTURA TABELLE ====================

SELECT '=== ANALISI STRUTTURA TABELLE ===' as info;

-- Verifica colonne tabella users
SELECT 'STRUTTURA TABELLA USERS:' as info;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'users' AND table_schema = 'public'
ORDER BY ordinal_position;

-- Verifica colonne tabella roles
SELECT 'STRUTTURA TABELLA ROLES:' as info;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'roles' AND table_schema = 'public'
ORDER BY ordinal_position;

-- ==================== VERIFICA DATI ====================

SELECT '=== ANALISI DATI ===' as info;

-- Conta record
SELECT 'CONTEGGI RECORD:' as info;
SELECT 'users' as tabella, COUNT(*) as conteggio FROM users
UNION ALL
SELECT 'roles', COUNT(*) FROM roles
UNION ALL
SELECT 'system_settings', COUNT(*) FROM system_settings;

-- Mostra tutti gli utenti
SELECT 'TUTTI GLI UTENTI:' as info;
SELECT 
    id,
    email,
    password_hash,
    first_name,
    last_name,
    role_id,
    is_active,
    created_at
FROM users;

-- Mostra tutti i ruoli
SELECT 'TUTTI I RUOLI:' as info;
SELECT 
    id,
    name,
    description,
    permissions
FROM roles;

-- Verifica relazioni
SELECT 'VERIFICA RELAZIONI:' as info;
SELECT 
    u.email,
    u.first_name,
    u.last_name,
    u.is_active,
    r.name as role_name,
    r.permissions
FROM users u
LEFT JOIN roles r ON u.role_id = r.id;

-- ==================== VERIFICA INTEGRITÀ ====================

SELECT '=== VERIFICA INTEGRITÀ ===' as info;

-- Utenti senza ruolo
SELECT 'UTENTI SENZA RUOLO:' as info;
SELECT email, first_name, last_name, role_id
FROM users 
WHERE role_id IS NULL;

-- Utenti inattivi
SELECT 'UTENTI INATTIVI:' as info;
SELECT email, first_name, last_name, is_active
FROM users 
WHERE is_active = false;

-- Ruoli orfani (senza utenti)
SELECT 'RUOLI ORFANI:' as info;
SELECT r.name, r.description
FROM roles r
LEFT JOIN users u ON r.id = u.role_id
WHERE u.id IS NULL;

-- ==================== VERIFICA PASSWORD ====================

SELECT '=== VERIFICA PASSWORD ===' as info;

-- Mostra hash password (per debug)
SELECT 'HASH PASSWORD UTENTI:' as info;
SELECT 
    email,
    password_hash,
    LENGTH(password_hash) as hash_length,
    CASE 
        WHEN password_hash = 'admin123' THEN 'PASSWORD IN CHIARO - PROBLEMA!'
        WHEN LENGTH(password_hash) < 20 THEN 'HASH TROPPO CORTO - POSSIBILE PROBLEMA!'
        ELSE 'HASH SEMBRA OK'
    END as password_status
FROM users;

-- ==================== SUGGERIMENTI ====================

SELECT '=== SUGGERIMENTI ===' as info;

DO $$
DECLARE
    user_count INTEGER;
    admin_count INTEGER;
    active_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO user_count FROM users;
    SELECT COUNT(*) INTO admin_count FROM users WHERE email = 'admin@macelleria.com';
    SELECT COUNT(*) INTO active_count FROM users WHERE is_active = true;
    
    RAISE NOTICE 'DIAGNOSI:';
    RAISE NOTICE '  - Totale utenti: %', user_count;
    RAISE NOTICE '  - Utenti admin: %', admin_count;
    RAISE NOTICE '  - Utenti attivi: %', active_count;
    
    IF user_count = 0 THEN
        RAISE NOTICE 'PROBLEMA: Nessun utente nel database!';
    ELSIF admin_count = 0 THEN
        RAISE NOTICE 'PROBLEMA: Utente admin non trovato!';
    ELSIF active_count = 0 THEN
        RAISE NOTICE 'PROBLEMA: Nessun utente attivo!';
    ELSE
        RAISE NOTICE 'DATI SEMBRANO OK - Controllare applicazione';
    END IF;
END $$;
