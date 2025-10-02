-- ==================== CREAZIONE TABELLA activity_log ====================

-- Tabella per log delle attività utente
CREATE TABLE IF NOT EXISTS activity_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    activity_type VARCHAR(100) NOT NULL,
    description TEXT,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indice per migliorare le performance
CREATE INDEX IF NOT EXISTS idx_activity_log_user_id ON activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_timestamp ON activity_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_activity_log_activity_type ON activity_log(activity_type);

-- Trigger per aggiornare updated_at
CREATE OR REPLACE FUNCTION update_activity_log_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_activity_log_updated_at 
    BEFORE UPDATE ON activity_log 
    FOR EACH ROW 
    EXECUTE FUNCTION update_activity_log_updated_at();

-- Inserisci un log di test
INSERT INTO activity_log (user_id, activity_type, description, ip_address) 
VALUES (
    '00000000-0000-0000-0000-000000000101', 
    'table_created', 
    'Tabella activity_log creata con successo', 
    '127.0.0.1'
);
