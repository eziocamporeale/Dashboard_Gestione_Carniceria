#!/usr/bin/env python3
"""
Script per creare la tabella activity_log in Supabase
"""

import os
import sys
from pathlib import Path

# Aggiungi il percorso della directory radice del progetto al Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.supabase_manager import SupabaseManager

def create_activity_log_table():
    """Crea la tabella activity_log in Supabase"""
    print("🚀 CREANDO TABELLA activity_log IN SUPABASE")
    print("=" * 50)
    
    # Inizializza SupabaseManager
    db = SupabaseManager()
    
    if not db.is_connected():
        print("❌ ERRORE: Connessione Supabase non disponibile")
        return False
    
    print("✅ Connessione Supabase attiva")
    
    # SQL per creare la tabella activity_log
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS activity_log (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID REFERENCES users(id) ON DELETE SET NULL,
        activity_type VARCHAR(100) NOT NULL,
        description TEXT,
        ip_address VARCHAR(45),
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    
    try:
        # Esegui la query SQL
        result = db.client.rpc('exec_sql', {'sql': create_table_sql}).execute()
        print("✅ Tabella activity_log creata con successo")
        return True
        
    except Exception as e:
        print(f"❌ Errore creando tabella activity_log: {e}")
        
        # Prova con un approccio alternativo
        try:
            # Inserisci un record di test per creare la tabella
            test_data = {
                'user_id': None,
                'activity_type': 'system_init',
                'description': 'Tabella activity_log creata automaticamente',
                'ip_address': None
            }
            
            result = db.insert('activity_log', test_data)
            if result:
                print("✅ Tabella activity_log creata tramite inserimento test")
                return True
            else:
                print("❌ Fallito anche l'inserimento test")
                return False
                
        except Exception as e2:
            print(f"❌ Errore anche con approccio alternativo: {e2}")
            return False

def test_activity_log():
    """Testa la tabella activity_log"""
    print("\n🧪 TESTANDO TABELLA activity_log")
    print("=" * 30)
    
    db = SupabaseManager()
    
    if not db.is_connected():
        print("❌ Connessione Supabase non disponibile")
        return False
    
    try:
        # Prova a inserire un record di test
        test_data = {
            'user_id': None,
            'activity_type': 'test',
            'description': 'Test tabella activity_log',
            'ip_address': '127.0.0.1'
        }
        
        result = db.insert('activity_log', test_data)
        if result:
            print("✅ Inserimento test riuscito")
            
            # Prova a recuperare i dati
            logs = db.select('activity_log', limit=5)
            print(f"✅ Recupero dati riuscito: {len(logs)} record trovati")
            return True
        else:
            print("❌ Inserimento test fallito")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante test: {e}")
        return False

if __name__ == "__main__":
    print("🔧 SCRIPT CREAZIONE TABELLA activity_log")
    print("=" * 50)
    
    # Assicurati che le variabili d'ambiente siano impostate
    os.environ["SUPABASE_URL"] = "https://xaxzwfuedzwhsshottum.supabase.co"
    os.environ["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhheHp3ZnVlZHp3aHNzaG90dHVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkzODQ0MDgsImV4cCI6MjA3NDk2MDQwOH0.VcPt8PSe-x_BGQquCXfKsh2HAwxOgs9mQBj7OWdB95k"
    
    # Crea la tabella
    success = create_activity_log_table()
    
    if success:
        # Testa la tabella
        test_success = test_activity_log()
        
        if test_success:
            print("\n🎉 TABELLA activity_log CREATA E TESTATA CON SUCCESSO!")
            print("✅ Il sistema ora può loggare le attività correttamente")
        else:
            print("\n⚠️ Tabella creata ma test fallito")
    else:
        print("\n❌ FALLIMENTO: Impossibile creare la tabella activity_log")
        print("💡 Prova a creare manualmente la tabella su Supabase Dashboard")
    
    print("\n" + "=" * 50)
