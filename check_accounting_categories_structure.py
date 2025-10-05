#!/usr/bin/env python3
"""
Script per verificare la struttura della tabella accounting_categories
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

def check_accounting_categories_structure():
    """Verifica la struttura della tabella accounting_categories"""
    
    print("🔍 VERIFICANDO STRUTTURA TABELLA ACCOUNTING_CATEGORIES...")
    print("=" * 60)
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            print("📡 Connesso a Supabase")
            
            # Prova a recuperare un record per vedere la struttura
            response = db.supabase_manager.client.table('accounting_categories').select('*').limit(1).execute()
            
            if response.data:
                print("📋 Struttura tabella accounting_categories:")
                columns_found = []
                for key, value in response.data[0].items():
                    print(f"  - {key}: {type(value).__name__} = {value}")
                    columns_found.append(key)
                
                return columns_found
            else:
                print("⚠️  Tabella vuota - provo a inserire un record di test")
                
                # Prova a inserire un record di test per vedere la struttura
                test_data = {
                    'name': 'Test Category',
                    'type': 'income',
                    'is_active': True
                }
                
                try:
                    response = db.supabase_manager.client.table('accounting_categories').insert(test_data).execute()
                    print("✅ Record di test inserito con successo")
                    
                    # Ora recupera il record per vedere la struttura
                    response = db.supabase_manager.client.table('accounting_categories').select('*').limit(1).execute()
                    if response.data:
                        print("📋 Struttura tabella accounting_categories (dal record di test):")
                        columns_found = []
                        for key, value in response.data[0].items():
                            print(f"  - {key}: {type(value).__name__} = {value}")
                            columns_found.append(key)
                        return columns_found
                except Exception as e:
                    print(f"❌ Errore inserendo record di test: {e}")
                    return []
                
        else:
            print("❌ Connessione Supabase non disponibile")
            return []
            
    except Exception as e:
        print(f"❌ Errore verificando struttura: {e}")
        return []

if __name__ == "__main__":
    print("🔍 VERIFICA STRUTTURA ACCOUNTING_CATEGORIES")
    print("=" * 45)
    
    columns = check_accounting_categories_structure()
    
    if columns:
        print(f"\n✅ Colonne trovate: {columns}")
        
        # Verifica colonne essenziali
        required_columns = ['name', 'type', 'is_active']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            print(f"❌ Colonne mancanti: {missing_columns}")
        else:
            print("✅ Tutte le colonne essenziali presenti")
    else:
        print("❌ Impossibile determinare la struttura della tabella")
    
    print("\n🎯 Verifica completata!")

