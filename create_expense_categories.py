#!/usr/bin/env python3
"""
Script per creare categorie di spesa
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

def create_expense_categories():
    """Crea categorie di spesa"""
    
    print("🔧 CREANDO CATEGORIE DI SPESA...")
    print("=" * 35)
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            print("📡 Connesso a Supabase")
            
            # Dati delle categorie di spesa
            expense_categories = [
                {
                    'name': 'Compras',
                    'type': 'expense',
                    'color': '#FF6B6B',
                    'icon': '🛍️',
                    'is_active': True
                },
                {
                    'name': 'Salarios',
                    'type': 'expense',
                    'color': '#4ECDC4',
                    'icon': '👥',
                    'is_active': True
                },
                {
                    'name': 'Alquiler',
                    'type': 'expense',
                    'color': '#45B7D1',
                    'icon': '🏠',
                    'is_active': True
                },
                {
                    'name': 'Servicios Públicos',
                    'type': 'expense',
                    'color': '#96CEB4',
                    'icon': '⚡',
                    'is_active': True
                },
                {
                    'name': 'Mantenimiento',
                    'type': 'expense',
                    'color': '#FFEAA7',
                    'icon': '🔧',
                    'is_active': True
                },
                {
                    'name': 'Marketing',
                    'type': 'expense',
                    'color': '#DDA0DD',
                    'icon': '📢',
                    'is_active': True
                },
                {
                    'name': 'Otros Gastos',
                    'type': 'expense',
                    'color': '#F39C12',
                    'icon': '💸',
                    'is_active': True
                }
            ]
            
            created_count = 0
            for category in expense_categories:
                try:
                    response = db.supabase_manager.client.table('accounting_categories').insert(category).execute()
                    if response.data:
                        print(f"✅ Categoria creata: {category['name']} {category['icon']}")
                        created_count += 1
                    else:
                        print(f"❌ Errore creando categoria: {category['name']}")
                except Exception as e:
                    print(f"⚠️  Categoria {category['name']} potrebbe già esistere: {e}")
            
            print(f"\n📊 Risultato: {created_count}/{len(expense_categories)} categorie create")
            
            # Verifica le categorie create
            response = db.supabase_manager.client.table('accounting_categories').select('*').eq('type', 'expense').eq('is_active', True).execute()
            
            if response.data:
                print(f"\n✅ Categorie di spesa disponibili ({len(response.data)}):")
                for cat in response.data:
                    print(f"  - {cat.get('name', 'N/A')} {cat.get('icon', '💰')} (ID: {cat.get('id', 'N/A')})")
                return True
            else:
                print("❌ Nessuna categoria di spesa trovata dopo la creazione")
                return False
                
        else:
            print("❌ Connessione Supabase non disponibile")
            return False
            
    except Exception as e:
        print(f"❌ Errore creando categorie: {e}")
        return False

def test_daily_expense_creation():
    """Testa la creazione di una spesa giornaliera"""
    
    print("\n🧪 TEST CREAZIONE SPESA GIORNALIERA...")
    print("=" * 45)
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            # Dati di test per una spesa
            test_expense = {
                'date': '2024-11-22',
                'amount': 250.50,
                'description': 'Compra de productos',
                'category': 'Compras',  # Usa una categoria esistente
                'payment_method': 'Efectivo'
            }
            
            print(f"🔧 Creando spesa di test: {test_expense['description']}")
            
            response = db.supabase_manager.client.table('daily_expenses').insert(test_expense).execute()
            
            if response.data:
                print("✅ Spesa creata con successo!")
                print(f"   ID: {response.data[0].get('id', 'N/A')}")
                print(f"   Importo: ${test_expense['amount']}")
                print(f"   Categoria: {test_expense['category']}")
                return True
            else:
                print("❌ Errore creando spesa")
                return False
                
        else:
            print("❌ Connessione Supabase non disponibile")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        return False

if __name__ == "__main__":
    print("🔍 FIX CATEGORIE DI SPESA")
    print("=" * 25)
    
    # 1. Crea categorie di spesa
    categories_created = create_expense_categories()
    
    if categories_created:
        # 2. Testa la creazione di una spesa
        test_ok = test_daily_expense_creation()
        
        print("\n🎯 RISULTATO FINALE")
        print("=" * 20)
        
        if test_ok:
            print("✅ CATEGORIE DI SPESA RISOLTE!")
            print("🎉 Le categorie di spesa sono state create")
            print("🎉 La creazione di spese giornaliere ora funziona")
            print("\n📋 Prova ora ad aggiungere una spesa nella dashboard!")
        else:
            print("❌ Test creazione spesa fallito")
    else:
        print("\n❌ Creazione categorie fallita")
    
    print("\n🎯 Script completato!")

