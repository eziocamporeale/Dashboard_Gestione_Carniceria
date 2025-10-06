#!/usr/bin/env python3
"""
Script per verificare il problema di visualizzazione fornitori
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
            
            # Recupera tutti i fornitori
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
                    print(f"   Note: {supplier.get('notes', 'N/A')}")
                    print(f"   Attivo: {supplier.get('is_active', 'N/A')}")
                    print(f"   Creato: {supplier.get('created_at', 'N/A')}")
                    print("-" * 40)
                
                # Cerca specificamente "Toledo Import"
                toledo_found = any('Toledo Import' in str(supplier.get('name', '')) for supplier in response.data)
                if toledo_found:
                    print("✅ 'Toledo Import' trovato nel database!")
                    return True
                else:
                    print("❌ 'Toledo Import' NON trovato nel database")
                    return False
            else:
                print("❌ Nessun fornitore trovato nel database")
                return False
                
        else:
            print("❌ Connessione Supabase non disponibile")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante il controllo: {e}")
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
        'create_supplier',
        'add_supplier'
    ]
    
    for method_name in methods_to_check:
        if hasattr(db, method_name):
            print(f"✅ Metodo '{method_name}' disponibile")
        else:
            print(f"❌ Metodo '{method_name}' NON disponibile")
    
    # Test del metodo select per suppliers
    try:
        suppliers = db.select('suppliers')
        if suppliers is not None:
            print(f"✅ db.select('suppliers') funziona - Trovati {len(suppliers)} fornitori")
            return True
        else:
            print("⚠️  db.select('suppliers') restituisce None")
            return False
    except Exception as e:
        print(f"❌ Errore con db.select('suppliers'): {e}")
        return False

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
            "Lista de Proveedores",
            "Nuevo Proveedor",
            "Gestión Proveedores",
            "get_suppliers",
            "suppliers =",
            "select('suppliers')"
        ]
        
        found_patterns = []
        for pattern in supplier_patterns:
            if pattern in content:
                found_patterns.append(pattern)
        
        if found_patterns:
            print(f"✅ Pattern fornitori trovati nell'app: {found_patterns}")
            
            # Cerca specificamente la sezione lista fornitori
            if "Lista de Proveedores" in content:
                print("✅ Sezione 'Lista de Proveedores' trovata")
                
                # Cerca il codice che dovrebbe mostrare i fornitori
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if "Lista de Proveedores" in line:
                        print(f"  📍 Linea {i+1}: {line.strip()}")
                        
                        # Controlla le righe successive per vedere come vengono caricati i fornitori
                        for j in range(1, 10):
                            if i+j < len(lines):
                                next_line = lines[i+j].strip()
                                if next_line and not next_line.startswith('#'):
                                    print(f"    {i+j+1}: {next_line}")
                                    if "suppliers" in next_line.lower() or "select" in next_line.lower():
                                        print(f"      🔍 Possibile caricamento fornitori")
                                        break
                        break
                
                return True
            else:
                print("❌ Sezione 'Lista de Proveedores' non trovata")
                return False
        else:
            print("❌ Nessun pattern di fornitori trovato nell'app")
            print("   Questo spiega perché la lista è vuota!")
            return False
        
    except Exception as e:
        print(f"❌ Errore leggendo app_es.py: {e}")
        return False

def check_suppliers_table_structure():
    """Verifica la struttura della tabella suppliers dopo l'aggiunta della colonna notes"""
    
    print("\n🗄️ VERIFICANDO STRUTTURA TABELLA SUPPLIERS DOPO FIX...")
    print("=" * 60)
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            print("📡 Connesso a Supabase")
            
            # Prova a recuperare un fornitore con tutti i campi
            response = db.supabase_manager.client.table('suppliers').select('*').limit(1).execute()
            
            if response.data:
                print("📋 Struttura tabella suppliers (aggiornata):")
                columns_found = []
                for key, value in response.data[0].items():
                    print(f"  - {key}: {type(value).__name__}")
                    columns_found.append(key)
                
                # Verifica se la colonna notes esiste ora
                if 'notes' in columns_found:
                    print("✅ Colonna 'notes' ora presente nella tabella!")
                    return True
                else:
                    print("❌ Colonna 'notes' ancora NON presente")
                    return False
            else:
                print("⚠️  Tabella vuota")
                return False
                
        else:
            print("❌ Connessione Supabase non disponibile")
            return False
            
    except Exception as e:
        print(f"❌ Errore verificando struttura: {e}")
        return False

if __name__ == "__main__":
    print("🔍 DIAGNOSI PROBLEMA VISUALIZZAZIONE FORNITORI")
    print("=" * 50)
    
    # 1. Verifica fornitori nel database
    db_has_suppliers = check_suppliers_in_database()
    
    # 2. Verifica struttura tabella
    table_structure_ok = check_suppliers_table_structure()
    
    # 3. Verifica metodi database
    methods_ok = check_suppliers_methods()
    
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
    elif db_has_suppliers and app_has_suppliers and methods_ok:
        print("✅ TUTTO OK: Fornitori presenti sia nel database che nell'app")
    elif not db_has_suppliers:
        print("❌ PROBLEMA: Nessun fornitore trovato nel database")
    elif not methods_ok:
        print("❌ PROBLEMA: Metodi per fornitori non funzionano")
    else:
        print("⚠️  PROBLEMA: Situazione non chiara, verifica necessaria")
    
    print("\n🎯 Diagnosi completata!")


