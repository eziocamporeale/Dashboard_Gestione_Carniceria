#!/usr/bin/env python3
"""
Script per fixare l'errore numeric field overflow
Aumenta la precisione dei campi amount per supportare importi maggiori
"""

import sys
from pathlib import Path

# Aggiungi il path del progetto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.hybrid_database_manager import get_hybrid_manager as get_db_manager

def fix_numeric_precision():
    """Fix dell'errore numeric field overflow"""
    print("🔧 Fix Numeric Field Overflow")
    print("=" * 50)
    
    db = get_db_manager()
    
    if not db.supabase_manager.is_connected():
        print("❌ Supabase non connesso")
        return False
    
    try:
        # SQL per aumentare la precisione
        sql_commands = [
            "ALTER TABLE daily_income ALTER COLUMN amount TYPE NUMERIC(10,2);",
            "ALTER TABLE daily_expenses ALTER COLUMN amount TYPE NUMERIC(10,2);"
        ]
        
        print("📊 Aggiornamento precisione campi amount...")
        
        for sql in sql_commands:
            print(f"   🔄 Eseguendo: {sql}")
            try:
                # Esegui comando SQL direttamente
                result = db.supabase_manager.client.rpc('exec_sql', {'sql': sql}).execute()
                print(f"   ✅ Comando eseguito con successo")
            except Exception as e:
                print(f"   ⚠️ Errore esecuzione comando: {e}")
                # Prova metodo alternativo
                try:
                    db.supabase_manager.client.postgrest.rpc('exec_sql', {'sql': sql})
                    print(f"   ✅ Comando eseguito con metodo alternativo")
                except Exception as e2:
                    print(f"   ❌ Errore anche con metodo alternativo: {e2}")
        
        # Test con importo grande
        print("\n🧪 Test con importo grande (8498.42)...")
        
        test_data = {
            'date': '2025-01-05',
            'amount': 8498.42,
            'category': 'Test Category',
            'description': 'Test importo grande - da eliminare',
            'supplier': 'Test Supplier',
            'payment_method': 'Efectivo'
        }
        
        result = db.supabase_manager.insert('daily_expenses', test_data)
        if result:
            print(f"   ✅ Test superato! Importo {test_data['amount']} inserito correttamente")
            
            # Rimuovi il record di test
            test_id = result.get('id')
            if test_id:
                success = db.supabase_manager.delete_daily_entry('expense', str(test_id))
                if success:
                    print("   🗑️ Record di test rimosso")
                else:
                    print("   ⚠️ Errore rimuovendo record di test")
        else:
            print("   ❌ Test fallito - errore ancora presente")
            return False
        
        print("\n🎉 Fix completato con successo!")
        print("💡 Ora puoi inserire importi fino a 99,999,999.99")
        return True
        
    except Exception as e:
        print(f"❌ Errore durante il fix: {e}")
        return False

def test_large_amounts():
    """Test con vari importi grandi"""
    print("\n🧪 Test Importi Grandi")
    print("-" * 30)
    
    db = get_db_manager()
    
    test_amounts = [
        1000.00,
        5000.50,
        9999.99,
        15000.75,
        99999.99
    ]
    
    for amount in test_amounts:
        print(f"   💰 Test importo: ${amount:,.2f}")
        
        test_data = {
            'date': '2025-01-05',
            'amount': amount,
            'category': 'Test Category',
            'description': f'Test importo {amount}',
            'supplier': 'Test Supplier',
            'payment_method': 'Efectivo'
        }
        
        result = db.supabase_manager.insert('daily_expenses', test_data)
        if result:
            print(f"      ✅ Successo")
            # Rimuovi test
            test_id = result.get('id')
            if test_id:
                db.supabase_manager.delete_daily_entry('expense', str(test_id))
        else:
            print(f"      ❌ Fallito")
            return False
    
    print("   🎉 Tutti i test di importi grandi superati!")
    return True

if __name__ == "__main__":
    if fix_numeric_precision():
        test_large_amounts()

