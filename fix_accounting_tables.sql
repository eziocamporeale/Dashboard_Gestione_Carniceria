-- Script per correggere e verificare le tabelle di accounting
-- Creato da Ezio Camporeale

-- Verifica se le tabelle esistono e creale se necessario
CREATE TABLE IF NOT EXISTS daily_income (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    amount DECIMAL(10,2) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    payment_method VARCHAR(50) DEFAULT 'Efectivo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    amount DECIMAL(10,2) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    supplier VARCHAR(100),
    payment_method VARCHAR(50) DEFAULT 'Efectivo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS accounting_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense')),
    color VARCHAR(7) DEFAULT '#636EFA',
    icon VARCHAR(50) DEFAULT '💰',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL UNIQUE,
    total_income DECIMAL(10,2) DEFAULT 0,
    total_expenses DECIMAL(10,2) DEFAULT 0,
    net_profit DECIMAL(10,2) DEFAULT 0,
    profit_margin DECIMAL(5,2) DEFAULT 0,
    transactions_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserisci categorie predefinite se non esistono
INSERT INTO accounting_categories (name, type, color, icon) VALUES
-- Categorie entrate
('Ventas Carnes', 'income', '#00CC96', '🥩'),
('Ventas Embutidos', 'income', '#00CC96', '🌭'),
('Ventas Pollo', 'income', '#00CC96', '🐔'),
('Ventas Varios', 'income', '#00CC96', '🛒'),
('Otros Ingresos', 'income', '#00CC96', '💰'),
('Test Category', 'income', '#00CC96', '🧪'),

-- Categorie uscite
('Compra Carnes', 'expense', '#FF6692', '🥩'),
('Compra Embutidos', 'expense', '#FF6692', '🌭'),
('Compra Pollo', 'expense', '#FF6692', '🐔'),
('Gastos Operativos', 'expense', '#FF6692', '⚙️'),
('Servicios Públicos', 'expense', '#FF6692', '💡'),
('Alquiler', 'expense', '#FF6692', '🏠'),
('Sueldos', 'expense', '#FF6692', '👥'),
('Otros Gastos', 'expense', '#FF6692', '💸')
ON CONFLICT (name) DO NOTHING;

-- Crea indici per performance
CREATE INDEX IF NOT EXISTS idx_daily_income_date ON daily_income(date);
CREATE INDEX IF NOT EXISTS idx_daily_expenses_date ON daily_expenses(date);
CREATE INDEX IF NOT EXISTS idx_daily_reports_date ON daily_reports(date);
CREATE INDEX IF NOT EXISTS idx_accounting_categories_type ON accounting_categories(type);

-- Verifica la struttura delle tabelle
SELECT 'daily_income' as table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'daily_income' 
ORDER BY ordinal_position;

SELECT 'daily_expenses' as table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'daily_expenses' 
ORDER BY ordinal_position;

SELECT 'daily_reports' as table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'daily_reports' 
ORDER BY ordinal_position;

SELECT 'accounting_categories' as table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'accounting_categories' 
ORDER BY ordinal_position;

-- Conta i record nelle tabelle
SELECT 'daily_income' as table_name, COUNT(*) as record_count FROM daily_income
UNION ALL
SELECT 'daily_expenses' as table_name, COUNT(*) as record_count FROM daily_expenses
UNION ALL
SELECT 'daily_reports' as table_name, COUNT(*) as record_count FROM daily_reports
UNION ALL
SELECT 'accounting_categories' as table_name, COUNT(*) as record_count FROM accounting_categories;
