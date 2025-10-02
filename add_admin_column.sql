-- Aggiungi colonna is_admin alla tabella users
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;

-- Aggiorna l'utente admin per impostare is_admin = TRUE
UPDATE users SET is_admin = TRUE WHERE email = 'admin@carniceria.com';

-- Aggiungi anche la colonna role_name se non esiste
ALTER TABLE users ADD COLUMN IF NOT EXISTS role_name VARCHAR(50) DEFAULT 'employee';

-- Aggiorna l'utente admin per impostare role_name = 'admin'
UPDATE users SET role_name = 'admin' WHERE email = 'admin@carniceria.com';

-- Crea un indice per migliorare le performance
CREATE INDEX IF NOT EXISTS idx_users_is_admin ON users(is_admin);
CREATE INDEX IF NOT EXISTS idx_users_role_name ON users(role_name);

-- Aggiungi commenti per chiarezza
COMMENT ON COLUMN users.is_admin IS 'Indica se l''utente è un amministratore';
COMMENT ON COLUMN users.role_name IS 'Nome del ruolo dell''utente';
