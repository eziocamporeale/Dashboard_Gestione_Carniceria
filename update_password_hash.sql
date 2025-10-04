-- =====================================================
-- AGGIORNA HASH PASSWORD CON NUOVO HASH VALIDO
-- =====================================================

-- Verifica hash attuale
SELECT 'HASH ATTUALE:' as info;
SELECT email, password_hash FROM users WHERE email = 'admin@carniceria.com';

-- Aggiorna con il nuovo hash valido generato dal Python
UPDATE users 
SET password_hash = '$2b$12$keTL8XekGpYZeiuf3zKrNureMowffxpYXDqaSDQq7ofc5hwEiDq.y'
WHERE email = 'admin@carniceria.com';

-- Verifica dopo l'aggiornamento
SELECT 'HASH DOPO AGGIORNAMENTO:' as info;
SELECT email, password_hash FROM users WHERE email = 'admin@carniceria.com';

-- Verifica completa
SELECT 'VERIFICA COMPLETA UTENTE:' as info;
SELECT 
    u.email,
    u.first_name,
    u.last_name,
    u.is_active,
    r.name as role_name
FROM users u
JOIN roles r ON u.role_id = r.id
WHERE u.email = 'admin@carniceria.com';

SELECT '✅ PASSWORD AGGIORNATA!' as messaggio;
SELECT '📧 Email: admin@carniceria.com' as credenziale;
SELECT '🔑 Password: admin123' as credenziale;
