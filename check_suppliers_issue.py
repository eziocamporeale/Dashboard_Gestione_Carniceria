#!/usr/bin/env python3
"""
Script per verificare il problema con i fornitori
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

def check_suppliers_in_database():
    """Verifica i fornitori nel database"""
    
    print("🔍 VERIFICANDO FORNITORI NEL DATABASE...")
    print("=" * 45)
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            print("📡 Connesso a Supabase")
            
            # Prova a recuperare tutti i fornitori
            try:
                response = db.supabase_manager.client.table('suppliers').select('*').execute()
                
                if response.data:
                    print(f"✅ Trovati {len(response.data)} fornitori nel database:")
                    print("-" * 60)
                    
                    for i, supplier in enumerate(response.data, 1):
                        print(f"{i}. ID: {supplier.get('id', 'N/A')}")
                        print(f"   Nome: {supplier.get('name', 'N/A')}")
                        print(f"   Email: {supplier.get('contact_email', 'N/A')}")
                        print(f"   Telefono: {supplier.get('phone', 'N/A')}")
                        print(f"   Indirizzo: {supplier.get('address', 'N/A')}")
                        print(f"   Contatto: {supplier.get('contact_person', 'N/A')}")
                        print(f"   Attivo: {supplier.get('is_active', 'N/A')}")
                        print(f"   Creato: {supplier.get('created_at', 'N/A')}")
                        print("-" * 40)
                    
                    # Cerca specificamente "Toledo Import SL"
                    toledo_found = any('Toledo Import' in str(supplier.get('name', '')) for supplier in response.data)
                    if toledo_found:
                        print("✅ 'Toledo Import SL' trovato nel database!")
                    else:
                        print("❌ 'Toledo Import SL' NON trovato nel database")
                    
                    return True
                else:
                    print("❌ Nessun fornitore trovato nel database")
                    return False
                    
            except Exception as e:
                print(f"❌ Errore durante il recupero fornitori: {e}")
                return False
                
        else:
            print("❌ Connessione Supabase non disponibile")
            return False
            
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        return False

def check_suppliers_table_structure():
    """Verifica la struttura della tabella suppliers"""
    
    print("\n🗄️ VERIFICANDO STRUTTURA TABELLA SUPPLIERS...")
    print("=" * 50)
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            # Prova a fare una query di test
            try:
                response = db.supabase_manager.client.table('suppliers').select('id').limit(1).execute()
                print("✅ Tabella 'suppliers' esiste e accessibile")
                return True
            except Exception as e:
                print(f"❌ Tabella 'suppliers' non accessibile: {e}")
                return False
        else:
            print("❌ Connessione Supabase non disponibile")
            return False
            
    except Exception as e:
        print(f"❌ Errore verificando struttura: {e}")
        return False

def check_suppliers_methods():
    """Verifica i metodi per i fornitori nel database manager"""
    
    print("\n🔧 VERIFICANDO METODI FORNITORI NEL DATABASE MANAGER...")
    print("=" * 55)
    
    db = get_hybrid_manager()
    
    # Verifica metodi disponibili
    methods_to_check = [
        'get_suppliers',
        'select',
        'add_supplier',
        'create_supplier'
    ]
    
    for method_name in methods_to_check:
        if hasattr(db, method_name):
            print(f"✅ Metodo '{method_name}' disponibile")
        else:
            print(f"❌ Metodo '{method_name}' NON disponibile")
    
    # Test del metodo select
    try:
        suppliers = db.select('suppliers')
        if suppliers is not None:
            print(f"✅ db.select('suppliers') funziona - Trovati {len(suppliers)} fornitori")
        else:
            print("⚠️  db.select('suppliers') restituisce None")
    except Exception as e:
        print(f"❌ Errore con db.select('suppliers'): {e}")

def check_app_suppliers_implementation():
    """Verifica se la funzionalità fornitori è implementata nell'app"""
    
    print("\n📱 VERIFICANDO IMPLEMENTAZIONE FORNITORI NELL'APP...")
    print("=" * 50)
    
    app_file = current_dir / "app_es.py"
    if not app_file.exists():
        print("❌ File app_es.py non trovato")
        return False
    
    try:
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Cerca riferimenti ai fornitori
        supplier_patterns = [
            "supplier",
            "proveedor",
            "Gestión Proveedores",
            "Lista Proveedores",
            "Nuevo Proveedor"
        ]
        
        found_patterns = []
        for pattern in supplier_patterns:
            if pattern.lower() in content.lower():
                found_patterns.append(pattern)
        
        if found_patterns:
            print(f"✅ Pattern trovati nell'app: {found_patterns}")
        else:
            print("❌ Nessun pattern di fornitori trovato nell'app")
            print("   Questo spiega perché la lista è vuota!")
        
        return len(found_patterns) > 0
        
    except Exception as e:
        print(f"❌ Errore leggendo app_es.py: {e}")
        return False

if __name__ == "__main__":
    print("🔍 DIAGNOSI PROBLEMA FORNITORI")
    print("=" * 35)
    
    # 1. Verifica fornitori nel database
    db_has_suppliers = check_suppliers_in_database()
    
    # 2. Verifica struttura tabella
    table_exists = check_suppliers_table_structure()
    
    # 3. Verifica metodi database
    check_suppliers_methods()
    
    # 4. Verifica implementazione app
    app_has_suppliers = check_app_suppliers_implementation()
    
    # 5. Diagnosi finale
    print("\n🎯 DIAGNOSI FINALE")
    print("=" * 20)
    
    if db_has_suppliers and not app_has_suppliers:
        print("❌ PROBLEMA IDENTIFICATO:")
        print("   ✅ I fornitori sono salvati nel database")
        print("   ❌ La funzionalità fornitori NON è implementata nell'app")
        print("🔧 SOLUZIONE: Implementare la sezione fornitori in app_es.py")
    elif not db_has_suppliers:
        print("❌ PROBLEMA: Nessun fornitore trovato nel database")
    elif app_has_suppliers and db_has_suppliers:
        print("✅ TUTTO OK: Fornitori presenti sia nel database che nell'app")
    else:
        print("⚠️  PROBLEMA: Situazione non chiara, verifica necessaria")
    
    print("\n🎯 Diagnosi completata!")
