-- =====================================================
-- FIX COMPLETO LOGIN - VERIFICA E RIPRISTINA TUTTO
-- Controlla e ricrea tutto quello che serve per il login
-- =====================================================

-- ==================== VERIFICA STATO ATTUALE ====================

SELECT '=== VERIFICA STATO DATABASE ===' as info;

-- Mostra tutte le tabelle esistenti
SELECT 'TABELLE ESISTENTI:' as info;
SELECT tablename as tabella FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Verifica esistenza tabelle critiche per login
SELECT 'VERIFICA TABELLE CRITICHE:' as info;
SELECT 
    'roles' as tabella,
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'roles') 
         THEN 'ESISTE' ELSE 'NON ESISTE' END as stato;

SELECT 
    'users' as tabella,
    CASE WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') 
         THEN 'ESISTE' ELSE 'NON ESISTE' END as stato;

-- ==================== CREAZIONE TABELLE MANCANTI ====================

-- Crea tabella roles se non esiste
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    permissions JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crea tabella users se non esiste
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role_id UUID REFERENCES roles(id),
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crea tabella system_settings se non esiste
CREATE TABLE IF NOT EXISTS system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== INSERIMENTO DATI BASE ====================

-- Inserisce ruolo admin se non esiste
INSERT INTO roles (id, name, description, permissions) VALUES 
('00000000-0000-0000-0000-000000000001', 'admin', 'Administrador completo', '{"all": true}')
ON CONFLICT (id) DO NOTHING;

-- Inserisce altri ruoli base
INSERT INTO roles (id, name, description, permissions) VALUES 
('00000000-0000-0000-0000-000000000002', 'manager', 'Gerente de tienda', '{"sales": true, "inventory": true, "reports": true}'),
('00000000-0000-0000-0000-000000000003', 'employee', 'Empleado', '{"sales": true, "inventory": false, "reports": false}'),
('00000000-0000-0000-0000-000000000004', 'viewer', 'Solo lectura', '{"reports": true}')
ON CONFLICT (id) DO NOTHING;

-- Inserisce utente admin (password: admin123)
INSERT INTO users (id, email, password_hash, first_name, last_name, role_id, is_active) VALUES 
('00000000-0000-0000-0000-000000000001', 'admin@macelleria.com', 'admin123', 'Administrador', 'Sistema', '00000000-0000-0000-0000-000000000001', true)
ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    password_hash = EXCLUDED.password_hash,
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    role_id = EXCLUDED.role_id,
    is_active = EXCLUDED.is_active;

-- Inserisce impostazioni sistema
INSERT INTO system_settings (id, key, value, description) VALUES 
('00000000-0000-0000-0000-000000000301', 'app_name', 'Dashboard Gestión Carnicería', 'Nombre de la aplicación'),
('00000000-0000-0000-0000-000000000302', 'app_version', '2.0.0', 'Versión de la aplicación'),
('00000000-0000-0000-0000-000000000303', 'currency', 'ARS', 'Moneda principal'),
('00000000-0000-0000-0000-000000000304', 'timezone', 'America/Argentina/Buenos_Aires', 'Zona horaria')
ON CONFLICT (id) DO NOTHING;

-- ==================== VERIFICA FINALE ====================

SELECT '=== VERIFICA FINALE ===' as info;

-- Mostra ruoli creati
SELECT 'RUOLI DISPONIBILI:' as info;
SELECT id, name, description FROM roles ORDER BY name;

-- Mostra utenti creati
SELECT 'UTENTI DISPONIBILI:' as info;
SELECT u.id, u.email, u.first_name, u.last_name, r.name as role_name, u.is_active
FROM users u
JOIN roles r ON u.role_id = r.id
ORDER BY u.email;

-- Mostra impostazioni
SELECT 'IMPOSTAZIONI SISTEMA:' as info;
SELECT key, value, description FROM system_settings ORDER BY key;

-- ==================== MESSAGGIO FINALE ====================
SELECT '=== LOGIN RIPRISTINATO ===' as info;
SELECT '✅ CREDENZIALI LOGIN:' as messaggio;
SELECT '📧 Email: admin@macelleria.com' as credenziale;
SELECT '🔑 Password: admin123' as credenziale;
SELECT '👤 Ruolo: admin (accesso completo)' as credenziale;
