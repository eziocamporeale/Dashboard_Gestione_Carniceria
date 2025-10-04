#!/usr/bin/env python3
"""
Script per creare la tabella employees nel database Supabase
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

def create_employees_table():
    """Testa se la tabella employees esiste, se no mostra come crearla"""
    
    # Ottieni il database manager
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            print("📡 Connesso a Supabase")
            
            # Prova a inserire un record di test
            test_employee = {
                'name': 'Test Employee',
                'email': 'test@example.com',
                'phone': '+54 11 0000-0000',
                'position': 'Test Position',
                'department': 'Test Department',
                'salary': 1000.00,
                'hire_date': '2024-01-01',
                'status': 'Activo'
            }
            
            print("🧪 Testando inserimento record di test...")
            result = db.add_employee(test_employee)
            
            if result:
                print("✅ Tabella employees esiste e funziona!")
                
                # Elimina il record di test
                print("🗑️ Eliminando record di test...")
                db.supabase_manager.client.table('employees').delete().eq('email', 'test@example.com').execute()
                print("✅ Record di test eliminato")
                
                return True
            else:
                print("❌ Errore durante l'inserimento - la tabella potrebbe non esistere")
                return False
        else:
            print("❌ Connessione Supabase non disponibile")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        print("\n📋 ISTRUZIONI PER CREARE LA TABELLA:")
        print("1. Vai al dashboard di Supabase")
        print("2. Apri la sezione 'Table Editor'")
        print("3. Clicca su 'Create a new table'")
        print("4. Nome tabella: 'employees'")
        print("5. Usa lo script SQL in create_employees_table.sql")
        return False

def test_employees_table():
    """Testa se la tabella employees esiste e funziona"""
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            # Testa se la tabella esiste
            response = db.supabase_manager.client.table('employees').select('*').limit(1).execute()
            print(f"✅ Tabella employees accessibile: {len(response.data)} record trovati")
            
            # Mostra la struttura della tabella
            if response.data:
                print("📋 Struttura della tabella:")
                for key in response.data[0].keys():
                    print(f"  - {key}")
            else:
                print("📋 Tabella vuota ma accessibile")
                
            return True
        else:
            print("❌ Connessione Supabase non disponibile")
            return False
            
    except Exception as e:
        print(f"❌ Errore test tabella: {e}")
        return False

if __name__ == "__main__":
    print("🔧 CREAZIONE TABELLA EMPLOYEES")
    print("=" * 40)
    
    # Crea la tabella
    success = create_employees_table()
    
    if success:
        print("\n🧪 TEST TABELLA EMPLOYEES")
        print("=" * 30)
        test_employees_table()
    else:
        print("❌ Creazione tabella fallita")
        sys.exit(1)
    
    print("\n🎯 Operazione completata!")
