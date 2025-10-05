#!/usr/bin/env python3
"""
Script per creare categorie di entrata (versione corretta)
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

def create_income_categories_fixed():
    """Crea categorie di entrata con la struttura corretta"""
    
    print("🔧 CREANDO CATEGORIE DI ENTRATA (STRUTTURA CORRETTA)...")
    print("=" * 60)
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            print("📡 Connesso a Supabase")
            
            # Dati delle categorie di entrata (senza description)
            income_categories = [
                {
                    'name': 'Ventas',
                    'type': 'income',
                    'color': '#00D084',
                    'icon': '🛒',
                    'is_active': True
                },
                {
                    'name': 'Servicios',
                    'type': 'income',
                    'color': '#636EFA',
                    'icon': '🔧',
                    'is_active': True
                },
                {
                    'name': 'Subvenciones',
                    'type': 'income',
                    'color': '#00B4DB',
                    'icon': '🏛️',
                    'is_active': True
                },
                {
                    'name': 'Otros Ingresos',
                    'type': 'income',
                    'color': '#F7931E',
                    'icon': '💰',
                    'is_active': True
                }
            ]
            
            created_count = 0
            for category in income_categories:
                try:
                    response = db.supabase_manager.client.table('accounting_categories').insert(category).execute()
                    if response.data:
                        print(f"✅ Categoria creata: {category['name']} {category['icon']}")
                        created_count += 1
                    else:
                        print(f"❌ Errore creando categoria: {category['name']}")
                except Exception as e:
                    print(f"⚠️  Categoria {category['name']} potrebbe già esistere: {e}")
            
            print(f"\n📊 Risultato: {created_count}/{len(income_categories)} categorie create")
            
            # Verifica le categorie create
            response = db.supabase_manager.client.table('accounting_categories').select('*').eq('type', 'income').eq('is_active', True).execute()
            
            if response.data:
                print(f"\n✅ Categorie di entrata disponibili ({len(response.data)}):")
                for cat in response.data:
                    print(f"  - {cat.get('name', 'N/A')} {cat.get('icon', '💰')} (ID: {cat.get('id', 'N/A')})")
                return True
            else:
                print("❌ Nessuna categoria di entrata trovata dopo la creazione")
                return False
                
        else:
            print("❌ Connessione Supabase non disponibile")
            return False
            
    except Exception as e:
        print(f"❌ Errore creando categorie: {e}")
        return False

def test_daily_income_creation():
    """Testa la creazione di una entrata giornaliera"""
    
    print("\n🧪 TEST CREAZIONE ENTRATA GIORNALIERA...")
    print("=" * 45)
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            # Dati di test per una entrata
            test_income = {
                'date': '2024-11-22',
                'amount': 1531.75,
                'description': 'Total dià',
                'category': 'Ventas',  # Usa una categoria esistente
                'payment_method': 'Efectivo'
            }
            
            print(f"🔧 Creando entrata di test: {test_income['description']}")
            
            response = db.supabase_manager.client.table('daily_income').insert(test_income).execute()
            
            if response.data:
                print("✅ Entrata creata con successo!")
                print(f"   ID: {response.data[0].get('id', 'N/A')}")
                print(f"   Importo: ${test_income['amount']}")
                print(f"   Categoria: {test_income['category']}")
                return True
            else:
                print("❌ Errore creando entrata")
                return False
                
        else:
            print("❌ Connessione Supabase non disponibile")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        return False

def verify_daily_expenses_categories():
    """Verifica se esistono categorie di spesa"""
    
    print("\n🔍 VERIFICANDO CATEGORIE DI SPESA...")
    print("=" * 40)
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            # Recupera categorie di spesa
            response = db.supabase_manager.client.table('accounting_categories').select('*').eq('type', 'expense').eq('is_active', True).execute()
            
            if response.data:
                print(f"✅ Trovate {len(response.data)} categorie di spesa:")
                for cat in response.data:
                    print(f"  - {cat.get('name', 'N/A')} {cat.get('icon', '💰')} (ID: {cat.get('id', 'N/A')})")
                return True
            else:
                print("❌ Nessuna categoria di spesa trovata")
                return False
                
        else:
            print("❌ Connessione Supabase non disponibile")
            return False
            
    except Exception as e:
        print(f"❌ Errore verificando categorie di spesa: {e}")
        return False

if __name__ == "__main__":
    print("🔍 FIX CATEGORIE DI ENTRATA (VERSIONE CORRETTA)")
    print("=" * 50)
    
    # 1. Crea categorie di entrata
    categories_created = create_income_categories_fixed()
    
    if categories_created:
        # 2. Testa la creazione di una entrata
        test_ok = test_daily_income_creation()
        
        # 3. Verifica categorie di spesa
        expenses_ok = verify_daily_expenses_categories()
        
        print("\n🎯 RISULTATO FINALE")
        print("=" * 20)
        
        if test_ok:
            print("✅ CATEGORIE DI ENTRATA RISOLTE!")
            print("🎉 Le categorie di entrata sono state create")
            print("🎉 La creazione di entrate giornaliere ora funziona")
            print("\n📋 Prova ora ad aggiungere un'entrata nella dashboard!")
            
            if not expenses_ok:
                print("\n⚠️  ATTENZIONE: Manca categorie di spesa")
                print("🔧 Le uscite giornaliere potrebbero avere lo stesso problema")
        else:
            print("❌ Test creazione entrata fallito")
    else:
        print("\n❌ Creazione categorie fallita")
    
    print("\n🎯 Script completato!")

