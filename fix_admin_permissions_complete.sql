-- =====================================================
-- FIX PERMESSI ADMIN COMPLETO
-- Verifica e corregge tutti i permessi dell'utente admin
-- =====================================================

-- ==================== VERIFICA STATO ATTUALE ====================

SELECT '=== VERIFICA STATO ATTUALE ADMIN ===' as info;

-- Verifica utente admin
SELECT 'UTENTE ADMIN:' as info;
SELECT 
    u.id,
    u.email,
    u.first_name,
    u.last_name,
    u.is_active,
    u.role_id,
    r.name as role_name,
    r.permissions
FROM users u
LEFT JOIN roles r ON u.role_id = r.id
WHERE u.email = 'admin@carniceria.com';

-- Verifica ruolo admin
SELECT 'RUOLO ADMIN:' as info;
SELECT 
    id,
    name,
    description,
    permissions
FROM roles 
WHERE name = 'admin';

-- ==================== CORREZIONE PERMESSI ====================

-- Aggiorna ruolo admin con permessi completi
UPDATE roles 
SET permissions = '{"all": true, "inventory": true, "sales": true, "customers": true, "suppliers": true, "employees": true, "analytics": true, "balance": true, "config": true}'
WHERE name = 'admin';

-- Assicura che l'utente admin abbia il ruolo corretto
UPDATE users 
SET role_id = (SELECT id FROM roles WHERE name = 'admin')
WHERE email = 'admin@carniceria.com';

-- Aggiungi colonna is_admin se non esiste (per compatibilità)
DO $$
BEGIN
    -- Aggiungi colonna is_admin se non esiste
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'is_admin') THEN
        ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT false;
    END IF;
END $$;

-- Imposta is_admin = true per l'utente admin
UPDATE users 
SET is_admin = true
WHERE email = 'admin@carniceria.com';

-- ==================== VERIFICA FINALE ====================

SELECT '=== VERIFICA FINALE ===' as info;

-- Verifica utente admin dopo correzione
SELECT 'UTENTE ADMIN DOPO CORREZIONE:' as info;
SELECT 
    u.id,
    u.email,
    u.first_name,
    u.last_name,
    u.is_active,
    u.is_admin,
    u.role_id,
    r.name as role_name,
    r.permissions
FROM users u
LEFT JOIN roles r ON u.role_id = r.id
WHERE u.email = 'admin@carniceria.com';

-- Verifica ruolo admin dopo correzione
SELECT 'RUOLO ADMIN DOPO CORREZIONE:' as info;
SELECT 
    id,
    name,
    description,
    permissions
FROM roles 
WHERE name = 'admin';

-- ==================== MESSAGGIO FINALE ====================
SELECT '✅ PERMESSI ADMIN CORRETTI!' as messaggio;
SELECT '🔑 L''utente admin ora ha accesso completo a tutte le sezioni' as dettaglio;
