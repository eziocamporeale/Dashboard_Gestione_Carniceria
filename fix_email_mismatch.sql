-- =====================================================
-- FIX EMAIL MISMATCH - Correzione email utente admin
-- L'applicazione cerca admin@carniceria.com ma abbiamo admin@macelleria.com
-- =====================================================

-- Verifica email attuali
SELECT 'EMAIL ATTUALI NEL DATABASE:' as info;
SELECT id, email, first_name, last_name, is_active FROM users;

-- Aggiorna email admin per corrispondere a quella che cerca l'applicazione
UPDATE users 
SET email = 'admin@carniceria.com'
WHERE email = 'admin@macelleria.com';

-- Oppure inserisce un nuovo utente con l'email corretta se non esiste
INSERT INTO users (id, email, password_hash, first_name, last_name, role_id, is_active) 
VALUES 
('00000000-0000-0000-0000-000000000002', 'admin@carniceria.com', 'admin123', 'Administrador', 'Sistema', '00000000-0000-0000-0000-000000000001', true)
ON CONFLICT (email) DO UPDATE SET
    password_hash = EXCLUDED.password_hash,
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    role_id = EXCLUDED.role_id,
    is_active = EXCLUDED.is_active;

-- Verifica email dopo la correzione
SELECT 'EMAIL DOPO CORREZIONE:' as info;
SELECT id, email, first_name, last_name, is_active FROM users ORDER BY email;

-- Verifica che l'utente sia attivo e abbia il ruolo giusto
SELECT 'VERIFICA UTENTE ADMIN:' as info;
SELECT 
    u.id,
    u.email,
    u.first_name,
    u.last_name,
    u.is_active,
    r.name as role_name,
    r.permissions
FROM users u
JOIN roles r ON u.role_id = r.id
WHERE u.email = 'admin@carniceria.com';

-- ==================== MESSAGGIO FINALE ====================
SELECT '✅ EMAIL CORRETTA!' as messaggio;
SELECT '📧 Email corretta: admin@carniceria.com' as credenziale;
SELECT '🔑 Password: admin123' as credenziale;
SELECT '👤 Ruolo: admin' as credenziale;
