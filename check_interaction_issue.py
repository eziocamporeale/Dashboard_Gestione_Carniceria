#!/usr/bin/env python3
"""
Script per verificare il problema con le interazioni
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

def check_interactions_in_database():
    """Verifica le interazioni nel database"""
    
    print("🔍 VERIFICANDO INTERAZIONI NEL DATABASE...")
    print("=" * 45)
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            print("📡 Connesso a Supabase")
            
            # Prova a recuperare tutte le interazioni
            try:
                response = db.supabase_manager.client.table('customer_interactions').select('*').execute()
                
                if response.data:
                    print(f"✅ Trovate {len(response.data)} interazioni nel database:")
                    print("-" * 60)
                    
                    for i, interaction in enumerate(response.data, 1):
                        print(f"{i}. ID: {interaction.get('id', 'N/A')}")
                        print(f"   Cliente ID: {interaction.get('customer_id', 'N/A')}")
                        print(f"   Tipo: {interaction.get('type', 'N/A')}")
                        print(f"   Data: {interaction.get('date', 'N/A')}")
                        print(f"   Descrizione: {interaction.get('description', 'N/A')}")
                        print(f"   Risultato: {interaction.get('outcome', 'N/A')}")
                        print(f"   Dipendente: {interaction.get('employee', 'N/A')}")
                        print(f"   Note: {interaction.get('notes', 'N/A')}")
                        print("-" * 40)
                    
                    # Cerca specificamente l'interazione di "Soporte Magnetico"
                    soporte_interactions = [i for i in response.data if i.get('customer_id') == '5369d0ec-e3f2-479e-a266-76a1a9b2ca41']
                    if soporte_interactions:
                        print("✅ Interazioni per 'Soporte Magnetico' trovate nel database!")
                        for interaction in soporte_interactions:
                            print(f"   - {interaction.get('type')} del {interaction.get('date')}")
                    else:
                        print("❌ Nessuna interazione per 'Soporte Magnetico' trovata nel database")
                    
                    return True
                else:
                    print("❌ Nessuna interazione trovata nel database")
                    return False
                    
            except Exception as e:
                print(f"❌ Errore durante il recupero interazioni: {e}")
                
                # Se l'errore è specifico, proviamo a capire quale tabella manca
                error_str = str(e)
                if "relation" in error_str and "does not exist" in error_str:
                    print("⚠️  Tabella 'customer_interactions' non esiste")
                    print("🔧 SOLUZIONE: Creare la tabella customer_interactions in Supabase")
                elif "Could not find the" in error_str:
                    print("⚠️  Colonna mancante nella tabella")
                    print("🔧 SOLUZIONE: Verificare la struttura della tabella")
                
                return False
                
        else:
            print("❌ Connessione Supabase non disponibile")
            return False
            
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        return False

def check_interaction_methods():
    """Verifica i metodi per le interazioni nel database manager"""
    
    print("\n🔧 VERIFICANDO METODI INTERAZIONI NEL DATABASE MANAGER...")
    print("=" * 60)
    
    db = get_hybrid_manager()
    
    # Verifica metodi disponibili
    methods_to_check = [
        'add_customer_interaction',
        'get_customer_interactions',
        'create_customer_interaction',
        'select'
    ]
    
    for method_name in methods_to_check:
        if hasattr(db, method_name):
            print(f"✅ Metodo '{method_name}' disponibile")
        else:
            print(f"❌ Metodo '{method_name}' NON disponibile")
    
    # Test del metodo select per customer_interactions
    try:
        interactions = db.select('customer_interactions')
        if interactions is not None:
            print(f"✅ db.select('customer_interactions') funziona - Trovate {len(interactions)} interazioni")
        else:
            print("⚠️  db.select('customer_interactions') restituisce None")
    except Exception as e:
        print(f"❌ Errore con db.select('customer_interactions'): {e}")

def check_interaction_creation_method():
    """Verifica il metodo di creazione interazioni"""
    
    print("\n🧪 VERIFICANDO METODO CREAZIONE INTERAZIONI...")
    print("=" * 50)
    
    db = get_hybrid_manager()
    
    # Dati di test per l'interazione
    test_interaction = {
        'customer_id': '5369d0ec-e3f2-479e-a266-76a1a9b2ca41',
        'type': 'test',
        'date': '2025-10-05',
        'description': 'Test interaction',
        'outcome': 'satisfecho',
        'notes': 'Test notes',
        'employee': 'Test Employee'
    }
    
    try:
        # Prova a creare un'interazione di test
        if hasattr(db, 'add_customer_interaction'):
            result = db.add_customer_interaction(test_interaction)
            print(f"✅ Test creazione interazione: {'SUCCESSO' if result else 'FALLITA'}")
            return result
        else:
            print("❌ Metodo add_customer_interaction non disponibile")
            return False
    except Exception as e:
        print(f"❌ Errore durante test creazione: {e}")
        return False

if __name__ == "__main__":
    print("🔍 DIAGNOSI PROBLEMA INTERAZIONI")
    print("=" * 35)
    
    # 1. Verifica interazioni nel database
    db_has_interactions = check_interactions_in_database()
    
    # 2. Verifica metodi database
    check_interaction_methods()
    
    # 3. Testa creazione interazione
    creation_test = check_interaction_creation_method()
    
    # 4. Diagnosi finale
    print("\n🎯 DIAGNOSI FINALE")
    print("=" * 20)
    
    if not db_has_interactions and not creation_test:
        print("❌ PROBLEMA IDENTIFICATO:")
        print("   ❌ Nessuna interazione trovata nel database")
        print("   ❌ Metodo di creazione non funziona")
        print("🔧 SOLUZIONE: Implementare correttamente i metodi per le interazioni")
    elif not db_has_interactions and creation_test:
        print("⚠️  PROBLEMA: Interazioni create ma non recuperate")
        print("🔧 SOLUZIONE: Verificare metodo di recupero")
    elif db_has_interactions:
        print("✅ TUTTO OK: Interazioni presenti nel database")
    else:
        print("⚠️  PROBLEMA: Situazione non chiara, verifica necessaria")
    
    print("\n🎯 Diagnosi completata!")
