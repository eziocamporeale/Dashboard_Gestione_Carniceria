#!/usr/bin/env python3
"""
Script per verificare se gli impiegati vengono dal database o sono hardcoded
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

def check_hardcoded_employees_in_code():
    """Verifica se ci sono impiegati hardcoded nel codice"""
    
    print("🔍 CERCANDO IMPIEGATI HARDCODED NEL CODICE...")
    print("=" * 50)
    
    # Cerca pattern comuni di dati hardcoded
    patterns_to_search = [
        "Orlando Garcia",
        "maspalomasorlando",
        "Carnicero Principal",
        "Ventas",
        "1830",
        "sample_employees",
        "hardcoded",
        "ficticio",
        "ejemplo"
    ]
    
    files_to_check = [
        "app_es.py",
        "database/hybrid_database_manager.py",
        "database/supabase_manager.py",
        "database/database_manager_simple.py"
    ]
    
    found_hardcoded = False
    
    for file_path in files_to_check:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"\n📄 Controllando {file_path}...")
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in patterns_to_search:
                    if pattern in content:
                        print(f"  ⚠️  Trovato '{pattern}' in {file_path}")
                        found_hardcoded = True
                        
                        # Mostra il contesto
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if pattern in line:
                                print(f"    Linea {i+1}: {line.strip()}")
                                
            except Exception as e:
                print(f"  ❌ Errore leggendo {file_path}: {e}")
        else:
            print(f"  ⚠️  File {file_path} non trovato")
    
    return found_hardcoded

def verify_database_employees():
    """Verifica gli impiegati nel database"""
    
    print("\n🗄️ VERIFICANDO IMPIEGATI NEL DATABASE...")
    print("=" * 45)
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            print("📡 Connesso a Supabase")
            
            # Recupera tutti gli impiegati con dettagli completi
            response = db.supabase_manager.client.table('employees').select('*').execute()
            
            if response.data:
                print(f"✅ Trovati {len(response.data)} impiegati nel database:")
                print("-" * 60)
                
                for i, emp in enumerate(response.data, 1):
                    print(f"{i}. ID: {emp.get('id', 'N/A')}")
                    print(f"   Nome: {emp.get('first_name', 'N/A')} {emp.get('last_name', 'N/A')}")
                    print(f"   Email: {emp.get('email', 'N/A')}")
                    print(f"   Posizione: {emp.get('position', 'N/A')}")
                    print(f"   Dipartimento: {emp.get('department', 'N/A')}")
                    print(f"   Salario: ${emp.get('salary', 0):,.2f}")
                    print(f"   Stato: {emp.get('status', 'N/A')}")
                    print(f"   Data assunzione: {emp.get('hire_date', 'N/A')}")
                    print(f"   Creato: {emp.get('created_at', 'N/A')}")
                    print(f"   Aggiornato: {emp.get('updated_at', 'N/A')}")
                    print("-" * 40)
                
                # Verifica se sono dati di test
                test_emails = [emp.get('email', '') for emp in response.data]
                if any('test' in email.lower() or 'example' in email.lower() for email in test_emails):
                    print("⚠️  ATTENZIONE: Alcuni impiegati sembrano essere dati di test!")
                    print("   Email con 'test' o 'example':")
                    for email in test_emails:
                        if 'test' in email.lower() or 'example' in email.lower():
                            print(f"     - {email}")
                
                return True
            else:
                print("❌ Nessun impiegato trovato nel database")
                return False
                
        else:
            print("❌ Connessione Supabase non disponibile")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante il controllo database: {e}")
        return False

def check_app_es_employees_logic():
    """Verifica la logica di caricamento impiegati in app_es.py"""
    
    print("\n🔍 VERIFICANDO LOGICA IMPIEGATI IN APP_ES.PY...")
    print("=" * 50)
    
    app_file = current_dir / "app_es.py"
    if not app_file.exists():
        print("❌ File app_es.py non trovato")
        return False
    
    try:
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Cerca la sezione render_personal
        if "def render_personal" in content:
            print("✅ Funzione render_personal trovata")
            
            # Cerca sample_employees
            if "sample_employees" in content:
                print("✅ Variabile sample_employees trovata")
                
                # Verifica come viene popolata
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if "sample_employees" in line and "=" in line:
                        print(f"  📍 Linea {i+1}: {line.strip()}")
                        
                        # Controlla le righe successive
                        for j in range(1, 5):
                            if i+j < len(lines):
                                next_line = lines[i+j].strip()
                                if next_line and not next_line.startswith('#'):
                                    print(f"    {i+j+1}: {next_line}")
                                    
                        break
            
            # Cerca dati hardcoded
            hardcoded_patterns = [
                "Orlando Garcia",
                "maspalomasorlando",
                "[{",
                "'name':",
                "'email':"
            ]
            
            found_patterns = []
            for pattern in hardcoded_patterns:
                if pattern in content:
                    found_patterns.append(pattern)
            
            if found_patterns:
                print(f"⚠️  Pattern sospetti trovati: {found_patterns}")
            else:
                print("✅ Nessun pattern di dati hardcoded sospetto trovato")
                
        return True
        
    except Exception as e:
        print(f"❌ Errore leggendo app_es.py: {e}")
        return False

if __name__ == "__main__":
    print("🔍 VERIFICA FONTE IMPIEGATI")
    print("=" * 35)
    
    # 1. Verifica dati hardcoded nel codice
    hardcoded_found = check_hardcoded_employees_in_code()
    
    # 2. Verifica impiegati nel database
    db_employees = verify_database_employees()
    
    # 3. Verifica logica in app_es.py
    app_logic_ok = check_app_es_employees_logic()
    
    # 4. Diagnosi finale
    print("\n🎯 DIAGNOSI FINALE")
    print("=" * 20)
    
    if hardcoded_found:
        print("❌ PROBLEMA: Dati hardcoded trovati nel codice")
        print("🔧 SOLUZIONE: Rimuovere dati hardcoded e usare solo database")
    elif db_employees and app_logic_ok:
        print("✅ TUTTO OK: Gli impiegati vengono dal database reale")
        print("✅ Nessun dato hardcoded trovato nel codice")
        print("✅ Logica di caricamento corretta")
    else:
        print("⚠️  PROBLEMA: Gli impiegati potrebbero non essere caricati correttamente")
        print("🔧 VERIFICA: Controllare la logica di caricamento dati")
    
    print("\n🎯 Verifica completata!")
