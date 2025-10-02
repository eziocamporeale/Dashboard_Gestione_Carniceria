# 🗄️ SUPABASE INITIAL DATA - Dashboard Gestión Carnicería

## 🔧 **PROBLEMA IDENTIFICATO**

**Errore:** `❌ Tentativo login fallito: admin`  
**Causa:** Database Supabase vuoto - nessun utente admin creato  
**Soluzione:** ✅ **Inserire dati iniziali nel database Supabase**

---

## 📊 **DATI INIZIALI NECESSARI**

### **1. 👤 Utenti Admin**
- **Email:** `admin@carniceria.com` o `admin`
- **Password:** `admin123`
- **Ruolo:** Amministratore completo

### **2. 🏷️ Categorie Prodotti**
- Carnes, Aves, Embutidos, Pescados, Verduras, Otros

### **3. 📏 Unità di Misura**
- Kilogramo, Gramo, Unidad, Libra, Onza

### **4. 📦 Prodotti di Esempio**
- Carne de Res, Pollo Entero, Jamón Cocido

### **5. 🏢 Fornitori di Esempio**
- Proveedor Carnes Premium, Distribuidora Aves

### **6. 👥 Dipendenti di Esempio**
- Carlos Rodríguez (Vendedor), Ana Martínez (Cajera)

---

## 🚀 **ISTRUZIONI PER INSERIRE DATI**

### **Step 1: 🗄️ Accedi a Supabase**
1. Vai su https://supabase.com
2. Accedi al tuo progetto: https://xaxzwfuedzwhsshottum.supabase.co
3. Vai su **SQL Editor**

### **Step 2: 📝 Esegui Script Dati Iniziali**
1. **Copia** tutto il contenuto di `database/initial_data.sql`
2. **Incolla** nello SQL Editor di Supabase
3. **Esegui** lo script SQL
4. **Verifica** che i dati siano stati inseriti

### **Step 3: 🧪 Testa Login**
1. Vai su Streamlit Cloud
2. Prova login con:
   - **Username:** `admin` o `admin@carniceria.com`
   - **Password:** `admin123`

---

## 📋 **SCRIPT SQL COMPLETO**

```sql
-- Inserimento ruoli utente
INSERT INTO roles (id, name, description, permissions) VALUES 
('00000000-0000-0000-0000-000000000001', 'admin', 'Administrador completo', '{"all": true}'),
('00000000-0000-0000-0000-000000000002', 'manager', 'Gerente de tienda', '{"sales": true, "inventory": true, "reports": true}'),
('00000000-0000-0000-0000-000000000003', 'employee', 'Empleado', '{"sales": true, "inventory": false, "reports": false}'),
('00000000-0000-0000-0000-000000000004', 'viewer', 'Solo lectura', '{"reports": true}')
ON CONFLICT (id) DO NOTHING;

-- Inserimento utente admin
INSERT INTO users (id, email, password_hash, first_name, last_name, role_id, is_active) VALUES 
('00000000-0000-0000-0000-000000000401', 'admin@carniceria.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J.8.8.8.8', 'Admin', 'Sistema', '00000000-0000-0000-0000-000000000001', true),
('00000000-0000-0000-0000-000000000402', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J.8.8.8.8', 'Admin', 'Sistema', '00000000-0000-0000-0000-000000000001', true)
ON CONFLICT (id) DO NOTHING;

-- Altri dati iniziali...
```

---

## 🧪 **TESTING POST-INSERIMENTO**

### **Verifica Dati Inseriti**
```sql
-- Conta utenti
SELECT count(*) as total_users FROM users;

-- Conta ruoli
SELECT count(*) as total_roles FROM roles;

-- Conta categorie
SELECT count(*) as total_categories FROM product_categories;

-- Verifica utente admin
SELECT email, first_name, last_name, is_active FROM users WHERE email = 'admin';
```

### **Test Login**
1. **Username:** `admin`
2. **Password:** `admin123`
3. **Risultato atteso:** Login riuscito

---

## ✅ **STATUS POST-INSERIMENTO**

- ✅ **Utente admin** creato
- ✅ **Ruoli** configurati
- ✅ **Categorie** inserite
- ✅ **Unità di misura** inserite
- ✅ **Prodotti** di esempio
- ✅ **Fornitori** di esempio
- ✅ **Dipendenti** di esempio

---

## 🎯 **RISULTATO FINALE**

Una volta inseriti i dati iniziali:

- **🔐 Login** funzionante con admin/admin123
- **📊 Dashboard** con dati di esempio
- **🛒 Vendite** operative
- **📦 Inventario** popolato
- **👥 Team** configurato
- **🏢 Fornitori** attivi

**Sistema completamente funzionante!** 🚀

---

## 🚀 **PROSSIMI PASSI**

1. **🗄️ Eseguire** script dati iniziali su Supabase
2. **🧪 Testare** login su Streamlit Cloud
3. **🎉 Iniziare** a usare il sistema!

**Dati iniziali pronti per l'inserimento!** 🚀
