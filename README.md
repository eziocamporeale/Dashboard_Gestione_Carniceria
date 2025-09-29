# 🥩 Dashboard Gestione Macelleria

## 📋 Descrizione del Progetto
Dashboard completa per la gestione di una macelleria, con funzionalità di inventario, vendite, clienti, fornitori e analytics avanzate.

## 🎯 Obiettivi Principali
- **Gestione Inventario**: Controllo completo di carne, prodotti freschi e surgelati
- **Gestione Vendite**: Tracking ordini, fatturazione e pagamenti
- **Gestione Clienti**: Database clienti con preferenze e storico acquisti
- **Gestione Fornitori**: Controllo fornitori, ordini e pagamenti
- **Analytics**: Reportistica completa su vendite, profitti e performance
- **Gestione Personale**: Controllo dipendenti, turni e produttività

## 🏗️ Struttura del Progetto

```
DASH_GESTIONE_MACELLERIA/
├── 📄 README.md                    # Documentazione principale
├── 📄 requirements.txt             # Dipendenze Python
├── 📄 config.py                    # Configurazione globale
├── 📄 app.py                       # Applicazione principale Streamlit
│
├── 📁 database/                   # Gestione database
│   ├── 📄 schema.sql              # Schema database SQLite
│   ├── 📄 init_database.py        # Inizializzazione database
│   ├── 📄 database_manager.py     # Classe gestione database
│   └── 📄 migrations/             # Migrazioni database
│
├── 📁 components/                 # Componenti Streamlit
│   ├── 📁 auth/                   # Sistema autenticazione
│   ├── 📁 dashboard/              # Dashboard principale
│   ├── 📁 inventario/             # Gestione prodotti
│   ├── 📁 vendite/                # Gestione vendite
│   ├── 📁 clienti/                # Gestione clienti
│   ├── 📁 fornitori/              # Gestione fornitori
│   ├── 📁 personale/              # Gestione dipendenti
│   ├── 📁 analytics/              # Report e statistiche
│   └── 📁 settings/               # Impostazioni
│
├── 📁 utils/                      # Utility e helper
│   ├── 📄 helpers.py              # Funzioni helper generiche
│   ├── 📄 validators.py           # Validazione dati
│   ├── 📄 exporters.py            # Export dati (Excel, PDF)
│   ├── 📄 notifications.py       # Sistema notifiche
│   └── 📄 backup.py               # Sistema backup
│
├── 📁 data/                       # Dati applicazione
│   ├── 📄 macelleria.db           # Database SQLite
│   ├── 📁 uploads/                # File caricati
│   └── 📁 exports/                # File esportati
│
├── 📁 logs/                       # Log applicazione
├── 📁 backups/                    # Backup database
└── 📁 static/                     # File statici
    ├── 📁 css/                    # Fogli di stile
    ├── 📁 js/                     # JavaScript
    └── 📁 images/                 # Immagini
```

## 🚀 Avvio Rapido

### Installazione Dipendenze
```bash
pip install -r requirements.txt
```

### Inizializzazione Database
```bash
python database/init_database.py
```

### Avvio Applicazione
```bash
streamlit run app.py
```

## 🌐 Accesso
- **URL**: http://localhost:8501
- **Database**: SQLite locale
- **Credenziali Default**: admin / admin123

## 📊 Funzionalità Principali

### 🏠 Dashboard Principale
- KPI in tempo reale (vendite, margini, prodotti più venduti)
- Grafici interattivi (trend vendite, analisi stagionalità)
- Alert (scorte basse, prodotti in scadenza, pagamenti scaduti)
- Quick Actions (nuovo ordine, aggiunta prodotto, registrazione vendita)

### 📦 Gestione Inventario
- Catalogo prodotti (carne bovina, suina, pollame, salumi)
- Controllo scorte (quantità disponibili, scadenze, lotti)
- Gestione prezzi (prezzi al kg, sconti, promozioni)
- Tracciabilità (lotto, data macellazione, provenienza)
- Alert scorte (notifiche automatiche per riordino)

### 🛒 Gestione Vendite
- POS integrato (registrazione vendite rapida)
- Ordini clienti (gestione ordini personalizzati)
- Fatturazione (emissione fatture e ricevute)
- Gestione pagamenti (contanti, carte, bonifici, rate)
- Sconti e promozioni (gestione offerte speciali)

### 👥 Gestione Clienti
- Database clienti (dati anagrafici, preferenze, allergie)
- Storico acquisti (analisi comportamento d'acquisto)
- Programmi fedeltà (punti, sconti, promozioni personalizzate)
- Comunicazioni (SMS/Email promozionali, ricette)
- Preferenze (tagli preferiti, giorni di acquisto)

### 🚚 Gestione Fornitori
- Database fornitori (macelli, allevatori, distributori)
- Ordini (gestione ordini di approvvigionamento)
- Controllo qualità (valutazioni fornitori, certificazioni)
- Pagamenti (gestione fatture e pagamenti fornitori)
- Contratti (gestione contratti e condizioni)

### 👨‍💼 Gestione Personale
- Database dipendenti (dati anagrafici, competenze, contratti)
- Turni (gestione orari e turni di lavoro)
- Produttività (tracking performance individuali)
- Formazione (gestione corsi e certificazioni)
- Paghe (calcolo ore lavoro e stipendi)

### 📊 Analytics e Reporting
- Vendite (analisi per periodo, prodotto, cliente)
- Profitti (margini, costi, ROI per prodotto)
- Inventario (rotazione scorte, sprechi, ottimizzazione)
- Clienti (analisi comportamento, segmentazione)
- Personale (produttività, efficienza, costi)

## 🔧 Tecnologie Utilizzate

### Frontend
- **Streamlit**: Framework web per Python
- **Plotly**: Grafici interattivi
- **CSS**: Styling personalizzato

### Backend
- **Python 3.8+**: Linguaggio principale
- **SQLite**: Database locale
- **Pandas**: Manipolazione dati

### Librerie Principali
- **streamlit**: Interfaccia web
- **plotly**: Visualizzazione dati
- **pandas**: Analisi dati
- **sqlite3**: Database
- **bcrypt**: Hashing password
- **openpyxl**: Export Excel

## 🎯 Roadmap Implementazione

### FASE 1: Setup Base (Settimana 1-2)
- [x] Creazione struttura progetto
- [ ] Setup database SQLite
- [ ] Sistema autenticazione
- [ ] Dashboard principale con KPI base
- [ ] Gestione prodotti base

### FASE 2: Core Business (Settimana 3-4)
- [ ] Gestione inventario completa
- [ ] Sistema vendite e POS
- [ ] Gestione clienti base
- [ ] Fatturazione base

### FASE 3: Advanced Features (Settimana 5-6)
- [ ] Gestione fornitori
- [ ] Analytics avanzate
- [ ] Gestione personale
- [ ] Sistema notifiche

### FASE 4: Polish & Deploy (Settimana 7-8)
- [ ] Ottimizzazioni UI/UX
- [ ] Testing completo
- [ ] Backup e sicurezza
- [ ] Documentazione finale

## 🔐 Sicurezza

### Autenticazione
- Hashing password con bcrypt
- Sessioni sicure
- Timeout automatico
- Log accessi

### Autorizzazione
- Sistema ruoli granulare
- Controllo permessi per modulo
- Audit trail attività

### Dati
- Validazione input
- Sanitizzazione dati
- Backup automatici
- Log operazioni critiche

## 📈 Scalabilità

### Database
- Migrazione a PostgreSQL per grandi volumi
- Ottimizzazione query
- Indici appropriati
- Partizionamento tabelle

### Performance
- Caching risultati
- Paginazione dati
- Lazy loading
- Ottimizzazione immagini

### Funzionalità
- API REST per integrazioni
- Webhook per automazioni
- Export/import dati
- Backup cloud

---

*Dashboard creata da Ezio Camporeale - DASH_GESTIONE_MACELLERIA*

