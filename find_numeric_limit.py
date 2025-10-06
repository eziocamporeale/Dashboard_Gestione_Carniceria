#!/usr/bin/env python3
"""
Script per trovare il limite numerico attuale del database
"""

import sys
from pathlib import Path

# Aggiungi il path del progetto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.hybrid_database_manager import get_hybrid_manager as get_db_manager

def find_numeric_limit():
    """Trova il limite numerico attuale"""
    print("🔍 Ricerca Limite Numerico Attuale")
    print("=" * 50)
    
    db = get_db_manager()
    
    if not db.supabase_manager.is_connected():
        print("❌ Supabase non connesso")
        return False
    
    try:
        # Test con importi crescenti per trovare il limite
        print("🧪 Test con importi crescenti:")
        print("-" * 30)
        
        test_amounts = [
            999.99,    # Dovrebbe funzionare (limite teorico NUMERIC(5,2))
            1000.00,   # Potrebbe fallire
            9999.99,   # Dovrebbe fallire se è ancora NUMERIC(5,2)
            10000.00,  # Dovrebbe fallire
            15000.00,  # Dovrebbe fallire
            25000.00,  # Dovrebbe fallire
            50000.00,  # Dovrebbe fallire
            99999.99,  # Dovrebbe fallire se è ancora NUMERIC(5,2)
            100000.00, # Dovrebbe fallire
        ]
        
        working_amounts = []
        failing_amounts = []
        
        for amount in test_amounts:
            print(f"   💰 Test ${amount:,.2f}: ", end="")
            
            test_data = {
                'date': '2025-01-05',
                'amount': amount,
                'category': 'Test Limit',
                'description': f'Test limite {amount}',
                'supplier': 'Test Supplier',
                'payment_method': 'Efectivo'
            }
            
            result = db.supabase_manager.insert('daily_expenses', test_data)
            if result:
                print("✅ OK")
                working_amounts.append(amount)
                # Rimuovi test
                test_id = result.get('id')
                if test_id:
                    db.supabase_manager.delete_daily_entry('expense', str(test_id))
            else:
                print("❌ FALLISCE")
                failing_amounts.append(amount)
        
        print("\n📊 RISULTATI:")
        print("-" * 20)
        print(f"✅ Importi che funzionano: {len(working_amounts)}")
        if working_amounts:
            print(f"   Max importo funzionante: ${max(working_amounts):,.2f}")
        
        print(f"❌ Importi che falliscono: {len(failing_amounts)}")
        if failing_amounts:
            print(f"   Primo importo che fallisce: ${min(failing_amounts):,.2f}")
        
        # Analisi del limite
        if max(working_amounts) < 1000:
            print("\n🔍 ANALISI:")
            print("   Schema attuale: NUMERIC(5,2) - Limite 999.99")
            print("   ⚠️ Fix NON applicato completamente")
            print("   💡 Devi applicare il fix in Supabase Dashboard")
        elif max(working_amounts) < 10000:
            print("\n🔍 ANALISI:")
            print("   Schema attuale: Probabilmente NUMERIC(6,2) - Limite 9999.99")
            print("   ⚠️ Fix parzialmente applicato")
        else:
            print("\n🔍 ANALISI:")
            print("   Schema attuale: NUMERIC(10,2) o superiore")
            print("   ✅ Fix applicato correttamente!")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        return False

if __name__ == "__main__":
    find_numeric_limit()


