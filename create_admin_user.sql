-- =====================================================
-- CREAZIONE UTENTE ADMIN E RUOLI
-- Ricrea l'utente amministratore e i ruoli base
-- Creato da: Ezio Camporeale
-- Data: 2024-12-19
-- =====================================================

-- ==================== CREAZIONE RUOLI ====================

-- Inserisce i ruoli base se non esistono
INSERT INTO roles (id, name, description, permissions) VALUES 
('00000000-0000-0000-0000-000000000001', 'admin', 'Administrador completo', '{"all": true}'),
('00000000-0000-0000-0000-000000000002', 'manager', 'Gerente de tienda', '{"sales": true, "inventory": true, "reports": true}'),
('00000000-0000-0000-0000-000000000003', 'employee', 'Empleado', '{"sales": true, "inventory": false, "reports": false}'),
('00000000-0000-0000-0000-000000000004', 'viewer', 'Solo lectura', '{"reports": true}')
ON CONFLICT (id) DO NOTHING;

-- ==================== CREAZIONE UTENTE ADMIN ====================

-- Inserisce l'utente admin (password: admin123)
-- NOTA: La password viene hashata dal sistema, questa è solo un placeholder
INSERT INTO users (id, email, password_hash, first_name, last_name, role_id, is_active) VALUES 
('00000000-0000-0000-0000-000000000001', 'admin@macelleria.com', 'admin123', 'Administrador', 'Sistema', '00000000-0000-0000-0000-000000000001', true)
ON CONFLICT (id) DO NOTHING;

-- ==================== CREAZIONE IMPOSTAZIONI SISTEMA ====================

-- Inserisce le impostazioni base del sistema
INSERT INTO system_settings (id, key, value, description) VALUES 
('00000000-0000-0000-0000-000000000301', 'app_name', 'Dashboard Gestión Carnicería', 'Nombre de la aplicación'),
('00000000-0000-0000-0000-000000000302', 'app_version', '2.0.0', 'Versión de la aplicación'),
('00000000-0000-0000-0000-000000000303', 'currency', 'ARS', 'Moneda principal'),
('00000000-0000-0000-0000-000000000304', 'timezone', 'America/Argentina/Buenos_Aires', 'Zona horaria')
ON CONFLICT (id) DO NOTHING;

-- ==================== VERIFICA CREAZIONE ====================

-- Verifica che i ruoli siano stati creati
SELECT 'RUOLI CREATI:' as info;
SELECT id, name, description FROM roles ORDER BY name;

-- Verifica che l'utente admin sia stato creato
SELECT 'UTENTE ADMIN CREATO:' as info;
SELECT u.id, u.email, u.first_name, u.last_name, r.name as role_name, u.is_active
FROM users u
JOIN roles r ON u.role_id = r.id
WHERE u.email = 'admin@macelleria.com';

-- Verifica le impostazioni del sistema
SELECT 'IMPOSTAZIONI SISTEMA:' as info;
SELECT key, value, description FROM system_settings ORDER BY key;

-- ==================== MESSAGGIO FINALE ====================
SELECT '✅ UTENTE ADMIN E RUOLI CREATI CON SUCCESSO!' as messaggio,
       'Email: admin@macelleria.com - Password: admin123' as dettaglio;
