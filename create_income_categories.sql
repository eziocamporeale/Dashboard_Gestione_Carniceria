-- Script per creare categorie di entrata nella tabella accounting_categories
-- Creado por Ezio Camporeale

-- Inserisci categorie di entrata
INSERT INTO accounting_categories (name, type, description, is_active, created_at, updated_at) VALUES
('Ventas', 'income', 'Ingresos por ventas de productos', true, NOW(), NOW()),
('Servicios', 'income', 'Ingresos por servicios prestados', true, NOW(), NOW()),
('Subvenciones', 'income', 'Subvenciones y ayudas recibidas', true, NOW(), NOW()),
('Otros Ingresos', 'income', 'Otros ingresos no clasificados', true, NOW(), NOW());

-- Verifica le categorie inserite
SELECT * FROM accounting_categories WHERE type = 'income' AND is_active = true;

