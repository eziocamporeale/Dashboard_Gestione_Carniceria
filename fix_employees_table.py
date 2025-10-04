#!/usr/bin/env python3
"""
Script per correggere la tabella employees aggiungendo colonne mancanti
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

def check_table_structure():
    """Verifica la struttura della tabella employees"""
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            print("📡 Connesso a Supabase")
            
            # Prova a selezionare dalla tabella per vedere quali colonne esistono
            try:
                response = db.supabase_manager.client.table('employees').select('*').limit(1).execute()
                print("✅ Tabella employees accessibile")
                
                if response.data:
                    print("📋 Colonne esistenti:")
                    for key in response.data[0].keys():
                        print(f"  ✅ {key}")
                else:
                    print("📋 Tabella vuota ma accessibile")
                    
                return True
                
            except Exception as e:
                print(f"❌ Errore accesso tabella: {e}")
                return False
        else:
            print("❌ Connessione Supabase non disponibile")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante il controllo: {e}")
        return False

def test_employee_creation():
    """Testa la creazione di un impiegato con tutte le colonne"""
    
    db = get_hybrid_manager()
    
    # Dati di test con tutte le colonne
    test_employee = {
        'name': 'Test Employee Fix',
        'email': 'test.fix@example.com',
        'phone': '+54 11 0000-0000',
        'address': 'Test Address 123',  # Questa colonna potrebbe mancare
        'position': 'Test Position',
        'department': 'Test Department',
        'salary': 1000.00,
        'hire_date': '2024-01-01',
        'status': 'Activo',
        'contract_type': 'Tiempo Completo',  # Questa colonna potrebbe mancare
        'emergency_contact': 'Emergency Contact',  # Questa colonna potrebbe mancare
        'emergency_phone': '+54 11 9999-9999',  # Questa colonna potrebbe mancare
        'notes': 'Test notes',  # Questa colonna potrebbe mancare
    }
    
    try:
        print("🧪 Testando creazione impiegato con tutte le colonne...")
        result = db.add_employee(test_employee)
        
        if result:
            print("✅ Impiegato di test creato con successo!")
            
            # Elimina il record di test
            print("🗑️ Eliminando record di test...")
            db.supabase_manager.client.table('employees').delete().eq('email', 'test.fix@example.com').execute()
            print("✅ Record di test eliminato")
            
            return True
        else:
            print("❌ Errore durante la creazione - alcune colonne potrebbero mancare")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        return False

def show_fix_instructions():
    """Mostra le istruzioni per correggere la tabella"""
    
    print("\n📋 ISTRUZIONI PER CORREGGERE LA TABELLA EMPLOYEES")
    print("=" * 60)
    print("1. Vai al dashboard di Supabase")
    print("2. Apri la sezione 'SQL Editor'")
    print("3. Incolla e esegui lo script da add_missing_columns.sql")
    print("4. Oppure aggiungi manualmente le colonne mancanti:")
    print()
    print("   ALTER TABLE employees ADD COLUMN IF NOT EXISTS address TEXT;")
    print("   ALTER TABLE employees ADD COLUMN IF NOT EXISTS contract_type VARCHAR(100) DEFAULT 'Tiempo Completo';")
    print("   ALTER TABLE employees ADD COLUMN IF NOT EXISTS emergency_contact TEXT;")
    print("   ALTER TABLE employees ADD COLUMN IF NOT EXISTS emergency_phone VARCHAR(50);")
    print("   ALTER TABLE employees ADD COLUMN IF NOT EXISTS notes TEXT;")
    print("   ALTER TABLE employees ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();")
    print("   ALTER TABLE employees ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();")
    print()
    print("5. Dopo aver aggiunto le colonne, esegui di nuovo questo script per testare")

if __name__ == "__main__":
    print("🔧 CORREZIONE TABELLA EMPLOYEES")
    print("=" * 40)
    
    # Controlla la struttura della tabella
    print("\n1️⃣ CONTROLLO STRUTTURA TABELLA")
    print("-" * 30)
    structure_ok = check_table_structure()
    
    # Testa la creazione di un impiegato
    print("\n2️⃣ TEST CREAZIONE IMPIEGATO")
    print("-" * 30)
    creation_ok = test_employee_creation()
    
    if not creation_ok:
        print("\n❌ PROBLEMA RILEVATO")
        print("-" * 20)
        show_fix_instructions()
    else:
        print("\n✅ TUTTO FUNZIONA CORRETTAMENTE!")
        print("La tabella employees è pronta per l'uso.")
    
    print("\n🎯 Operazione completata!")
