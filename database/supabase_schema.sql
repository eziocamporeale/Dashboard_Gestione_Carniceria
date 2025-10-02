-- =====================================================
-- SUPABASE SCHEMA - Dashboard Gestión Carnicería
-- Versione: 2.0.0
-- Creato da: Ezio Camporeale
-- Database: PostgreSQL (Supabase)
-- =====================================================

-- ==================== EXTENSIONS ====================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==================== FUNCTIONS ====================
-- Funzione per aggiornare updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ==================== TABLES ====================

-- Tabella ruoli utente
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    permissions JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella utenti
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

-- Tabella categorie prodotti
CREATE TABLE IF NOT EXISTS product_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7) DEFAULT '#6C757D',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella unità di misura
CREATE TABLE IF NOT EXISTS units_of_measure (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,
    symbol VARCHAR(10) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella prodotti
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE,
    description TEXT,
    category_id UUID REFERENCES product_categories(id),
    unit_id UUID REFERENCES units_of_measure(id),
    cost_price DECIMAL(10,2) DEFAULT 0,
    selling_price DECIMAL(10,2) DEFAULT 0,
    current_stock DECIMAL(10,3) DEFAULT 0,
    min_stock_level DECIMAL(10,3) DEFAULT 0,
    expiry_date DATE,
    supplier_id UUID,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella fornitori
CREATE TABLE IF NOT EXISTS suppliers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    contact_person VARCHAR(255),
    total_amount DECIMAL(12,2) DEFAULT 0,
    transactions_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella clienti
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    total_purchases DECIMAL(12,2) DEFAULT 0,
    last_purchase TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella vendite
CREATE TABLE IF NOT EXISTS sales (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id),
    user_id UUID REFERENCES users(id),
    sale_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    total_amount DECIMAL(12,2) NOT NULL,
    discount_percentage DECIMAL(5,2) DEFAULT 0,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    final_amount DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella dettagli vendite
CREATE TABLE IF NOT EXISTS sale_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sale_id UUID REFERENCES sales(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    quantity DECIMAL(10,3) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella dipendenti
CREATE TABLE IF NOT EXISTS employees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    position VARCHAR(100),
    department VARCHAR(100),
    salary DECIMAL(10,2),
    hire_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella turni dipendenti
CREATE TABLE IF NOT EXISTS employee_shifts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id),
    shift_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    hours_worked DECIMAL(4,2),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella dati Excel salvati
CREATE TABLE IF NOT EXISTS excel_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_name VARCHAR(255) NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    data JSONB NOT NULL,
    processed_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella riepilogo mensile
CREATE TABLE IF NOT EXISTS monthly_summary (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    month VARCHAR(7) NOT NULL, -- YYYY-MM format
    total_sales DECIMAL(12,2) DEFAULT 0,
    total_expenses DECIMAL(12,2) DEFAULT 0,
    total_profit DECIMAL(12,2) DEFAULT 0,
    transactions_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabella impostazioni sistema
CREATE TABLE IF NOT EXISTS system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== TRIGGERS ====================
-- Trigger per aggiornare updated_at automaticamente
CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON roles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_product_categories_updated_at BEFORE UPDATE ON product_categories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_units_of_measure_updated_at BEFORE UPDATE ON units_of_measure FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON suppliers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_sales_updated_at BEFORE UPDATE ON sales FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_employees_updated_at BEFORE UPDATE ON employees FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_employee_shifts_updated_at BEFORE UPDATE ON employee_shifts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_monthly_summary_updated_at BEFORE UPDATE ON monthly_summary FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==================== ROW LEVEL SECURITY (RLS) ====================

-- Abilita RLS su tutte le tabelle
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE units_of_measure ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE sale_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE employee_shifts ENABLE ROW LEVEL SECURITY;
ALTER TABLE excel_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE monthly_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;

-- Politiche RLS per accesso completo (admin)
CREATE POLICY "Admin full access" ON roles FOR ALL USING (true);
CREATE POLICY "Admin full access" ON users FOR ALL USING (true);
CREATE POLICY "Admin full access" ON product_categories FOR ALL USING (true);
CREATE POLICY "Admin full access" ON units_of_measure FOR ALL USING (true);
CREATE POLICY "Admin full access" ON products FOR ALL USING (true);
CREATE POLICY "Admin full access" ON suppliers FOR ALL USING (true);
CREATE POLICY "Admin full access" ON customers FOR ALL USING (true);
CREATE POLICY "Admin full access" ON sales FOR ALL USING (true);
CREATE POLICY "Admin full access" ON sale_items FOR ALL USING (true);
CREATE POLICY "Admin full access" ON employees FOR ALL USING (true);
CREATE POLICY "Admin full access" ON employee_shifts FOR ALL USING (true);
CREATE POLICY "Admin full access" ON excel_data FOR ALL USING (true);
CREATE POLICY "Admin full access" ON monthly_summary FOR ALL USING (true);
CREATE POLICY "Admin full access" ON system_settings FOR ALL USING (true);

-- ==================== INDEXES ====================
-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_products_code ON products(code);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON sale_items(sale_id);
CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department);
CREATE INDEX IF NOT EXISTS idx_employee_shifts_date ON employee_shifts(shift_date);
CREATE INDEX IF NOT EXISTS idx_monthly_summary_month ON monthly_summary(month);

-- ==================== INITIAL DATA ====================
-- Inserimento dati iniziali
INSERT INTO roles (id, name, description, permissions) VALUES 
('00000000-0000-0000-0000-000000000001', 'admin', 'Administrador completo', '{"all": true}'),
('00000000-0000-0000-0000-000000000002', 'manager', 'Gerente de tienda', '{"sales": true, "inventory": true, "reports": true}'),
('00000000-0000-0000-0000-000000000003', 'employee', 'Empleado', '{"sales": true, "inventory": false, "reports": false}'),
('00000000-0000-0000-0000-000000000004', 'viewer', 'Solo lectura', '{"reports": true}');

INSERT INTO product_categories (id, name, description, color) VALUES 
('00000000-0000-0000-0000-000000000101', 'Carnes', 'Carnes frescas', '#DC3545'),
('00000000-0000-0000-0000-000000000102', 'Aves', 'Pollo y otras aves', '#FFC107'),
('00000000-0000-0000-0000-000000000103', 'Embutidos', 'Embutidos y fiambres', '#6F42C1'),
('00000000-0000-0000-0000-000000000104', 'Pescados', 'Pescados frescos', '#17A2B8'),
('00000000-0000-0000-0000-000000000105', 'Verduras', 'Verduras frescas', '#28A745'),
('00000000-0000-0000-0000-000000000106', 'Otros', 'Otros productos', '#6C757D');

INSERT INTO units_of_measure (id, name, symbol, description) VALUES 
('00000000-0000-0000-0000-000000000201', 'Kilogramo', 'kg', 'Peso en kilogramos'),
('00000000-0000-0000-0000-000000000202', 'Gramo', 'g', 'Peso en gramos'),
('00000000-0000-0000-0000-000000000203', 'Unidad', 'un', 'Cantidad en unidades'),
('00000000-0000-0000-0000-000000000204', 'Libra', 'lb', 'Peso en libras'),
('00000000-0000-0000-0000-000000000205', 'Onza', 'oz', 'Peso en onzas');

INSERT INTO system_settings (id, key, value, description) VALUES 
('00000000-0000-0000-0000-000000000301', 'app_name', 'Dashboard Gestión Carnicería', 'Nombre de la aplicación'),
('00000000-0000-0000-0000-000000000302', 'app_version', '2.0.0', 'Versión de la aplicación'),
('00000000-0000-0000-0000-000000000303', 'currency', 'ARS', 'Moneda principal'),
('00000000-0000-0000-0000-000000000304', 'timezone', 'America/Argentina/Buenos_Aires', 'Zona horaria');

-- ==================== COMMENTS ====================
COMMENT ON TABLE roles IS 'Tabla de roles de usuario del sistema';
COMMENT ON TABLE users IS 'Tabla de usuarios del sistema';
COMMENT ON TABLE products IS 'Tabla de productos de la carnicería';
COMMENT ON TABLE sales IS 'Tabla de ventas realizadas';
COMMENT ON TABLE employees IS 'Tabla de empleados de la carnicería';
COMMENT ON TABLE excel_data IS 'Tabla de datos importados desde Excel';
