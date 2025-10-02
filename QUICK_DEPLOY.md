# 🚀 QUICK DEPLOY - Dashboard Gestión Carnicería

## ⚡ **DEPLOYMENT RAPIDO (5 MINUTI)**

### **1. 📦 Repository GitHub**
✅ **COMPLETATO** - Codice pushato su GitHub:
- Repository: https://github.com/eziocamporeale/Dashboard_Gestione_Carniceria
- Branch: `main`
- Tutti i file Supabase integrati

### **2. 🗄️ Setup Supabase Database**

**IMPORTANTE:** Eseguire questo script SQL su Supabase:

1. Vai su https://supabase.com
2. Accedi al tuo progetto: https://xaxzwfuedzwhsshottum.supabase.co
3. Vai su **SQL Editor**
4. Copia e incolla tutto il contenuto di `database/supabase_schema.sql`
5. Esegui lo script

### **3. ☁️ Deploy su Streamlit Cloud**

1. **Vai su:** https://share.streamlit.io
2. **Clicca:** "New app"
3. **Configura:**
   - Repository: `eziocamporeale/Dashboard_Gestione_Carniceria`
   - Branch: `main`
   - Main file: `app_es.py`
   - App URL: `dashboard-gestion-carniceria` (opzionale)

4. **Configura Secrets:**
   - Vai su Settings → Secrets
   - Copia il contenuto di `.streamlit/secrets.toml.example`
   - Incolla nelle secrets di Streamlit Cloud

### **4. 🔐 Variabili Ambiente (Streamlit Cloud)**

```toml
[secrets]
SUPABASE_URL = "https://xaxzwfuedzwhsshottum.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhheHp3ZnVlZHp3aHNzaG90dHVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkzODQ0MDgsImV4cCI6MjA3NDk2MDQwOH0.VcPt8PSe-x_BGQquCXfKsh2HAwxOgs9mQBj7OWdB95k"
USE_SUPABASE = "true"
APP_ENVIRONMENT = "production"
```

### **5. 🚀 Deploy!**

1. Clicca **"Deploy!"**
2. Attendi 2-3 minuti
3. Testa l'applicazione

---

## ✅ **CHECKLIST DEPLOYMENT**

- [x] **Repository GitHub** configurato
- [x] **Codice Supabase** integrato
- [x] **Schema database** creato
- [x] **Configurazione Streamlit** pronta
- [x] **Variabili ambiente** configurate
- [ ] **Script SQL** eseguito su Supabase
- [ ] **Deploy** su Streamlit Cloud
- [ ] **Test** funzionalità

---

## 🎯 **RISULTATO FINALE**

**URL Dashboard:** `https://dashboard-gestion-carniceria.streamlit.app`

**Funzionalità:**
- 🛒 Gestione vendite completa
- 📊 Analytics avanzate
- 👥 Gestione team
- 🏢 Gestione fornitori
- 📈 Reportistica Excel
- 🔐 Sicurezza enterprise

**Sistema pronto per produzione!** 🚀
