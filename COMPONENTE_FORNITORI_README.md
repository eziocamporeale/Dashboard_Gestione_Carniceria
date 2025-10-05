# 🚚 Componente Fornitori - CRUD Completo

## 📋 Panoramica

Il componente fornitori fornisce funzionalità CRUD complete per la gestione dei fornitori nella dashboard di gestione macelleria. Include validazione dati, gestione errori e interfaccia utente intuitiva.

## 🏗️ Struttura Componente

```
components/fornitori/
├── __init__.py              # Inizializzazione modulo
├── suppliers_manager.py     # Logica CRUD e gestione dati
└── suppliers_ui.py          # Interfaccia utente Streamlit
```

## 🚀 Funzionalità Implementate

### ✅ CREATE (Creazione)
- **Form di creazione** con tutti i campi necessari
- **Validazione dati** in tempo reale
- **Gestione errori** completa
- **Riepilogo** del fornitore creato

### ✅ READ (Lettura)
- **Lista fornitori** con tabella interattiva
- **Filtri** per fornitori attivi/inattivi
- **Ricerca** per nome, contatto o email
- **Esportazione CSV** della lista
- **Statistiche** dettagliate

### ✅ UPDATE (Aggiornamento)
- **Selezione fornitore** da dropdown
- **Form di modifica** pre-popolato
- **Validazione dati** aggiornata
- **Conferma modifiche** con feedback

### ✅ DELETE (Eliminazione)
- **Soft Delete**: Disattiva fornitore (imposta `is_active=False`)
- **Hard Delete**: Elimina definitivamente il record
- **Conferma eliminazione** per sicurezza
- **Gestione errori** per eliminazioni

## 🗄️ Struttura Database

La tabella `suppliers` deve contenere le seguenti colonne:

```sql
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    contact_person VARCHAR(255),
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🔧 Installazione e Configurazione

### 1. **Verifica Struttura Database**
```bash
python check_suppliers_table_structure.py
```

### 2. **Correggi Struttura Database (se necessario)**
Esegui lo script SQL in Supabase:
```bash
# Il file fix_suppliers_table.sql contiene le correzioni necessarie
```

### 3. **Test Componente**
```bash
python test_suppliers_crud_complete.py
```

## 📱 Utilizzo Interfaccia

### **Tab 1: Lista Fornitori**
- Visualizza tutti i fornitori in tabella
- Filtra per fornitori attivi
- Cerca per nome, contatto o email
- Esporta lista in CSV
- Aggiorna dati in tempo reale

### **Tab 2: Nuovo Fornitore**
- Compila form con tutti i campi
- Validazione automatica
- Salvataggio con conferma
- Riepilogo fornitore creato

### **Tab 3: Modifica Fornitore**
- Seleziona fornitore da dropdown
- Modifica dati pre-popolati
- Salva modifiche
- Disattiva o elimina fornitore

### **Tab 4: Statistiche**
- Metriche fornitori totali/attivi/inattivi
- Percentuale fornitori attivi
- Grafico a torta distribuzione
- Aggiornamento automatico

## 🔒 Permessi e Sicurezza

Il componente richiede il permesso `"fornitori"` per essere accessibile:

```python
@require_permission("fornitori")
def render_fornitori():
    # ... codice componente
```

## 🧪 Testing

### **Test Automatici**
```bash
python test_suppliers_crud_complete.py
```

Il test verifica:
- ✅ Creazione fornitore
- ✅ Lettura lista fornitori
- ✅ Lettura fornitore per ID
- ✅ Aggiornamento fornitore
- ✅ Eliminazione fornitore (soft/hard)
- ✅ Statistiche fornitori
- ✅ Validazione dati

### **Test Manuali**
1. **Crea un nuovo fornitore** con tutti i campi
2. **Modifica** i dati di un fornitore esistente
3. **Cerca** fornitori per nome
4. **Disattiva** un fornitore
5. **Verifica statistiche** aggiornate

## 🚨 Gestione Errori

### **Errori Comuni**
1. **"Colonna 'notes' non trovata"**
   - **Soluzione**: Esegui `fix_suppliers_table.sql`

2. **"Database non disponibile"**
   - **Soluzione**: Verifica connessione Supabase

3. **"Fornitore non trovato"**
   - **Soluzione**: Verifica ID fornitore

4. **"Email non valida"**
   - **Soluzione**: Controlla formato email

### **Log Errori**
Gli errori vengono registrati e mostrati all'utente con messaggi chiari e soluzioni suggerite.

## 📊 Performance

### **Ottimizzazioni**
- **Lazy Loading**: Carica dati solo quando necessario
- **Caching**: Cache dei dati per ridurre query
- **Paginazione**: Per liste con molti fornitori
- **Filtri**: Riduce carico server

### **Limitazioni**
- **Max fornitori**: Nessun limite impostato
- **Ricerca**: Case-insensitive, substring matching
- **Esportazione**: Limitata a 1000 record per performance

## 🔄 Integrazione App Principale

Il componente è integrato nell'app principale tramite:

```python
def render_fornitori():
    """Renderizza la sezione fornitori"""
    require_permission("fornitori")
    
    try:
        from components.fornitori.suppliers_ui import render_suppliers_page
        render_suppliers_page()
    except ImportError as e:
        st.error(f"❌ Errore nel caricamento del componente fornitori: {e}")
        st.info("🚧 Funzionalità fornitori non disponibile - Contatta l'amministratore")
```

## 🎯 Prossimi Sviluppi

### **Funzionalità Future**
- [ ] **Import/Export** Excel fornitori
- [ ] **Categorie fornitori** (carne, verdura, etc.)
- [ ] **Rating fornitori** (qualità, puntualità)
- [ ] **Storico ordini** per fornitore
- [ ] **Notifiche** scadenze contratti
- [ ] **API REST** per integrazioni esterne

### **Miglioramenti UI**
- [ ] **Drag & Drop** per upload documenti
- [ ] **Filtri avanzati** (data creazione, categoria)
- [ ] **Vista calendario** per scadenze
- [ ] **Dashboard fornitori** personalizzata

## 📞 Supporto

Per problemi o domande:
1. **Verifica log** applicazione
2. **Esegui test** automatici
3. **Controlla database** struttura
4. **Contatta sviluppatore** con dettagli errore

---

**Creato da Ezio Camporeale**  
**Versione**: 1.0  
**Data**: Ottobre 2024
