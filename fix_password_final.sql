-- =====================================================
-- FIX PASSWORD FINALE - Hash bcrypt corretto
-- Usa l'hash generato dal Python script
-- =====================================================

-- Verifica stato attuale
SELECT 'STATO PASSWORD PRIMA DEL FIX:' as info;
SELECT 
    email,
    password_hash,
    LENGTH(password_hash) as hash_length,
    CASE 
        WHEN password_hash = 'admin123' THEN 'PASSWORD IN CHIARO'
        WHEN password_hash LIKE '$2b$%' THEN 'HASH BCRYPT VALIDO'
        ELSE 'HASH NON VALIDO'
    END as password_status
FROM users 
WHERE email = 'admin@carniceria.com';

-- Aggiorna con il nuovo hash bcrypt corretto
UPDATE users 
SET password_hash = '$2b$12$uc4GoY7RTL.IPQXng4LcUuMJjl/5bL4j.CxrBQii4lTQyBnhcf9Xu'
WHERE email = 'admin@carniceria.com';

-- Verifica dopo l'aggiornamento
SELECT 'STATO PASSWORD DOPO IL FIX:' as info;
SELECT 
    email,
    password_hash,
    LENGTH(password_hash) as hash_length,
    CASE 
        WHEN password_hash = 'admin123' THEN 'PASSWORD IN CHIARO'
        WHEN password_hash LIKE '$2b$%' THEN 'HASH BCRYPT VALIDO'
        ELSE 'HASH NON VALIDO'
    END as password_status
FROM users 
WHERE email = 'admin@carniceria.com';

-- Verifica completa utente
SELECT 'VERIFICA COMPLETA UTENTE ADMIN:' as info;
SELECT 
    u.email,
    u.first_name,
    u.last_name,
    u.is_active,
    u.password_hash,
    r.name as role_name,
    r.permissions
FROM users u
JOIN roles r ON u.role_id = r.id
WHERE u.email = 'admin@carniceria.com';

-- ==================== MESSAGGIO FINALE ====================
SELECT '✅ PASSWORD CORRETTA!' as messaggio;
SELECT '📧 Email: admin@carniceria.com' as credenziale;
SELECT '🔑 Password: admin123' as credenziale;
SELECT '🔐 Hash: bcrypt valido' as credenziale;
SELECT '👤 Ruolo: admin (accesso completo)' as credenziale;
