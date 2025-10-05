#!/usr/bin/env python3
"""
Script per verificare la struttura della tabella suppliers
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

def check_suppliers_table_structure():
    """Verifica la struttura della tabella suppliers"""
    
    print("🔍 VERIFICANDO STRUTTURA TABELLA SUPPLIERS...")
    print("=" * 50)
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            print("📡 Connesso a Supabase")
            
            # Prova a recuperare un fornitore con tutti i campi
            try:
                response = db.supabase_manager.client.table('suppliers').select('*').limit(1).execute()
                print("✅ Tabella 'suppliers' accessibile")
                
                if response.data:
                    print("📋 Struttura tabella suppliers:")
                    for key, value in response.data[0].items():
                        print(f"  - {key}: {type(value).__name__}")
                else:
                    print("⚠️  Tabella vuota - proviamo a inserire un record di test")
                    
                    # Prova a inserire un record minimo
                    test_data = {
                        'name': 'Test Supplier',
                        'contact_email': 'test@example.com',
                        'is_active': True
                    }
                    
                    insert_response = db.supabase_manager.client.table('suppliers').insert(test_data).execute()
                    
                    if insert_response.data:
                        print("✅ Record di test inserito con successo")
                        
                        # Recupera il record inserito per vedere la struttura
                        response = db.supabase_manager.client.table('suppliers').select('*').limit(1).execute()
                        if response.data:
                            print("📋 Struttura tabella suppliers (da record inserito):")
                            for key, value in response.data[0].items():
                                print(f"  - {key}: {type(value).__name__}")
                        
                        # Pulisci il record di test
                        db.supabase_manager.client.table('suppliers').delete().eq('name', 'Test Supplier').execute()
                        print("🧹 Record di test rimosso")
                    else:
                        print("❌ Errore inserendo record di test")
                        
            except Exception as e:
                print(f"❌ Errore durante il controllo: {e}")
                
                # Se l'errore è specifico, proviamo a capire quale colonna manca
                error_str = str(e)
                if "Could not find the" in error_str and "column" in error_str:
                    # Estrai il nome della colonna mancante
                    import re
                    match = re.search(r"'([^']+)' column", error_str)
                    if match:
                        missing_column = match.group(1)
                        print(f"⚠️  Colonna mancante identificata: '{missing_column}'")
                        print("🔧 SOLUZIONE: Aggiungere la colonna alla tabella suppliers")
                
                return False
                
        else:
            print("❌ Connessione Supabase non disponibile")
            return False
            
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        return False

def create_suppliers_table_fix():
    """Crea uno script SQL per correggere la tabella suppliers"""
    
    print("\n🔧 CREANDO SCRIPT DI CORREZIONE...")
    print("=" * 40)
    
    # Crea uno script SQL per aggiungere le colonne mancanti
    sql_fix = """
-- Script per correggere la tabella suppliers
-- Esegui questo script in Supabase SQL Editor

-- Aggiungi colonne mancanti alla tabella suppliers
ALTER TABLE suppliers 
ADD COLUMN IF NOT EXISTS notes TEXT;

ALTER TABLE suppliers 
ADD COLUMN IF NOT EXISTS phone VARCHAR(50);

ALTER TABLE suppliers 
ADD COLUMN IF NOT EXISTS address TEXT;

ALTER TABLE suppliers 
ADD COLUMN IF NOT EXISTS contact_person VARCHAR(255);

-- Verifica la struttura finale
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'suppliers' 
ORDER BY ordinal_position;
"""
    
    fix_file = current_dir / "fix_suppliers_table.sql"
    try:
        with open(fix_file, 'w', encoding='utf-8') as f:
            f.write(sql_fix)
        print(f"✅ Script di correzione creato: {fix_file}")
        print("📝 Istruzioni:")
        print("   1. Apri Supabase Dashboard")
        print("   2. Vai su SQL Editor")
        print("   3. Esegui il contenuto di fix_suppliers_table.sql")
        print("   4. Riavvia la dashboard")
        return True
    except Exception as e:
        print(f"❌ Errore creando script: {e}")
        return False

if __name__ == "__main__":
    print("🔍 VERIFICA STRUTTURA TABELLA SUPPLIERS")
    print("=" * 45)
    
    # 1. Verifica struttura
    structure_ok = check_suppliers_table_structure()
    
    # 2. Crea script di correzione
    if not structure_ok:
        script_created = create_suppliers_table_fix()
        
        print("\n🎯 DIAGNOSI FINALE")
        print("=" * 20)
        print("❌ PROBLEMA: Struttura tabella suppliers incompleta")
        print("🔧 SOLUZIONE: Eseguire fix_suppliers_table.sql in Supabase")
        if script_created:
            print("✅ Script di correzione creato")
    else:
        print("\n✅ Struttura tabella suppliers OK")
    
    print("\n🎯 Verifica completata!")
