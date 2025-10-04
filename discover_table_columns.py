#!/usr/bin/env python3
"""
Script per scoprire tutte le colonne esistenti nella tabella employees
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

def discover_all_columns():
    """Scopre tutte le colonne esistenti nella tabella"""
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            print("📡 Connesso a Supabase")
            
            # Prova a inserire un record vuoto per vedere l'errore completo
            try:
                empty_record = {}
                response = db.supabase_manager.client.table('employees').insert(empty_record).execute()
                print("✅ Inserimento vuoto riuscito (inaspettato)")
            except Exception as e:
                print(f"🔍 Errore inserimento vuoto: {e}")
                
                # Analizza l'errore per capire le colonne richieste
                error_str = str(e)
                if 'first_name' in error_str:
                    print("❌ La tabella richiede una colonna 'first_name'")
                if 'last_name' in error_str:
                    print("❌ La tabella richiede una colonna 'last_name'")
                if 'name' in error_str:
                    print("❌ La tabella richiede una colonna 'name'")
            
            # Prova a selezionare con select(*) per vedere tutte le colonne
            try:
                response = db.supabase_manager.client.table('employees').select('*').limit(1).execute()
                if response.data:
                    print(f"\n📋 COLONNE DISPONIBILI NEI DATI:")
                    for key in response.data[0].keys():
                        print(f"  - {key}")
                else:
                    print("📋 Tabella vuota - proviamo con un inserimento di test...")
                    
                    # Prova a inserire un record con tutti i campi che conosciamo
                    test_record = {
                        'name': 'Test Name',
                        'first_name': 'Test',
                        'last_name': 'User',
                        'email': 'test.discover@example.com',
                        'phone': '+54 11 0000-0000',
                        'address': 'Test Address',
                        'position': 'Test Position',
                        'department': 'Test Department',
                        'salary': 1000.00,
                        'hire_date': '2024-01-01',
                        'status': 'Activo',
                        'contract_type': 'Tiempo Completo',
                        'emergency_contact': 'Emergency Contact',
                        'emergency_phone': '+54 11 9999-9999',
                        'notes': 'Test notes'
                    }
                    
                    try:
                        response = db.supabase_manager.client.table('employees').insert(test_record).execute()
                        print("✅ Record di test inserito con successo!")
                        
                        # Elimina il record di test
                        db.supabase_manager.client.table('employees').delete().eq('email', 'test.discover@example.com').execute()
                        print("✅ Record di test eliminato")
                        
                        return True
                        
                    except Exception as e:
                        print(f"❌ Errore inserimento test: {e}")
                        return False
                        
            except Exception as e:
                print(f"❌ Errore selezione: {e}")
                return False
                
        else:
            print("❌ Connessione Supabase non disponibile")
            return False
            
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        return False

if __name__ == "__main__":
    print("🔍 SCOPERTA COLONNE TABELLA EMPLOYEES")
    print("=" * 45)
    
    success = discover_all_columns()
    
    if success:
        print("\n✅ SCOPERTA COMPLETATA!")
        print("Ora sappiamo esattamente quali colonne esistono.")
    else:
        print("\n❌ PROBLEMA NELLA SCOPERTA")
        print("La tabella potrebbe avere una struttura diversa da quella attesa.")
    
    print("\n🎯 Scoperta completata!")
