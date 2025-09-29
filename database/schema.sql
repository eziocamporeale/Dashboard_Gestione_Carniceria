-- Schema Database Dashboard Gestione Macelleria
-- Creato da Ezio Camporeale

-- ===== TABELLE UTENTI E AUTENTICAZIONE =====

-- Tabella ruoli utente
CREATE TABLE IF NOT EXISTS user_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    permissions TEXT, -- JSON string con permessi
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella utenti
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    role_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    is_admin BOOLEAN DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    created_by INTEGER,
    FOREIGN KEY (role_id) REFERENCES user_roles(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- ===== TABELLE PRODOTTI E INVENTARIO =====

-- Tabella categorie prodotti
CREATE TABLE IF NOT EXISTS product_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER,
    color VARCHAR(7) DEFAULT '#FF6B35', -- Hex color
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES product_categories(id)
);

-- Tabella unità di misura
CREATE TABLE IF NOT EXISTS units_of_measure (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) NOT NULL UNIQUE,
    symbol VARCHAR(10) NOT NULL,
    type VARCHAR(20) NOT NULL, -- weight, volume, pieces
    conversion_factor REAL DEFAULT 1.0, -- Fattore di conversione rispetto all'unità base
    is_base_unit BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella prodotti
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(50) UNIQUE, -- Codice prodotto interno
    barcode VARCHAR(50), -- Codice a barre
    category_id INTEGER NOT NULL,
    unit_id INTEGER NOT NULL,
    description TEXT,
    brand VARCHAR(100),
    origin VARCHAR(100), -- Provenienza/provenienza
    weight_per_unit REAL DEFAULT 1.0, -- Peso per unità
    cost_price DECIMAL(10,2) DEFAULT 0.00, -- Prezzo di costo
    selling_price DECIMAL(10,2) NOT NULL, -- Prezzo di vendita
    min_stock_level INTEGER DEFAULT 0, -- Livello minimo scorte
    max_stock_level INTEGER DEFAULT 1000, -- Livello massimo scorte
    shelf_life_days INTEGER, -- Giorni di conservazione
    requires_temperature_control BOOLEAN DEFAULT 0,
    storage_temperature_min REAL, -- Temperatura minima conservazione
    storage_temperature_max REAL, -- Temperatura massima conservazione
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES product_categories(id),
    FOREIGN KEY (unit_id) REFERENCES units_of_measure(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Tabella scorte/inventario
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    batch_number VARCHAR(50), -- Numero lotto
    quantity REAL NOT NULL DEFAULT 0.0,
    unit_id INTEGER NOT NULL,
    purchase_date DATE NOT NULL,
    expiry_date DATE,
    supplier_id INTEGER,
    purchase_price DECIMAL(10,2),
    storage_location VARCHAR(100), -- Posizione in magazzino
    temperature_zone VARCHAR(50), -- Zona temperatura (frigo, congelatore, scaffale)
    quality_status VARCHAR(20) DEFAULT 'good', -- good, damaged, expired
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (unit_id) REFERENCES units_of_measure(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

-- ===== TABELLE CLIENTI =====

-- Tabella clienti
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    postal_code VARCHAR(10),
    country VARCHAR(100) DEFAULT 'Italia',
    birth_date DATE,
    customer_type VARCHAR(20) DEFAULT 'individual', -- individual, business
    company_name VARCHAR(200), -- Per clienti business
    vat_number VARCHAR(50), -- Partita IVA
    tax_code VARCHAR(50), -- Codice fiscale
    preferences TEXT, -- JSON con preferenze cliente
    allergies TEXT, -- Allergie alimentari
    loyalty_points INTEGER DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0.00,
    last_purchase_date DATE,
    is_active BOOLEAN DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- ===== TABELLE FORNITORI =====

-- Tabella fornitori
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    contact_person VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    postal_code VARCHAR(10),
    country VARCHAR(100) DEFAULT 'Italia',
    vat_number VARCHAR(50),
    tax_code VARCHAR(50),
    bank_details TEXT, -- Dettagli bancari per pagamenti
    payment_terms INTEGER DEFAULT 30, -- Giorni di pagamento
    delivery_terms TEXT,
    quality_rating INTEGER DEFAULT 5, -- Rating qualità 1-5
    reliability_rating INTEGER DEFAULT 5, -- Rating affidabilità 1-5
    certifications TEXT, -- Certificazioni (HACCP, BIO, etc.)
    is_active BOOLEAN DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- ===== TABELLE ORDINI E VENDITE =====

-- Tabella ordini clienti
CREATE TABLE IF NOT EXISTS customer_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivery_date DATE,
    delivery_time VARCHAR(20), -- Orario consegna preferito
    status VARCHAR(20) DEFAULT 'nuovo', -- nuovo, in_preparazione, pronto, consegnato, annullato
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    tax_amount DECIMAL(10,2) DEFAULT 0.00,
    final_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    payment_method VARCHAR(20) DEFAULT 'contanti',
    payment_status VARCHAR(20) DEFAULT 'pending', -- pending, paid, partial, overdue
    payment_due_date DATE,
    delivery_address TEXT,
    delivery_notes TEXT,
    special_instructions TEXT,
    is_delivery BOOLEAN DEFAULT 0,
    delivery_fee DECIMAL(10,2) DEFAULT 0.00,
    created_by INTEGER NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Tabella dettagli ordini
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    unit_id INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    discount_percentage REAL DEFAULT 0.0,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES customer_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (unit_id) REFERENCES units_of_measure(id)
);

-- Tabella vendite (transazioni)
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_number VARCHAR(50) UNIQUE NOT NULL,
    order_id INTEGER,
    customer_id INTEGER,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    tax_amount DECIMAL(10,2) DEFAULT 0.00,
    final_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'paid',
    cashier_id INTEGER NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES customer_orders(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (cashier_id) REFERENCES users(id)
);

-- Tabella dettagli vendite
CREATE TABLE IF NOT EXISTS sale_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    unit_id INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (unit_id) REFERENCES units_of_measure(id)
);

-- ===== TABELLE FORNITORI E APPROVVIGIONAMENTO =====

-- Tabella ordini fornitori
CREATE TABLE IF NOT EXISTS supplier_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    supplier_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    status VARCHAR(20) DEFAULT 'pending', -- pending, confirmed, shipped, delivered, cancelled
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    tax_amount DECIMAL(10,2) DEFAULT 0.00,
    final_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    payment_status VARCHAR(20) DEFAULT 'pending',
    payment_due_date DATE,
    delivery_notes TEXT,
    created_by INTEGER NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Tabella dettagli ordini fornitori
CREATE TABLE IF NOT EXISTS supplier_order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    unit_id INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    received_quantity REAL DEFAULT 0.0,
    quality_status VARCHAR(20) DEFAULT 'good',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_order_id) REFERENCES supplier_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (unit_id) REFERENCES units_of_measure(id)
);

-- ===== TABELLE PAGAMENTI =====

-- Tabella pagamenti
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_number VARCHAR(50) UNIQUE NOT NULL,
    payment_type VARCHAR(20) NOT NULL, -- income, expense
    related_id INTEGER, -- ID dell'ordine/vendita/fornitore correlato
    related_type VARCHAR(20), -- order, sale, supplier
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    payment_date DATE NOT NULL,
    reference_number VARCHAR(100), -- Numero riferimento bancario
    bank_account VARCHAR(100),
    notes TEXT,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- ===== TABELLE PERSONALE =====

-- Tabella dipendenti
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    birth_date DATE,
    hire_date DATE NOT NULL,
    position VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    salary DECIMAL(10,2),
    hourly_rate DECIMAL(8,2),
    contract_type VARCHAR(20) DEFAULT 'full_time', -- full_time, part_time, contractor
    is_active BOOLEAN DEFAULT 1,
    skills TEXT, -- Competenze specifiche
    certifications TEXT, -- Certificazioni professionali
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Tabella turni di lavoro
CREATE TABLE IF NOT EXISTS work_shifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    shift_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    break_duration INTEGER DEFAULT 30, -- Minuti di pausa
    hours_worked DECIMAL(4,2) NOT NULL,
    hourly_rate DECIMAL(8,2),
    total_pay DECIMAL(10,2),
    shift_type VARCHAR(20) DEFAULT 'regular', -- regular, overtime, holiday
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- ===== TABELLE ANALYTICS E REPORTING =====

-- Tabella metriche giornaliere
CREATE TABLE IF NOT EXISTS daily_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_date DATE NOT NULL UNIQUE,
    total_sales DECIMAL(10,2) DEFAULT 0.00,
    total_orders INTEGER DEFAULT 0,
    total_customers INTEGER DEFAULT 0,
    total_products_sold INTEGER DEFAULT 0,
    average_order_value DECIMAL(10,2) DEFAULT 0.00,
    total_costs DECIMAL(10,2) DEFAULT 0.00,
    gross_profit DECIMAL(10,2) DEFAULT 0.00,
    net_profit DECIMAL(10,2) DEFAULT 0.00,
    profit_margin DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella attività (log)
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50), -- product, customer, order, sale, etc.
    entity_id INTEGER,
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Tabella impostazioni sistema
CREATE TABLE IF NOT EXISTS system_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(20) DEFAULT 'string', -- string, number, boolean, json
    description TEXT,
    category VARCHAR(50) DEFAULT 'general',
    is_editable BOOLEAN DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== INDICI PER PERFORMANCE =====

-- Indici per tabelle principali
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_code ON products(code);
CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active);

CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_expiry ON inventory(expiry_date);
CREATE INDEX IF NOT EXISTS idx_inventory_batch ON inventory(batch_number);

CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_customers_active ON customers(is_active);

CREATE INDEX IF NOT EXISTS idx_orders_customer ON customer_orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON customer_orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON customer_orders(status);

CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_cashier ON sales(cashier_id);

CREATE INDEX IF NOT EXISTS idx_suppliers_active ON suppliers(is_active);
CREATE INDEX IF NOT EXISTS idx_supplier_orders_supplier ON supplier_orders(supplier_id);
CREATE INDEX IF NOT EXISTS idx_supplier_orders_date ON supplier_orders(order_date);

CREATE INDEX IF NOT EXISTS idx_employees_active ON employees(is_active);
CREATE INDEX IF NOT EXISTS idx_employees_position ON employees(position);
CREATE INDEX IF NOT EXISTS idx_shifts_employee ON work_shifts(employee_id);
CREATE INDEX IF NOT EXISTS idx_shifts_date ON work_shifts(shift_date);

CREATE INDEX IF NOT EXISTS idx_activity_log_user ON activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_date ON activity_log(created_at);
CREATE INDEX IF NOT EXISTS idx_activity_log_entity ON activity_log(entity_type, entity_id);

-- ===== TRIGGER PER TIMESTAMP =====

-- Trigger per aggiornamento timestamp
CREATE TRIGGER IF NOT EXISTS update_products_timestamp 
    AFTER UPDATE ON products
    BEGIN
        UPDATE products SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_customers_timestamp 
    AFTER UPDATE ON customers
    BEGIN
        UPDATE customers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_suppliers_timestamp 
    AFTER UPDATE ON suppliers
    BEGIN
        UPDATE suppliers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_orders_timestamp 
    AFTER UPDATE ON customer_orders
    BEGIN
        UPDATE customer_orders SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_supplier_orders_timestamp 
    AFTER UPDATE ON supplier_orders
    BEGIN
        UPDATE supplier_orders SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_employees_timestamp 
    AFTER UPDATE ON employees
    BEGIN
        UPDATE employees SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_users_timestamp 
    AFTER UPDATE ON users
    BEGIN
        UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- ===== VISTE UTILI =====

-- Vista prodotti con informazioni complete
CREATE VIEW IF NOT EXISTS v_products_complete AS
SELECT 
    p.id,
    p.name,
    p.code,
    p.barcode,
    pc.name as category_name,
    pc.color as category_color,
    uom.name as unit_name,
    uom.symbol as unit_symbol,
    p.selling_price,
    p.cost_price,
    p.min_stock_level,
    p.max_stock_level,
    COALESCE(SUM(i.quantity), 0) as current_stock,
    p.is_active,
    p.created_at
FROM products p
LEFT JOIN product_categories pc ON p.category_id = pc.id
LEFT JOIN units_of_measure uom ON p.unit_id = uom.id
LEFT JOIN inventory i ON p.id = i.product_id AND i.quality_status = 'good'
GROUP BY p.id;

-- Vista ordini con informazioni cliente
CREATE VIEW IF NOT EXISTS v_orders_complete AS
SELECT 
    co.id,
    co.order_number,
    co.order_date,
    co.delivery_date,
    co.status,
    co.total_amount,
    co.final_amount,
    co.payment_status,
    c.first_name || ' ' || c.last_name as customer_name,
    c.phone as customer_phone,
    c.email as customer_email,
    u.first_name || ' ' || u.last_name as created_by_name
FROM customer_orders co
LEFT JOIN customers c ON co.customer_id = c.id
LEFT JOIN users u ON co.created_by = u.id;

-- Vista vendite giornaliere
CREATE VIEW IF NOT EXISTS v_daily_sales AS
SELECT 
    DATE(sale_date) as sale_day,
    COUNT(*) as total_sales,
    SUM(final_amount) as total_revenue,
    AVG(final_amount) as average_sale_value,
    COUNT(DISTINCT customer_id) as unique_customers
FROM sales
GROUP BY DATE(sale_date);

-- ===== DATI INIZIALI =====

-- Inserimento ruoli utente predefiniti
INSERT OR IGNORE INTO user_roles (name, display_name, permissions, description) VALUES
('admin', 'Amministratore', '["all"]', 'Accesso completo a tutte le funzionalità'),
('manager', 'Manager', '["inventario", "vendite", "clienti", "analytics"]', 'Gestione operativa completa'),
('venditore', 'Venditore', '["vendite", "clienti"]', 'Gestione vendite e clienti'),
('magazziniere', 'Magazziniere', '["inventario"]', 'Gestione inventario e scorte'),
('viewer', 'Visualizzatore', '["analytics"]', 'Solo visualizzazione report');

-- Inserimento unità di misura predefinite
INSERT OR IGNORE INTO units_of_measure (name, symbol, type, conversion_factor, is_base_unit) VALUES
('chilogrammo', 'kg', 'weight', 1.0, 1),
('grammo', 'g', 'weight', 0.001, 0),
('ettogrammo', 'hg', 'weight', 0.1, 0),
('litro', 'L', 'volume', 1.0, 1),
('millilitro', 'ml', 'volume', 0.001, 0),
('pezzo', 'pz', 'pieces', 1.0, 1),
('confezione', 'conf', 'pieces', 1.0, 0);

-- Inserimento categorie prodotti predefinite
INSERT OR IGNORE INTO product_categories (name, color, description) VALUES
('Carne Bovina', '#8B4513', 'Carne bovina e derivati'),
('Carne Suina', '#FFB6C1', 'Carne suina e derivati'),
('Pollame', '#FFD700', 'Pollame e volatili'),
('Salumi', '#CD853F', 'Salumi e insaccati'),
('Prodotti Freschi', '#90EE90', 'Verdure, formaggi, latticini'),
('Surgelati', '#87CEEB', 'Prodotti surgelati');

-- Inserimento impostazioni sistema predefinite
INSERT OR IGNORE INTO system_settings (setting_key, setting_value, setting_type, description, category) VALUES
('company_name', 'Macelleria Ezio', 'string', 'Nome dell''azienda', 'general'),
('company_address', 'Via Roma 123, 00100 Roma', 'string', 'Indirizzo dell''azienda', 'general'),
('company_phone', '+39 06 1234567', 'string', 'Telefono dell''azienda', 'general'),
('company_email', 'info@macelleriaezio.it', 'string', 'Email dell''azienda', 'general'),
('default_currency', 'EUR', 'string', 'Valuta predefinita', 'general'),
('tax_rate', '22', 'number', 'Aliquota IVA percentuale', 'tax'),
('low_stock_threshold', '10', 'number', 'Soglia scorte basse', 'inventory'),
('expiry_warning_days', '3', 'number', 'Giorni di preavviso per scadenze', 'inventory'),
('auto_backup_enabled', 'true', 'boolean', 'Backup automatico abilitato', 'backup'),
('backup_frequency_hours', '24', 'number', 'Frequenza backup in ore', 'backup');

-- Inserimento utente amministratore predefinito
-- Password: admin123
INSERT OR IGNORE INTO users (username, email, password_hash, first_name, last_name, role_id, is_admin, created_by) VALUES
('admin', 'admin@macelleriaezio.it', '$2b$12$N7ODldIPrnAg078f8VOOb.XRd.cEHJZ6YYhrDTSAE5BF9r52Km1Qm', 'Admin', 'Sistema', 1, 1, 1);

-- ===== COMMENTI FINALI =====

-- Schema creato con successo
-- Database ottimizzato per performance con indici appropriati
-- Trigger per mantenimento timestamp automatici
-- Viste per query complesse frequenti
-- Dati iniziali per configurazione base
-- Sistema di permessi granulare
-- Tracciabilità completa delle attività
