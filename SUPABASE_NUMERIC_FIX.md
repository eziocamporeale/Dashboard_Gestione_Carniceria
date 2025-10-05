# 🔧 Fix Numeric Field Overflow - Supabase

## 🚨 Problema Identificato
Errore: `numeric field overflow: A field with precision 5, scale 2 must round to an absolute value less than 10^3`

Il campo `amount` nelle tabelle `daily_income` e `daily_expenses` ha precisione `NUMERIC(5,2)`, che supporta solo valori fino a **999.99**.

## 🎯 Soluzione

### Metodo 1: Dashboard Supabase (Raccomandato)

1. **Vai alla Dashboard Supabase:**
   - Accedi a: https://supabase.com/dashboard
   - Seleziona il tuo progetto: `xaxzwfuedzwhsshottum`

2. **Naviga a Table Editor:**
   - Clicca su "Table Editor" nel menu laterale
   - Seleziona la tabella `daily_income`

3. **Modifica Schema:**
   - Clicca sull'icona "⚙️ Settings" accanto al nome della tabella
   - Seleziona "Edit Column" per la colonna `amount`
   - Cambia il tipo da `NUMERIC(5,2)` a `NUMERIC(10,2)`
   - Salva le modifiche

4. **Ripeti per daily_expenses:**
   - Vai alla tabella `daily_expenses`
   - Modifica la colonna `amount` da `NUMERIC(5,2)` a `NUMERIC(10,2)`
   - Salva le modifiche

### Metodo 2: SQL Editor Supabase

1. **Vai a SQL Editor:**
   - Clicca su "SQL Editor" nel menu laterale

2. **Esegui questi comandi:**
   ```sql
   -- Fix daily_income
   ALTER TABLE daily_income 
   ALTER COLUMN amount TYPE NUMERIC(10,2);
   
   -- Fix daily_expenses
   ALTER TABLE daily_expenses 
   ALTER COLUMN amount TYPE NUMERIC(10,2);
   ```

3. **Verifica le modifiche:**
   ```sql
   SELECT 
       table_name,
       column_name,
       data_type,
       numeric_precision,
       numeric_scale
   FROM information_schema.columns 
   WHERE table_name IN ('daily_income', 'daily_expenses') 
   AND column_name = 'amount';
   ```

### Metodo 3: Test Rapido

Dopo aver applicato il fix, testa con questo importo:

```sql
INSERT INTO daily_expenses (
    date, amount, category, description, supplier, payment_method
) VALUES (
    '2025-01-05', 8498.42, 'Compra Carnes', 'Test importo grande', 'Toledo Import', 'Efectivo'
);
```

## 📊 Risultato Atteso

Dopo il fix, il campo `amount` supporterà:
- **Precisione**: 10 cifre totali
- **Decimali**: 2 cifre
- **Range**: da -99,999,999.99 a +99,999,999.99

## ⚠️ Importante

- **Backup**: Assicurati di avere un backup prima di modificare lo schema
- **Test**: Verifica sempre con un importo di test prima di inserire dati reali
- **Tempo**: L'operazione potrebbe richiedere alcuni minuti per tabelle grandi

## 🎉 Dopo il Fix

Potrai inserire importi come:
- ✅ 8498.42 (il tuo importo attuale)
- ✅ 15000.00
- ✅ 99999.99
- ✅ Qualsiasi importo ragionevole per una macelleria

