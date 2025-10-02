#!/usr/bin/env python3
"""
Script per verificare e creare le tabelle mancanti in Supabase
"""

import os
import sys
from pathlib import Path

# Aggiungi il percorso della directory radice del progetto al Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.supabase_manager import SupabaseManager

def check_table_exists(table_name):
    """Verifica se una tabella esiste in Supabase"""
    try:
        db = SupabaseManager()
        if not db.is_connected():
            print(f"❌ Connessione Supabase non disponibile")
            return False
        
        # Prova a fare una query semplice
        result = db.select(table_name, limit=1)
        print(f"✅ Tabella {table_name} esiste e accessibile")
        return True
        
    except Exception as e:
        print(f"❌ Tabella {table_name} non esiste o non accessibile: {e}")
        return False

def create_missing_tables():
    """Crea le tabelle mancanti in Supabase"""
    print("🔧 CREANDO TABELLE MANCANTI IN SUPABASE")
    print("=" * 50)
    
    # Lista delle tabelle necessarie
    required_tables = [
        'products',
        'customers', 
        'sales',
        'users',
        'roles',
        'activity_log'
    ]
    
    missing_tables = []
    
    # Verifica quali tabelle esistono
    for table in required_tables:
        if not check_table_exists(table):
            missing_tables.append(table)
    
    if not missing_tables:
        print("✅ Tutte le tabelle necessarie esistono!")
        return True
    
    print(f"❌ Tabelle mancanti: {missing_tables}")
    print("\n📋 ISTRUZIONI PER CREARE LE TABELLE MANCANTI:")
    print("=" * 50)
    
    # SQL per creare le tabelle mancanti
    if 'products' in missing_tables:
        print("\n🔧 CREA TABELLA PRODUCTS:")
        print("""
        CREATE TABLE IF NOT EXISTS products (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            category VARCHAR(100),
            current_stock NUMERIC(10, 2) DEFAULT 0.00,
            min_stock_level NUMERIC(10, 2) DEFAULT 0.00,
            expiry_date DATE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """)
    
    if 'customers' in missing_tables:
        print("\n🔧 CREA TABELLA CUSTOMERS:")
        print("""
        CREATE TABLE IF NOT EXISTS customers (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            phone VARCHAR(50),
            address TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """)
    
    if 'sales' in missing_tables:
        print("\n🔧 CREA TABELLA SALES:")
        print("""
        CREATE TABLE IF NOT EXISTS sales (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            customer_id UUID REFERENCES customers(id),
            total_amount NUMERIC(12, 2) NOT NULL,
            sale_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """)
    
    print("\n📝 ISTRUZIONI:")
    print("1. Vai su https://supabase.com")
    print("2. Accedi al tuo progetto")
    print("3. Vai su SQL Editor")
    print("4. Copia e incolla gli script SQL sopra")
    print("5. Esegui le query")
    print("6. Verifica che le tabelle siano state create")
    
    return False

def test_all_tables():
    """Testa tutte le tabelle"""
    print("\n🧪 TESTANDO TUTTE LE TABELLE")
    print("=" * 30)
    
    tables = ['products', 'customers', 'sales', 'users', 'roles', 'activity_log']
    
    for table in tables:
        print(f"\n🔍 Testando tabella: {table}")
        if check_table_exists(table):
            # Prova a inserire un record di test
            try:
                db = SupabaseManager()
                test_data = {
                    'name': f'Test {table}',
                    'description': f'Record di test per {table}'
                }
                
                # Rimuovi campi non validi per alcune tabelle
                if table == 'users':
                    test_data = {
                        'email': 'test@example.com',
                        'first_name': 'Test',
                        'last_name': 'User'
                    }
                elif table == 'roles':
                    test_data = {
                        'name': 'test_role',
                        'description': 'Test role'
                    }
                elif table == 'activity_log':
                    test_data = {
                        'activity_type': 'test',
                        'description': 'Test activity'
                    }
                
                result = db.insert(table, test_data)
                if result:
                    print(f"✅ Inserimento test riuscito per {table}")
                else:
                    print(f"⚠️ Inserimento test fallito per {table}")
                    
            except Exception as e:
                print(f"⚠️ Errore durante test inserimento per {table}: {e}")
        else:
            print(f"❌ Tabella {table} non accessibile")

if __name__ == "__main__":
    print("🔍 VERIFICA TABELLE SUPABASE")
    print("=" * 50)
    
    # Assicurati che le variabili d'ambiente siano impostate
    os.environ["SUPABASE_URL"] = "https://xaxzwfuedzwhsshottum.supabase.co"
    os.environ["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhheHp3ZnVlZHp3aHNzaG90dHVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkzODQ0MDgsImV4cCI6MjA3NDk2MDQwOH0.VcPt8PSe-x_BGQquCXfKsh2HAwxOgs9mQBj7OWdB95k"
    
    # Verifica e crea tabelle mancanti
    success = create_missing_tables()
    
    if success:
        # Testa tutte le tabelle
        test_all_tables()
        print("\n🎉 TUTTE LE TABELLE SONO OPERATIVE!")
    else:
        print("\n⚠️ Alcune tabelle mancano - segui le istruzioni sopra")
    
    print("\n" + "=" * 50)
