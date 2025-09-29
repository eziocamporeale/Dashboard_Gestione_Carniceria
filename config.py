#!/usr/bin/env python3
"""
Configurazione globale per Dashboard Gestione Macelleria
Creato da Ezio Camporeale
"""

import os
from pathlib import Path
from datetime import timedelta

# ===== CONFIGURAZIONE GENERALE =====

# Nome applicazione
APP_NAME = "Dashboard Gestione Macelleria"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Ezio Camporeale"

# Percorsi file
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
BACKUPS_DIR = BASE_DIR / "backups"
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = DATA_DIR / "uploads"
EXPORTS_DIR = DATA_DIR / "exports"

# Database
DATABASE_PATH = DATA_DIR / "macelleria.db"
DATABASE_BACKUP_RETENTION_DAYS = 30

# ===== CONFIGURAZIONE STREAMLIT =====

# Impostazioni Streamlit
STREAMLIT_CONFIG = {
    "server": {
        "port": 8501,
        "headless": True,
        "enableCORS": False,
        "enableXsrfProtection": True,
    },
    "browser": {
        "gatherUsageStats": False,
    },
    "theme": {
        "primaryColor": "#FF6B35",  # Arancione macelleria
        "backgroundColor": "#FFFFFF",
        "secondaryBackgroundColor": "#F0F2F6",
        "textColor": "#262730",
    }
}

# ===== CONFIGURAZIONE AUTENTICAZIONE =====

# Sicurezza
SECRET_KEY = "macelleria_secret_key_2024_ezio_camporeale"
SESSION_TIMEOUT_HOURS = 8
PASSWORD_MIN_LENGTH = 8

# Ruoli utente
USER_ROLES = {
    "admin": {
        "name": "Amministratore",
        "permissions": ["all"],
        "description": "Accesso completo a tutte le funzionalità"
    },
    "manager": {
        "name": "Manager",
        "permissions": ["inventario", "vendite", "clienti", "analytics"],
        "description": "Gestione operativa completa"
    },
    "venditore": {
        "name": "Venditore",
        "permissions": ["vendite", "clienti"],
        "description": "Gestione vendite e clienti"
    },
    "magazziniere": {
        "name": "Magazziniere",
        "permissions": ["inventario"],
        "description": "Gestione inventario e scorte"
    },
    "viewer": {
        "name": "Visualizzatore",
        "permissions": ["analytics"],
        "description": "Solo visualizzazione report"
    }
}

# ===== CONFIGURAZIONE BUSINESS =====

# Valute
DEFAULT_CURRENCY = "EUR"
CURRENCY_SYMBOL = "€"

# Unità di misura
UNITS_OF_MEASURE = {
    "weight": ["kg", "g", "hg"],
    "volume": ["L", "ml"],
    "pieces": ["pz", "pezzi"]
}

# Categorie prodotti principali
PRODUCT_CATEGORIES = {
    "bovino": {
        "name": "Carne Bovina",
        "color": "#8B4513",
        "subcategories": ["manzo", "vitello", "bue", "scottona"]
    },
    "suino": {
        "name": "Carne Suina", 
        "color": "#FFB6C1",
        "subcategories": ["maiale", "cinghiale", "porchetta"]
    },
    "pollame": {
        "name": "Pollame",
        "color": "#FFD700",
        "subcategories": ["pollo", "tacchino", "anatra", "coniglio"]
    },
    "salumi": {
        "name": "Salumi",
        "color": "#CD853F",
        "subcategories": ["prosciutto", "salame", "mortadella", "pancetta"]
    },
    "freschi": {
        "name": "Prodotti Freschi",
        "color": "#90EE90",
        "subcategories": ["verdure", "formaggi", "latticini"]
    },
    "surgelati": {
        "name": "Surgelati",
        "color": "#87CEEB",
        "subcategories": ["carne", "pesce", "verdure"]
    }
}

# Stati ordini
ORDER_STATUSES = {
    "nuovo": {"name": "Nuovo", "color": "#FF6B35"},
    "in_preparazione": {"name": "In Preparazione", "color": "#FFA500"},
    "pronto": {"name": "Pronto", "color": "#32CD32"},
    "consegnato": {"name": "Consegnato", "color": "#008000"},
    "annullato": {"name": "Annullato", "color": "#FF0000"}
}

# Metodi di pagamento
PAYMENT_METHODS = {
    "contanti": {"name": "Contanti", "icon": "💰"},
    "carta": {"name": "Carta", "icon": "💳"},
    "bonifico": {"name": "Bonifico", "icon": "🏦"},
    "assegno": {"name": "Assegno", "icon": "📄"},
    "rate": {"name": "Rate", "icon": "📅"}
}

# ===== CONFIGURAZIONE NOTIFICHE =====

# Email
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "macelleria@example.com",
    "sender_password": "your_password_here"
}

# Alert configurazione
ALERT_CONFIG = {
    "low_stock_threshold": 10,  # Soglia scorte basse
    "expiry_warning_days": 3,   # Giorni prima scadenza per alert
    "payment_overdue_days": 7   # Giorni per pagamenti scaduti
}

# ===== CONFIGURAZIONE REPORT =====

# Formati export
EXPORT_FORMATS = {
    "excel": {"extension": ".xlsx", "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    "pdf": {"extension": ".pdf", "mime_type": "application/pdf"},
    "csv": {"extension": ".csv", "mime_type": "text/csv"}
}

# Template report
REPORT_TEMPLATES = {
    "vendite_giornaliere": "Report vendite giornaliere",
    "inventario_scorte": "Report scorte inventario",
    "clienti_analisi": "Analisi clienti",
    "fornitori_pagamenti": "Report pagamenti fornitori"
}

# ===== CONFIGURAZIONE BACKUP =====

BACKUP_CONFIG = {
    "auto_backup": True,
    "backup_frequency_hours": 24,
    "backup_retention_days": 30,
    "compress_backups": True
}

# ===== CONFIGURAZIONE LOGGING =====

LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": LOGS_DIR / "macelleria.log",
    "max_size_mb": 10,
    "backup_count": 5
}

# ===== CONFIGURAZIONE PERFORMANCE =====

PERFORMANCE_CONFIG = {
    "cache_ttl_seconds": 300,  # Cache time-to-live
    "max_records_per_page": 100,
    "enable_query_optimization": True,
    "lazy_loading": True
}

# ===== CONFIGURAZIONE INTEGRAZIONI =====

# API esterne (opzionali)
EXTERNAL_APIS = {
    "pos_system": {
        "enabled": False,
        "endpoint": "http://localhost:8080/api",
        "api_key": "your_api_key"
    },
    "accounting_system": {
        "enabled": False,
        "endpoint": "http://localhost:8081/api",
        "api_key": "your_api_key"
    }
}

# ===== FUNZIONI UTILITY =====

def ensure_directories():
    """Crea le directory necessarie se non esistono"""
    directories = [DATA_DIR, LOGS_DIR, BACKUPS_DIR, UPLOADS_DIR, EXPORTS_DIR]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_database_path():
    """Restituisce il percorso del database"""
    return str(DATABASE_PATH)

def get_static_path():
    """Restituisce il percorso della cartella static"""
    return str(STATIC_DIR)

def get_upload_path():
    """Restituisce il percorso della cartella uploads"""
    return str(UPLOADS_DIR)

def get_export_path():
    """Restituisce il percorso della cartella exports"""
    return str(EXPORTS_DIR)

# ===== INIZIALIZZAZIONE =====

# Crea le directory necessarie
ensure_directories()

# Configurazione ambiente
if os.getenv("ENVIRONMENT") == "production":
    # Configurazioni per produzione
    STREAMLIT_CONFIG["server"]["headless"] = True
    LOGGING_CONFIG["level"] = "WARNING"
else:
    # Configurazioni per sviluppo
    STREAMLIT_CONFIG["server"]["headless"] = False
    LOGGING_CONFIG["level"] = "DEBUG"

print(f"✅ Configurazione {APP_NAME} v{APP_VERSION} caricata correttamente")
print(f"📁 Directory base: {BASE_DIR}")
print(f"🗄️ Database: {DATABASE_PATH}")
print(f"📊 Ruoli utente: {len(USER_ROLES)} configurati")
print(f"🏷️ Categorie prodotti: {len(PRODUCT_CATEGORIES)} configurate")

