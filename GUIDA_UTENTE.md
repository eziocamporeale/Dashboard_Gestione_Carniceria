# 🥩 Guida Utente - Dashboard Gestione Macelleria

## 📋 Indice
1. [Introduzione](#introduzione)
2. [Installazione e Setup](#installazione-e-setup)
3. [Primo Accesso](#primo-accesso)
4. [Navigazione](#navigazione)
5. [Funzionalità Principali](#funzionalità-principali)
6. [Gestione Prodotti](#gestione-prodotti)
7. [Gestione Clienti](#gestione-clienti)
8. [Gestione Vendite](#gestione-vendite)
9. [Analytics e Report](#analytics-e-report)
10. [Impostazioni](#impostazioni)
11. [FAQ](#faq)

---

## 🎯 Introduzione

La **Dashboard Gestione Macelleria** è un sistema completo per la gestione di una macelleria, sviluppato da Ezio Camporeale. Il sistema offre funzionalità avanzate per:

- **Gestione Inventario**: Controllo completo di carne, prodotti freschi e surgelati
- **Gestione Vendite**: Tracking ordini, fatturazione e pagamenti
- **Gestione Clienti**: Database clienti con preferenze e storico acquisti
- **Gestione Fornitori**: Controllo fornitori, ordini e pagamenti
- **Analytics**: Reportistica completa su vendite, profitti e performance
- **Gestione Personale**: Controllo dipendenti, turni e produttività

---

## 🚀 Installazione e Setup

### Requisiti di Sistema
- **Python 3.8+**
- **Streamlit**
- **SQLite** (incluso con Python)

### Installazione Dipendenze
```bash
pip install -r requirements.txt
```

### Inizializzazione Database
```bash
python3 database/init_database.py
```

### Avvio Applicazione
```bash
streamlit run app.py
```

L'applicazione sarà disponibile su: **http://localhost:8501**

---

## 🔐 Primo Accesso

### Accesso al Sistema
⚠️ **IMPORTANTE**: Contatta l'amministratore per ottenere le credenziali di accesso!

### Cambio Password
1. Accedi al sistema
2. Vai su **⚙️ Impostazioni**
3. Seleziona **🔑 Cambio Password**
4. Inserisci password attuale e nuova password
5. Conferma il cambio

---

## 🧭 Navigazione

### Sidebar Principale
La sidebar contiene:
- **👤 Informazioni Utente**: Nome, ruolo, permessi
- **🧭 Menu Navigazione**: Sezioni principali
- **⚡ Azioni Rapide**: Operazioni frequenti
- **ℹ️ Informazioni Sistema**: Versione e stato

### Sezioni Disponibili
- **🏠 Dashboard**: Panoramica generale e KPI
- **📦 Inventario**: Gestione prodotti e scorte
- **🛒 Vendite**: Sistema vendite e POS
- **👥 Clienti**: Database clienti e CRM
- **🚚 Fornitori**: Gestione fornitori
- **👨‍💼 Personale**: Gestione dipendenti
- **📊 Analytics**: Report e statistiche
- **⚙️ Impostazioni**: Configurazioni sistema

---

## 🏠 Funzionalità Principali

### Dashboard Principale
La dashboard mostra:

#### KPI Principali
- **💰 Vendite Oggi**: Importo e numero transazioni
- **📋 Ordini Oggi**: Numero ordini e valore
- **👥 Clienti Totali**: Numero clienti attivi
- **📦 Prodotti Totali**: Prodotti in catalogo

#### Alert e Notifiche
- **⚠️ Alert Scorte**: Prodotti con scorte basse
- **📅 Scadenze Prossime**: Prodotti in scadenza

#### Grafici Interattivi
- **📈 Vendite Ultimi 7 Giorni**: Trend vendite
- **🏆 Prodotti Più Venduti**: Top 5 prodotti

---

## 📦 Gestione Prodotti

### Panoramica Prodotti
Visualizza tutti i prodotti con:
- Nome e codice prodotto
- Categoria e prezzo
- Scorte attuali e minime
- Stato del prodotto

### Aggiunta Nuovo Prodotto
1. Vai su **📦 Inventario** → **➕ Nuovo Prodotto**
2. Compila i campi obbligatori:
   - **Nome Prodotto** (obbligatorio)
   - **Categoria** (obbligatorio)
   - **Unità di Misura** (obbligatorio)
   - **Prezzo di Vendita** (obbligatorio)
3. Opzionalmente compila:
   - Codice prodotto
   - Codice a barre
   - Descrizione
   - Marca e provenienza
   - Prezzo di costo
   - Scorte minime/massime
   - Giorni di conservazione
   - Controllo temperatura
4. Clicca **➕ Aggiungi Prodotto**

### Gestione Scorte
- **📊 Scorte**: Visualizza e gestisci inventario
- **⚠️ Alert**: Prodotti con scorte basse o in scadenza

### Categorie Prodotti Predefinite
- **🥩 Carne Bovina**: Manzo, vitello, bue, scottona
- **🐷 Carne Suina**: Maiale, cinghiale, porchetta
- **🐔 Pollame**: Pollo, tacchino, anatra, coniglio
- **🥓 Salumi**: Prosciutto, salame, mortadella, pancetta
- **🥬 Prodotti Freschi**: Verdure, formaggi, latticini
- **❄️ Surgelati**: Carne, pesce, verdure surgelate

---

## 👥 Gestione Clienti

### Database Clienti
Gestisci i tuoi clienti con:
- **Dati Anagrafici**: Nome, cognome, contatti
- **Indirizzo**: Per consegne
- **Preferenze**: Tagli preferiti, giorni acquisto
- **Allergie**: Informazioni importanti
- **Storico Acquisti**: Analisi comportamento

### Aggiunta Nuovo Cliente
1. Vai su **👥 Clienti** → **➕ Nuovo Cliente**
2. Compila i dati:
   - Nome e cognome (obbligatori)
   - Email e telefono
   - Indirizzo completo
   - Tipo cliente (individual/business)
   - Preferenze e allergie
3. Clicca **➕ Aggiungi Cliente**

### Programmi Fedeltà
- **Punti**: Sistema punti per acquisti
- **Sconti**: Promozioni personalizzate
- **Comunicazioni**: SMS/Email promozionali

---

## 🛒 Gestione Vendite

### Sistema POS
- **Registrazione Vendite**: Rapida e intuitiva
- **Gestione Pagamenti**: Contanti, carte, bonifici
- **Sconti**: Applicazione sconti automatici
- **Fatturazione**: Emissione fatture

### Ordini Clienti
- **Ordini Personalizzati**: Gestione ordini speciali
- **Consegne**: Programmazione consegne
- **Tracking**: Stato ordini in tempo reale

### Metodi di Pagamento
- **💰 Contanti**: Pagamento immediato
- **💳 Carta**: Pagamento con carta
- **🏦 Bonifico**: Pagamento bancario
- **📄 Assegno**: Pagamento con assegno
- **📅 Rate**: Pagamento rateizzato

---

## 📊 Analytics e Report

### Report Disponibili
- **📈 Vendite**: Analisi per periodo, prodotto, cliente
- **💰 Profitti**: Margini, costi, ROI per prodotto
- **📦 Inventario**: Rotazione scorte, sprechi
- **👥 Clienti**: Analisi comportamento, segmentazione
- **👨‍💼 Personale**: Produttività, efficienza

### Export Dati
- **📊 Excel**: Report dettagliati in Excel
- **📄 PDF**: Report formattati in PDF
- **📄 CSV**: Dati per analisi esterne

### Grafici Interattivi
- **Trend Vendite**: Andamento nel tempo
- **Prodotti Top**: Più venduti
- **Analisi Clienti**: Segmentazione
- **Performance**: KPI aziendali

---

## ⚙️ Impostazioni

### Configurazioni Aziendali
- **Nome Azienda**: Macelleria Ezio
- **Indirizzo**: Via Roma 123, 00100 Roma
- **Contatti**: Telefono e email
- **Valuta**: Euro (EUR)

### Impostazioni Sistema
- **IVA**: Aliquota IVA (22%)
- **Scorte**: Soglie scorte basse
- **Scadenze**: Giorni preavviso scadenze
- **Backup**: Configurazione backup automatici

### Gestione Utenti
- **Ruoli**: Admin, Manager, Venditore, Magazziniere, Viewer
- **Permessi**: Controllo accessi granulare
- **Sicurezza**: Password e sessioni

---

## ❓ FAQ

### Domande Frequenti

**Q: Come cambio la password admin?**
A: Vai su Impostazioni → Cambio Password e inserisci la nuova password.

**Q: Come aggiungo un nuovo prodotto?**
A: Vai su Inventario → Nuovo Prodotto e compila il form.

**Q: Come visualizzo le vendite di oggi?**
A: La dashboard principale mostra automaticamente le vendite del giorno.

**Q: Come esporto i dati?**
A: Ogni sezione ha pulsanti di download per Excel e CSV.

**Q: Come gestisco le scorte basse?**
A: Il sistema mostra automaticamente alert per prodotti con scorte basse.

**Q: Come aggiungo un nuovo cliente?**
A: Vai su Clienti → Nuovo Cliente e compila i dati anagrafici.

**Q: Come funziona il sistema di permessi?**
A: Ogni utente ha un ruolo con permessi specifici per accedere alle funzioni.

**Q: Come faccio il backup dei dati?**
A: Il sistema fa backup automatici, ma puoi crearne manuali in Impostazioni.

**Q: Come contatto il supporto?**
A: Contatta Ezio Camporeale per supporto tecnico.

---

## 🆘 Supporto Tecnico

### Contatti
- **Sviluppatore**: Ezio Camporeale
- **Email**: ezio.camporeale@example.com
- **Versione**: 1.0.0

### Log e Debugging
- I log sono salvati in `logs/macelleria.log`
- Per problemi, controlla i log per dettagli
- Il database è in `data/macelleria.db`

### Aggiornamenti
- Controlla regolarmente gli aggiornamenti
- Backup sempre i dati prima degli aggiornamenti
- Segui le istruzioni di migrazione

---

## 📝 Changelog

### Versione 1.0.0 (21/09/2024)
- ✅ Sistema di autenticazione completo
- ✅ Gestione prodotti e inventario
- ✅ Dashboard con KPI principali
- ✅ Gestione clienti base
- ✅ Sistema di permessi granulare
- ✅ Database SQLite ottimizzato
- ✅ Interfaccia moderna e responsive

---

*Guida creata da Ezio Camporeale - Dashboard Gestione Macelleria v1.0.0*

