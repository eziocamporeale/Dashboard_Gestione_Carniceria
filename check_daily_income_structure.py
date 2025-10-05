#!/usr/bin/env python3
"""
Script per verificare la struttura della tabella daily_income
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

def check_daily_income_structure():
    """Verifica la struttura della tabella daily_income"""
    
    print("🔍 VERIFICANDO STRUTTURA TABELLA DAILY_INCOME...")
    print("=" * 55)
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            print("📡 Connesso a Supabase")
            
            # Prova a recuperare un record per vedere la struttura
            response = db.supabase_manager.client.table('daily_income').select('*').limit(1).execute()
            
            if response.data:
                print("📋 Struttura tabella daily_income:")
                columns_found = []
                for key, value in response.data[0].items():
                    print(f"  - {key}: {type(value).__name__} = {value}")
                    columns_found.append(key)
                
                # Verifica se la colonna category esiste
                if 'category' in columns_found:
                    print("✅ Colonna 'category' presente nella tabella")
                else:
                    print("❌ Colonna 'category' NON presente nella tabella")
                
                # Verifica se ci sono altre colonne di categoria
                category_columns = [col for col in columns_found if 'categor' in col.lower()]
                if category_columns:
                    print(f"📝 Colonne categoria trovate: {category_columns}")
                else:
                    print("⚠️  Nessuna colonna categoria trovata")
                
                return columns_found
            else:
                print("⚠️  Tabella vuota - provo a inserire un record di test")
                
                # Prova a inserire un record di test per vedere la struttura
                test_data = {
                    'date': '2024-11-22',
                    'amount': 100.0,
                    'description': 'Test entry',
                    'category': 'Test Category',
                    'payment_method': 'Efectivo'
                }
                
                try:
                    response = db.supabase_manager.client.table('daily_income').insert(test_data).execute()
                    print("✅ Record di test inserito con successo")
                    
                    # Ora recupera il record per vedere la struttura
                    response = db.supabase_manager.client.table('daily_income').select('*').limit(1).execute()
                    if response.data:
                        print("📋 Struttura tabella daily_income (dal record di test):")
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

def check_accounting_categories():
    """Verifica le categorie disponibili"""
    
    print("\n🔍 VERIFICANDO CATEGORIE CONTABILITÀ...")
    print("=" * 40)
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            # Recupera categorie di entrata
            income_categories = db.supabase_manager.client.table('accounting_categories').select('*').eq('type', 'income').eq('is_active', True).execute()
            
            if income_categories.data:
                print(f"✅ Trovate {len(income_categories.data)} categorie di entrata:")
                for cat in income_categories.data:
                    print(f"  - {cat.get('name', 'N/A')} (ID: {cat.get('id', 'N/A')})")
                return income_categories.data
            else:
                print("❌ Nessuna categoria di entrata trovata")
                return []
        else:
            print("❌ Connessione Supabase non disponibile")
            return []
            
    except Exception as e:
        print(f"❌ Errore verificando categorie: {e}")
        return []

def check_daily_reports_structure():
    """Verifica la struttura della tabella daily_reports"""
    
    print("\n🔍 VERIFICANDO STRUTTURA TABELLA DAILY_REPORTS...")
    print("=" * 50)
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            # Prova a recuperare un record per vedere la struttura
            response = db.supabase_manager.client.table('daily_reports').select('*').limit(1).execute()
            
            if response.data:
                print("📋 Struttura tabella daily_reports:")
                columns_found = []
                for key, value in response.data[0].items():
                    print(f"  - {key}: {type(value).__name__} = {value}")
                    columns_found.append(key)
                
                # Verifica se la colonna date esiste
                if 'date' in columns_found:
                    print("✅ Colonna 'date' presente nella tabella")
                else:
                    print("❌ Colonna 'date' NON presente nella tabella")
                
                return columns_found
            else:
                print("⚠️  Tabella daily_reports vuota")
                return []
                
        else:
            print("❌ Connessione Supabase non disponibile")
            return []
            
    except Exception as e:
        print(f"❌ Errore verificando struttura daily_reports: {e}")
        return []

if __name__ == "__main__":
    print("🔍 DIAGNOSI PROBLEMI CONTABILITÀ")
    print("=" * 40)
    
    # 1. Verifica struttura daily_income
    daily_income_columns = check_daily_income_structure()
    
    # 2. Verifica categorie disponibili
    categories = check_accounting_categories()
    
    # 3. Verifica struttura daily_reports
    daily_reports_columns = check_daily_reports_structure()
    
    # 4. Diagnosi finale
    print("\n🎯 DIAGNOSI FINALE")
    print("=" * 20)
    
    if 'category' not in daily_income_columns:
        print("❌ PROBLEMA IDENTIFICATO:")
        print("   La colonna 'category' non esiste nella tabella daily_income")
        print("🔧 SOLUZIONE: Aggiungere la colonna 'category' alla tabella")
    elif not categories:
        print("❌ PROBLEMA IDENTIFICATO:")
        print("   Nessuna categoria di entrata disponibile")
        print("🔧 SOLUZIONE: Creare categorie di entrata nella tabella accounting_categories")
    else:
        print("✅ Struttura daily_income OK")
    
    if 'date' not in daily_reports_columns:
        print("❌ PROBLEMA IDENTIFICATO:")
        print("   La colonna 'date' non esiste nella tabella daily_reports")
        print("🔧 SOLUZIONE: Aggiungere la colonna 'date' alla tabella")
    else:
        print("✅ Struttura daily_reports OK")
    
    print("\n🎯 Diagnosi completata!")

