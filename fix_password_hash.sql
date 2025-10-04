-- =====================================================
-- FIX PASSWORD HASH - Correzione hash password
-- Risolve l'errore "Invalid salt" durante il login
-- =====================================================

-- Verifica stato attuale password
SELECT 'STATO ATTUALE PASSWORD:' as info;
SELECT 
    email,
    password_hash,
    LENGTH(password_hash) as hash_length,
    CASE 
        WHEN password_hash = 'admin123' THEN 'PASSWORD IN CHIARO - PROBLEMA!'
        WHEN LENGTH(password_hash) < 20 THEN 'HASH TROPPO CORTO - POSSIBILE PROBLEMA!'
        WHEN password_hash LIKE '%$%' THEN 'HASH CON SALT - SEMBRA OK'
        ELSE 'FORMATO HASH NON RICONOSCIUTO'
    END as password_status
FROM users 
WHERE email = 'admin@carniceria.com';

-- Opzione 1: Imposta password in chiaro (il sistema dovrebbe hasharla automaticamente)
UPDATE users 
SET password_hash = 'admin123'
WHERE email = 'admin@carniceria.com';

-- Verifica dopo aggiornamento
SELECT 'PASSWORD DOPO AGGIORNAMENTO:' as info;
SELECT 
    email,
    password_hash,
    LENGTH(password_hash) as hash_length,
    CASE 
        WHEN password_hash = 'admin123' THEN 'PASSWORD IN CHIARO - PRONTA PER HASH'
        ELSE 'PASSWORD HASHATA'
    END as password_status
FROM users 
WHERE email = 'admin@carniceria.com';

-- Usa l'hash bcrypt corretto trovato nel codice (admin123)
UPDATE users 
SET password_hash = '$0.00b$0.00$N7ODldIPrnAg078f8VOOb.XRd.cEHJZ6YYhrDTSAE5BF9r52Km1Qm'
WHERE email = 'admin@carniceria.com';

-- Verifica finale
SELECT 'VERIFICA FINALE UTENTE:' as info;
SELECT 
    u.email,
    u.first_name,
    u.last_name,
    u.is_active,
    u.password_hash,
    r.name as role_name
FROM users u
JOIN roles r ON u.role_id = r.id
WHERE u.email = 'admin@carniceria.com';

-- ==================== MESSAGGIO FINALE ====================
SELECT '✅ PASSWORD AGGIORNATA!' as messaggio;
SELECT '📧 Email: admin@carniceria.com' as credenziale;
SELECT '🔑 Password: admin123' as credenziale;
SELECT '💡 Il sistema dovrebbe ora riuscire a verificare la password' as nota;
