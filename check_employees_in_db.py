#!/usr/bin/env python3
"""
Script per verificare se ci sono impiegati nel database
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

def check_employees_in_database():
    """Verifica se ci sono impiegati nel database"""
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            print("📡 Connesso a Supabase")
            
            # Recupera tutti gli impiegati
            response = db.supabase_manager.client.table('employees').select('*').execute()
            
            if response.data:
                print(f"✅ Trovati {len(response.data)} impiegati nel database:")
                print("=" * 60)
                
                for i, emp in enumerate(response.data, 1):
                    print(f"{i}. Nome: {emp.get('first_name', 'N/A')} {emp.get('last_name', 'N/A')}")
                    print(f"   Email: {emp.get('email', 'N/A')}")
                    print(f"   Posizione: {emp.get('position', 'N/A')}")
                    print(f"   Dipartimento: {emp.get('department', 'N/A')}")
                    print(f"   Salario: ${emp.get('salary', 0):,.2f}")
                    print(f"   Stato: {emp.get('status', 'N/A')}")
                    print(f"   Data assunzione: {emp.get('hire_date', 'N/A')}")
                    print("-" * 40)
                
                return True
            else:
                print("❌ Nessun impiegato trovato nel database")
                return False
                
        else:
            print("❌ Connessione Supabase non disponibile")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante il controllo: {e}")
        return False

def test_database_select():
    """Testa il metodo select del database manager"""
    
    db = get_hybrid_manager()
    
    try:
        print("\n🧪 Testando db.select('employees')...")
        employees = db.select('employees') or []
        
        print(f"✅ db.select() ha restituito {len(employees)} impiegati")
        
        if employees:
            print("📋 Primi 3 impiegati trovati:")
            for i, emp in enumerate(employees[:3], 1):
                print(f"  {i}. {emp.get('first_name', 'N/A')} {emp.get('last_name', 'N/A')} - {emp.get('email', 'N/A')}")
        
        return len(employees)
        
    except Exception as e:
        print(f"❌ Errore db.select(): {e}")
        return 0

if __name__ == "__main__":
    print("🔍 VERIFICA IMPIEGATI NEL DATABASE")
    print("=" * 45)
    
    # Controlla direttamente il database
    print("\n1️⃣ CONTROLLO DIRETTO DATABASE")
    print("-" * 30)
    db_has_employees = check_employees_in_database()
    
    # Testa il metodo select del database manager
    print("\n2️⃣ TEST METODO DB.SELECT")
    print("-" * 25)
    select_count = test_database_select()
    
    # Diagnosi
    print("\n3️⃣ DIAGNOSI")
    print("-" * 10)
    
    if db_has_employees and select_count > 0:
        print("✅ IMPIEGATI PRESENTI NEL DATABASE")
        print("❌ PROBLEMA: La lista non si aggiorna correttamente")
        print("\n🔧 SOLUZIONE:")
        print("1. Ricarica la pagina (F5 o Ctrl+R)")
        print("2. Verifica che sample_employees = db.select('employees') funzioni")
        print("3. Controlla se c'è un problema di cache")
    elif db_has_employees and select_count == 0:
        print("✅ IMPIEGATI PRESENTI NEL DATABASE")
        print("❌ PROBLEMA: Il metodo db.select() non funziona")
        print("\n🔧 SOLUZIONE:")
        print("1. Verifica l'implementazione di db.select()")
        print("2. Controlla se c'è un problema di mapping dei dati")
    else:
        print("❌ NESSUN IMPIEGATO NEL DATABASE")
        print("❌ PROBLEMA: Gli impiegati non sono stati salvati")
        print("\n🔧 SOLUZIONE:")
        print("1. Verifica che il form di creazione funzioni")
        print("2. Controlla i log per errori di salvataggio")
    
    print("\n🎯 Verifica completata!")
