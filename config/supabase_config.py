#!/usr/bin/env python3
"""
Configurazione Supabase per Dashboard Gestión Carnicería
Gestione sicura delle credenziali e configurazione database
Creato da Ezio Camporeale
"""

import os
from pathlib import Path
from typing import Optional

class SupabaseConfig:
    """Configurazione Supabase per sicurezza e deployment"""
    
    # URL e API Key Supabase (da variabili ambiente per sicurezza)
    SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://xaxzwfuedzwhsshottum.supabase.co')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhheHp3ZnVlZHp3aHNzaG90dHVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkzODQ0MDgsImV4cCI6MjA3NDk2MDQwOH0.VcPt8PSe-x_BGQquCXfKsh2HAwxOgs9mQBj7OWdB95k')
    
    # Configurazione database
    USE_SUPABASE = os.getenv('USE_SUPABASE', 'true').lower() == 'true'
    FALLBACK_TO_SQLITE = os.getenv('FALLBACK_TO_SQLITE', 'true').lower() == 'true'
    
    # Configurazione sicurezza
    ROW_LEVEL_SECURITY = True
    ENCRYPTION_ENABLED = True
    SSL_REQUIRED = True
    
    # Configurazione autenticazione
    AUTH_COOKIE_NAME = 'carniceria_auth'
    AUTH_COOKIE_EXPIRY_DAYS = 30
    SESSION_TIMEOUT_MINUTES = 60
    
    # Configurazione app
    APP_NAME = 'Dashboard Gestión Carnicería'
    APP_VERSION = '2.0.0'
    APP_ENVIRONMENT = os.getenv('APP_ENVIRONMENT', 'development')
    
    @classmethod
    def is_supabase_configured(cls) -> bool:
        """Verifica se Supabase è configurato correttamente"""
        return bool(cls.SUPABASE_URL and cls.SUPABASE_ANON_KEY)
    
    @classmethod
    def get_database_url(cls) -> str:
        """Ottiene URL database per connessione"""
        return cls.SUPABASE_URL
    
    @classmethod
    def get_api_key(cls) -> str:
        """Ottiene API key per autenticazione"""
        return cls.SUPABASE_ANON_KEY
    
    @classmethod
    def is_production(cls) -> bool:
        """Verifica se siamo in ambiente di produzione"""
        return cls.APP_ENVIRONMENT.lower() == 'production'
    
    @classmethod
    def get_connection_config(cls) -> dict:
        """Ottiene configurazione connessione Supabase"""
        return {
            'url': cls.SUPABASE_URL,
            'key': cls.SUPABASE_ANON_KEY,
            'options': {
                'schema': 'public',
                'auto_refresh_token': True,
                'persist_session': True,
                'detect_session_in_url': True
            }
        }

def get_supabase_setup_instructions():
    """Istruzioni per configurazione Supabase"""
    return """
    🚀 CONFIGURAZIONE SUPABASE - Dashboard Gestión Carnicería
    
    📋 STEP 1: Variabili Ambiente
    Crea file .env nella root del progetto:
    
    SUPABASE_URL=https://xaxzwfuedzwhsshottum.supabase.co
    SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhheHp3ZnVlZHp3aHNzaG90dHVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkzODQ0MDgsImV4cCI6MjA3NDk2MDQwOH0.VcPt8PSe-x_BGQquCXfKsh2HAwxOgs9mQBj7OWdB95k
    USE_SUPABASE=true
    APP_ENVIRONMENT=production
    
    📋 STEP 2: Installazione Dipendenze
    pip install -r requirements_supabase.txt
    
    📋 STEP 3: Test Connessione
    python test_supabase_connection.py
    
    ⚠️ SICUREZZA: Non committare mai le API keys nel codice!
    """

# Configurazione per Streamlit Cloud
STREAMLIT_CLOUD_CONFIG = {
    'SUPABASE_URL': 'https://xaxzwfuedzwhsshottum.supabase.co',
    'SUPABASE_ANON_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhheHp3ZnVlZHp3aHNzaG90dHVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkzODQ0MDgsImV4cCI6MjA3NDk2MDQwOH0.VcPt8PSe-x_BGQquCXfKsh2HAwxOgs9mQBj7OWdB95k',
    'USE_SUPABASE': 'true',
    'APP_ENVIRONMENT': 'production'
}
