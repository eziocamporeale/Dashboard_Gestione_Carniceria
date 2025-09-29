# 🚀 Istruzioni di Avvio - Dashboard Gestione Macelleria

## ✅ **ERRORE RISOLTO**
L'errore `NameError: name 'is_authenticated' is not defined` è stato **corretto** aggiungendo l'import mancante nel file `app.py`.

## 🎯 **Come Avviare il Sistema**

### **Metodo 1: Script Automatico (Consigliato)**
```bash
cd "/Users/ezio/Ezio_Root/CREAZIONE PROGETTI EZIO/DASH_GESTIONE_MACELLERIA"
./AVVIA_MACELLERIA.sh
```

### **Metodo 2: Avvio Manuale**
```bash
cd "/Users/ezio/Ezio_Root/CREAZIONE PROGETTI EZIO/DASH_GESTIONE_MACELLERIA"

# Verifica dipendenze
pip install -r requirements.txt

# Avvia applicazione
streamlit run app.py
```

## 🌐 **Accesso al Sistema**

- **URL**: http://localhost:8501
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **IMPORTANTE**: Cambia la password dopo il primo accesso!

## 🔧 **Risoluzione Problemi**

### **Se vedi errori di import:**
```bash
# Verifica che tutte le dipendenze siano installate
pip install -r requirements.txt

# Verifica che il database sia inizializzato
python3 database/init_database.py
```

### **Se il database non esiste:**
```bash
# Inizializza il database
python3 database/init_database.py
```

### **Se Streamlit non si avvia:**
```bash
# Installa Streamlit
pip install streamlit

# Avvia con porta specifica
streamlit run app.py --server.port 8501
```

## 📱 **Funzionalità Disponibili**

Una volta avviato il sistema, avrai accesso a:

- **🏠 Dashboard**: KPI e grafici in tempo reale
- **📦 Inventario**: Gestione prodotti e scorte
- **👥 Clienti**: Database clienti con CRM
- **🛒 Vendite**: Sistema POS integrato
- **📊 Analytics**: Report e statistiche
- **⚙️ Impostazioni**: Configurazioni sistema

## 🎉 **Sistema Pronto!**

La Dashboard Gestione Macelleria è **completamente funzionale** e pronta per gestire la tua attività!

---

*Creato da Ezio Camporeale - Dashboard Gestione Macelleria v1.0.0*
