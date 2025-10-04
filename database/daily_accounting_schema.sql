-- Schema per il sistema di contabilità giornaliera
-- Creato da Ezio Camporeale

-- Tabella per le entrate giornaliere
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

-- Tabella per le uscite giornaliere
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

-- Tabella per le categorie personalizzabili
CREATE TABLE IF NOT EXISTS accounting_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense')),
    color VARCHAR(7) DEFAULT '#636EFA',
    icon VARCHAR(50) DEFAULT '💰',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella per i report giornalieri (calcolati automaticamente)
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

-- Inserisci categorie predefinite
INSERT INTO accounting_categories (name, type, color, icon) VALUES
-- Categorie entrate
('Ventas Carnes', 'income', '#00CC96', '🥩'),
('Ventas Embutidos', 'income', '#00CC96', '🌭'),
('Ventas Pollo', 'income', '#00CC96', '🐔'),
('Ventas Varios', 'income', '#00CC96', '🛒'),
('Otros Ingresos', 'income', '#00CC96', '💰'),

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

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_daily_income_date ON daily_income(date);
CREATE INDEX IF NOT EXISTS idx_daily_expenses_date ON daily_expenses(date);
CREATE INDEX IF NOT EXISTS idx_daily_reports_date ON daily_reports(date);
CREATE INDEX IF NOT EXISTS idx_accounting_categories_type ON accounting_categories(type);

-- Trigger per aggiornare i report giornalieri
CREATE OR REPLACE FUNCTION update_daily_report()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO daily_reports (date, total_income, total_expenses, net_profit, profit_margin, transactions_count)
    SELECT 
        COALESCE(NEW.date, OLD.date),
        COALESCE(income.total, 0),
        COALESCE(expenses.total, 0),
        COALESCE(income.total, 0) - COALESCE(expenses.total, 0),
        CASE 
            WHEN COALESCE(income.total, 0) > 0 
            THEN ((COALESCE(income.total, 0) - COALESCE(expenses.total, 0)) / income.total * 100)
            ELSE 0 
        END,
        COALESCE(income.count, 0) + COALESCE(expenses.count, 0)
    FROM 
        (SELECT date, SUM(amount) as total, COUNT(*) as count 
         FROM daily_income 
         WHERE date = COALESCE(NEW.date, OLD.date) 
         GROUP BY date) income
    FULL OUTER JOIN
        (SELECT date, SUM(amount) as total, COUNT(*) as count 
         FROM daily_expenses 
         WHERE date = COALESCE(NEW.date, OLD.date) 
         GROUP BY date) expenses
    ON income.date = expenses.date
    ON CONFLICT (date) DO UPDATE SET
        total_income = EXCLUDED.total_income,
        total_expenses = EXCLUDED.total_expenses,
        net_profit = EXCLUDED.net_profit,
        profit_margin = EXCLUDED.profit_margin,
        transactions_count = EXCLUDED.transactions_count,
        updated_at = CURRENT_TIMESTAMP;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger per entrate
DROP TRIGGER IF EXISTS trigger_update_daily_report_income ON daily_income;
CREATE TRIGGER trigger_update_daily_report_income
    AFTER INSERT OR UPDATE OR DELETE ON daily_income
    FOR EACH ROW EXECUTE FUNCTION update_daily_report();

-- Trigger per uscite
DROP TRIGGER IF EXISTS trigger_update_daily_report_expenses ON daily_expenses;
CREATE TRIGGER trigger_update_daily_report_expenses
    AFTER INSERT OR UPDATE OR DELETE ON daily_expenses
    FOR EACH ROW EXECUTE FUNCTION update_daily_report();
