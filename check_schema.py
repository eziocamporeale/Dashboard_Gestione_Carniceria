#!/usr/bin/env python3
"""
Script per verificare lo schema attuale del database
"""

import sys
from pathlib import Path

# Aggiungi il path del progetto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.hybrid_database_manager import get_hybrid_manager as get_db_manager

def check_schema():
    """Verifica lo schema attuale del database"""
    print("🔍 Verifica Schema Database")
    print("=" * 50)
    
    db = get_db_manager()
    
    if not db.supabase_manager.is_connected():
        print("❌ Supabase non connesso")
        return False
    
    try:
        # Query per verificare lo schema delle colonne amount
        schema_query = """
        SELECT 
            table_name,
            column_name,
            data_type,
            numeric_precision,
            numeric_scale,
            is_nullable
        FROM information_schema.columns 
        WHERE table_name IN ('daily_income', 'daily_expenses') 
        AND column_name = 'amount'
        ORDER BY table_name;
        """
        
        print("📊 Schema attuale colonne amount:")
        print("-" * 40)
        
        # Esegui query tramite Supabase
        result = db.supabase_manager.client.rpc('exec_sql', {'sql': schema_query}).execute()
        
        if result.data:
            for row in result.data:
                table = row['table_name']
                precision = row['numeric_precision']
                scale = row['numeric_scale']
                
                print(f"📋 Tabella: {table}")
                print(f"   Tipo: NUMERIC({precision},{scale})")
                print(f"   Max valore: {10**(precision-scale)-1}.{scale*'9'}")
                print()
        else:
            print("❌ Impossibile recuperare schema - prova metodo alternativo")
            
            # Test pratico con importi
            print("🧪 Test pratico con importi:")
            test_amounts = [999.99, 1000.00, 9999.99, 25000.00]
            
            for amount in test_amounts:
                print(f"   💰 Test ${amount:,.2f}: ", end="")
                
                test_data = {
                    'date': '2025-01-05',
                    'amount': amount,
                    'category': 'Test',
                    'description': f'Test {amount}',
                    'supplier': 'Test',
                    'payment_method': 'Efectivo'
                }
                
                result = db.supabase_manager.insert('daily_expenses', test_data)
                if result:
                    print("✅ OK")
                    # Rimuovi test
                    test_id = result.get('id')
                    if test_id:
                        db.supabase_manager.delete_daily_entry('expense', str(test_id))
                else:
                    print("❌ FALLISCE")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore durante la verifica: {e}")
        return False

if __name__ == "__main__":
    check_schema()

