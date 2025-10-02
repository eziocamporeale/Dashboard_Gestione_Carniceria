-- =====================================================
-- DATI INIZIALI - Dashboard Gestión Carnicería
-- Versione: 2.0.0
-- Creato da: Ezio Camporeale
-- Database: Supabase PostgreSQL
-- =====================================================

-- ==================== DATI INIZIALI ====================

-- Inserimento ruoli utente
INSERT INTO roles (id, name, description, permissions) VALUES 
('00000000-0000-0000-0000-000000000001', 'admin', 'Administrador completo', '{"all": true}'),
('00000000-0000-0000-0000-000000000002', 'manager', 'Gerente de tienda', '{"sales": true, "inventory": true, "reports": true}'),
('00000000-0000-0000-0000-000000000003', 'employee', 'Empleado', '{"sales": true, "inventory": false, "reports": false}'),
('00000000-0000-0000-0000-000000000004', 'viewer', 'Solo lectura', '{"reports": true}')
ON CONFLICT (id) DO NOTHING;

-- Inserimento categorie prodotti
INSERT INTO product_categories (id, name, description, color) VALUES 
('00000000-0000-0000-0000-000000000101', 'Carnes', 'Carnes frescas', '#DC3545'),
('00000000-0000-0000-0000-000000000102', 'Aves', 'Pollo y otras aves', '#FFC107'),
('00000000-0000-0000-0000-000000000103', 'Embutidos', 'Embutidos y fiambres', '#6F42C1'),
('00000000-0000-0000-0000-000000000104', 'Pescados', 'Pescados frescos', '#17A2B8'),
('00000000-0000-0000-0000-000000000105', 'Verduras', 'Verduras frescas', '#28A745'),
('00000000-0000-0000-0000-000000000106', 'Otros', 'Otros productos', '#6C757D')
ON CONFLICT (id) DO NOTHING;

-- Inserimento unità di misura
INSERT INTO units_of_measure (id, name, symbol, description) VALUES 
('00000000-0000-0000-0000-000000000201', 'Kilogramo', 'kg', 'Peso en kilogramos'),
('00000000-0000-0000-0000-000000000202', 'Gramo', 'g', 'Peso en gramos'),
('00000000-0000-0000-0000-000000000203', 'Unidad', 'un', 'Cantidad en unidades'),
('00000000-0000-0000-0000-000000000204', 'Libra', 'lb', 'Peso en libras'),
('00000000-0000-0000-0000-000000000205', 'Onza', 'oz', 'Peso en onzas')
ON CONFLICT (id) DO NOTHING;

-- Inserimento impostazioni sistema
INSERT INTO system_settings (id, key, value, description) VALUES 
('00000000-0000-0000-0000-000000000301', 'app_name', 'Dashboard Gestión Carnicería', 'Nombre de la aplicación'),
('00000000-0000-0000-0000-000000000302', 'app_version', '2.0.0', 'Versión de la aplicación'),
('00000000-0000-0000-0000-000000000303', 'currency', 'ARS', 'Moneda principal'),
('00000000-0000-0000-0000-000000000304', 'timezone', 'America/Argentina/Buenos_Aires', 'Zona horaria')
ON CONFLICT (id) DO NOTHING;

-- Inserimento utente admin (password: admin123)
-- Hash della password admin123 generato con bcrypt
INSERT INTO users (id, email, password_hash, first_name, last_name, role_id, is_active) VALUES 
('00000000-0000-0000-0000-000000000401', 'admin@carniceria.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J.8.8.8.8', 'Admin', 'Sistema', '00000000-0000-0000-0000-000000000001', true)
ON CONFLICT (id) DO NOTHING;

-- Inserimento utente admin alternativo (username: admin, password: admin123)
INSERT INTO users (id, email, password_hash, first_name, last_name, role_id, is_active) VALUES 
('00000000-0000-0000-0000-000000000402', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J.8.8.8.8', 'Admin', 'Sistema', '00000000-0000-0000-0000-000000000001', true)
ON CONFLICT (id) DO NOTHING;

-- Inserimento prodotti di esempio
INSERT INTO products (id, name, code, description, category_id, unit_id, cost_price, selling_price, current_stock, min_stock_level, is_active) VALUES 
('00000000-0000-0000-0000-000000000501', 'Carne de Res', 'CR001', 'Carne de res fresca', '00000000-0000-0000-0000-000000000101', '00000000-0000-0000-0000-000000000201', 15.50, 25.00, 50.0, 10.0, true),
('00000000-0000-0000-0000-000000000502', 'Pollo Entero', 'PE001', 'Pollo entero fresco', '00000000-0000-0000-0000-000000000102', '00000000-0000-0000-0000-000000000201', 8.00, 12.00, 30.0, 5.0, true),
('00000000-0000-0000-0000-000000000503', 'Jamón Cocido', 'JC001', 'Jamón cocido premium', '00000000-0000-0000-0000-000000000103', '00000000-0000-0000-0000-000000000201', 12.00, 18.00, 20.0, 3.0, true)
ON CONFLICT (id) DO NOTHING;

-- Inserimento fornitori di esempio
INSERT INTO suppliers (id, name, contact_person, phone, contact_email, address, total_amount, transactions_count, is_active) VALUES 
('00000000-0000-0000-0000-000000000601', 'Proveedor Carnes Premium', 'Juan Pérez', '+54 11 1234-5678', 'juan@carnespremium.com', 'Av. Corrientes 1234, Buenos Aires', 15000.00, 25, true),
('00000000-0000-0000-0000-000000000602', 'Distribuidora Aves', 'María González', '+54 11 8765-4321', 'maria@aves.com', 'Av. Santa Fe 5678, Buenos Aires', 8500.00, 15, true)
ON CONFLICT (id) DO NOTHING;

-- Inserimento dipendenti di esempio
INSERT INTO employees (id, first_name, last_name, phone, email, position, department, salary, hire_date, is_active) VALUES 
('00000000-0000-0000-0000-000000000701', 'Carlos', 'Rodríguez', '+54 11 1111-1111', 'carlos@carniceria.com', 'Vendedor', 'Ventas', 80000.00, '2024-01-15', true),
('00000000-0000-0000-0000-000000000702', 'Ana', 'Martínez', '+54 11 2222-2222', 'ana@carniceria.com', 'Cajera', 'Atención al Cliente', 75000.00, '2024-02-01', true)
ON CONFLICT (id) DO NOTHING;

-- ==================== VERIFICA DATI ====================

-- Verifica inserimento ruoli
SELECT 'Roles inseriti:' as info, count(*) as totale FROM roles;

-- Verifica inserimento categorie
SELECT 'Categorie inserite:' as info, count(*) as totale FROM product_categories;

-- Verifica inserimento unità
SELECT 'Unità inserite:' as info, count(*) as totale FROM units_of_measure;

-- Verifica inserimento utenti
SELECT 'Utenti inseriti:' as info, count(*) as totale FROM users;

-- Verifica inserimento prodotti
SELECT 'Prodotti inseriti:' as info, count(*) as totale FROM products;

-- Verifica inserimento fornitori
SELECT 'Fornitori inseriti:' as info, count(*) as totale FROM suppliers;

-- Verifica inserimento dipendenti
SELECT 'Dipendenti inseriti:' as info, count(*) as totale FROM employees;

-- ==================== FINE SCRIPT ====================
