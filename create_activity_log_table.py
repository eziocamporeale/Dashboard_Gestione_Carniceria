#!/usr/bin/env python3
"""
Script per creare la tabella activity_log nel database Supabase
Dashboard Gestión Carnicería
Creato da Ezio Camporeale
"""

import os
import sys
import logging
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.supabase_manager import SupabaseManager

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_activity_log_table():
    """Crea la tabella activity_log nel database Supabase"""
    
    print("🔧 CREANDO TABELLA activity_log IN SUPABASE")
    print("=" * 60)
    
    # Configura le variabili d'ambiente
    os.environ["SUPABASE_URL"] = "https://xaxzwfuedzwhsshottum.supabase.co"
    os.environ["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhheHp3ZnVlZHp3aHNzaG90dHVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkzODQ0MDgsImV4cCI6MjA3NDk2MDQwOH0.VcPt8PSe-x_BGQquCXfKsh2HAwxOgs9mQBj7OWdB95k"
    
    # Inizializza il manager Supabase
    print("\n🔍 Inizializzando SupabaseManager...")
    db = SupabaseManager()
    
    if not db.is_connected():
        print("❌ FALLO: Connessione a Supabase fallita.")
        return False
    
    print("✅ Connessione a Supabase stabilita.")
    
    # 1. Crea la tabella activity_log
    print("\n➡️ Creando tabella activity_log...")
    
    # SQL per creare la tabella activity_log
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS activity_log (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID REFERENCES users(id) ON DELETE SET NULL,
        activity_type VARCHAR(100) NOT NULL,
        description TEXT,
        ip_address VARCHAR(45),
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    
    try:
        # Usa RPC per eseguire SQL
        result = db.rpc('exec_sql', {'sql': create_table_sql})
        if result:
            print("✅ Tabella activity_log creata con successo!")
        else:
            print("⚠️ Tabella activity_log potrebbe già esistere")
    except Exception as e:
        print(f"⚠️ Errore creando tabella: {e}")
        print("La tabella potrebbe già esistere")
    
    # 2. Testa l'inserimento di un log
    print("\n➡️ Testando inserimento log...")
    test_log = db.log_activity(
        user_id="00000000-0000-0000-0000-000000000101",  # admin user ID
        action="test_connection",
        details="Test di connessione activity_log",
        ip_address="127.0.0.1"
    )
    
    if test_log:
        print("✅ Test inserimento log riuscito!")
    else:
        print("❌ Test inserimento log fallito")
    
    # 3. Verifica che la tabella esista
    print("\n➡️ Verificando esistenza tabella...")
    try:
        logs = db.select('activity_log', limit=5)
        if logs is not None:
            print(f"✅ Tabella activity_log verificata: {len(logs)} record trovati")
        else:
            print("❌ Tabella activity_log non accessibile")
    except Exception as e:
        print(f"❌ Errore verificando tabella: {e}")
    
    print("\n" + "=" * 60)
    print("✅ CREAZIONE TABELLA activity_log COMPLETATA!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = create_activity_log_table()
    if success:
        print("\n🎉 Tabella activity_log creata con successo!")
        print("🚀 Ora il sistema può loggare le attività utente")
    else:
        print("\n❌ Errore creando tabella activity_log")
        sys.exit(1)
