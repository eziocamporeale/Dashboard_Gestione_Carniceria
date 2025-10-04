#!/usr/bin/env python3
"""
Script per verificare la struttura esatta della tabella employees
Creado por Ezio Camporeale
"""

import os
import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

try:
    from database.hybrid_database_manager import get_hybrid_manager
    print("✅ Importato HybridDatabaseManager")
except ImportError as e:
    print(f"❌ Errore import HybridDatabaseManager: {e}")
    sys.exit(1)

def check_table_structure_detailed():
    """Verifica la struttura dettagliata della tabella employees"""
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            print("📡 Connesso a Supabase")
            
            # Prova a selezionare con colonne specifiche per vedere quali esistono
            test_columns = [
                'id', 'name', 'email', 'phone', 'address', 'position', 
                'department', 'salary', 'hire_date', 'status', 
                'contract_type', 'emergency_contact', 'emergency_phone', 
                'notes', 'created_at', 'updated_at'
            ]
            
            print("🧪 Testando colonne specifiche...")
            
            existing_columns = []
            missing_columns = []
            
            for column in test_columns:
                try:
                    # Prova a selezionare solo questa colonna
                    response = db.supabase_manager.client.table('employees').select(column).limit(1).execute()
                    existing_columns.append(column)
                    print(f"  ✅ {column} - ESISTE")
                except Exception as e:
                    missing_columns.append(column)
                    print(f"  ❌ {column} - MANCA")
            
            print(f"\n📊 RISULTATO:")
            print(f"  ✅ Colonne esistenti: {len(existing_columns)}")
            print(f"  ❌ Colonne mancanti: {len(missing_columns)}")
            
            if missing_columns:
                print(f"\n📋 COLONNE MANCANTI:")
                for col in missing_columns:
                    print(f"  - {col}")
                    
                print(f"\n🔧 SCRIPT SQL PER AGGIUNGERE COLONNE MANCANTI:")
                for col in missing_columns:
                    if col == 'address':
                        print(f"ALTER TABLE employees ADD COLUMN IF NOT EXISTS {col} TEXT;")
                    elif col == 'contract_type':
                        print(f"ALTER TABLE employees ADD COLUMN IF NOT EXISTS {col} VARCHAR(100) DEFAULT 'Tiempo Completo';")
                    elif col == 'emergency_contact':
                        print(f"ALTER TABLE employees ADD COLUMN IF NOT EXISTS {col} TEXT;")
                    elif col == 'emergency_phone':
                        print(f"ALTER TABLE employees ADD COLUMN IF NOT EXISTS {col} VARCHAR(50);")
                    elif col == 'notes':
                        print(f"ALTER TABLE employees ADD COLUMN IF NOT EXISTS {col} TEXT;")
                    elif col == 'created_at':
                        print(f"ALTER TABLE employees ADD COLUMN IF NOT EXISTS {col} TIMESTAMP WITH TIME ZONE DEFAULT NOW();")
                    elif col == 'updated_at':
                        print(f"ALTER TABLE employees ADD COLUMN IF NOT EXISTS {col} TIMESTAMP WITH TIME ZONE DEFAULT NOW();")
            
            return len(missing_columns) == 0
            
        else:
            print("❌ Connessione Supabase non disponibile")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante il controllo: {e}")
        return False

def test_simple_insert():
    """Testa un inserimento semplice con solo le colonne base"""
    
    db = get_hybrid_manager()
    
    # Test con solo le colonne essenziali
    simple_employee = {
        'name': 'Test Simple',
        'email': 'test.simple@example.com',
        'phone': '+54 11 0000-0000',
        'position': 'Test Position',
        'department': 'Test Department',
        'salary': 1000.00,
        'hire_date': '2024-01-01',
        'status': 'Activo'
    }
    
    try:
        print("\n🧪 Testando inserimento con colonne base...")
        result = db.add_employee(simple_employee)
        
        if result:
            print("✅ Inserimento base riuscito!")
            
            # Elimina il record di test
            print("🗑️ Eliminando record di test...")
            db.supabase_manager.client.table('employees').delete().eq('email', 'test.simple@example.com').execute()
            print("✅ Record di test eliminato")
            
            return True
        else:
            print("❌ Inserimento base fallito")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante il test semplice: {e}")
        return False

if __name__ == "__main__":
    print("🔍 VERIFICA STRUTTURA TABELLA EMPLOYEES")
    print("=" * 50)
    
    # Controlla la struttura dettagliata
    print("\n1️⃣ CONTROLLO STRUTTURA DETTAGLIATA")
    print("-" * 35)
    structure_ok = check_table_structure_detailed()
    
    # Testa inserimento semplice
    print("\n2️⃣ TEST INSERIMENTO SEMPLICE")
    print("-" * 30)
    simple_ok = test_simple_insert()
    
    if structure_ok and simple_ok:
        print("\n✅ TUTTO FUNZIONA PERFETTAMENTE!")
        print("La tabella employees è completa e funzionale.")
    elif simple_ok:
        print("\n⚠️ INSERIMENTO BASE FUNZIONA")
        print("Alcune colonne aggiuntive mancano ma le funzionalità base sono OK.")
    else:
        print("\n❌ PROBLEMI RILEVATI")
        print("La tabella ha problemi strutturali che impediscono l'inserimento.")
    
    print("\n🎯 Verifica completata!")
