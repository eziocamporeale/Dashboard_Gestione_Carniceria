# 🔧 Setup Tabella Employees

## ❌ Problema Attuale
La tabella `employees` non esiste nel database Supabase. Questo causa l'errore:
```
Could not find the 'name' column of 'employees' in the schema cache
```

## ✅ Soluzione

### Opzione 1: Creazione Manuale (Raccomandato)
1. Vai al [Dashboard Supabase](https://supabase.com/dashboard)
2. Seleziona il tuo progetto
3. Vai a **Table Editor**
4. Clicca su **"Create a new table"**
5. Nome tabella: `employees`
6. Usa questo script SQL:

```sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    address TEXT,
    position VARCHAR(255) NOT NULL,
    department VARCHAR(100) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'Activo',
    contract_type VARCHAR(100) DEFAULT 'Tiempo Completo',
    emergency_contact TEXT,
    emergency_phone VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Opzione 2: Usa SQL Editor
1. Vai a **SQL Editor** in Supabase
2. Incolla lo script SQL completo da `create_employees_table.sql`
3. Esegui lo script

## 🧪 Test
Dopo aver creato la tabella, esegui:
```bash
python3 create_employees_table.py
```

## 📋 Struttura Tabella
- `id`: Chiave primaria auto-incrementale
- `name`: Nome completo (obbligatorio)
- `email`: Email unica (obbligatorio)
- `phone`: Telefono
- `address`: Indirizzo
- `position`: Posizione lavorativa (obbligatorio)
- `department`: Dipartimento (obbligatorio)
- `salary`: Stipendio (obbligatorio)
- `hire_date`: Data assunzione (obbligatorio)
- `status`: Stato (default: 'Activo')
- `contract_type`: Tipo contratto (default: 'Tiempo Completo')
- `emergency_contact`: Contatto emergenza
- `emergency_phone`: Telefono emergenza
- `notes`: Note aggiuntive
- `created_at`: Data creazione (automatica)
- `updated_at`: Data aggiornamento (automatica)

## 🎯 Risultato Atteso
Dopo la creazione della tabella, il form di creazione impiegati funzionerà correttamente e vedrai le richieste POST nei log del database.
