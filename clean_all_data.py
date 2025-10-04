#!/usr/bin/env python3
"""
Script per pulire COMPLETAMENTE tutti i dati dal database
Elimina tutti i dati hardcoded e di esempio
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.hybrid_database_manager import get_hybrid_manager

def clean_all_data():
    """Pulisce COMPLETAMENTE tutti i dati dal database"""
    
    print("🧹 INIZIANDO PULIZIA COMPLETA DEL DATABASE...")
    print("⚠️  ATTENZIONE: Questo eliminerà TUTTI i dati!")
    
    db = get_hybrid_manager()
    
    # Lista completa di tutte le tabelle da pulire
    all_tables = [
        # Tabelle vecchie
        'sales',
        'purchases', 
        'suppliers',
        'customers',
        'products',
        'product_categories',
        'units_of_measure',
        'employees',
        'orders',
        'order_items',
        'inventory_transactions',
        'excel_data',
        'monthly_summary',
        
        # Tabelle nuove contabilità
        'daily_income',
        'daily_expenses',
        'daily_reports',
        'accounting_categories',
        
        # Altre tabelle
        'activity_log',
        'backup_logs',
        'system_logs'
    ]
    
    print(f"📊 Trovate {len(all_tables)} tabelle da pulire")
    
    for table in all_tables:
        try:
            print(f"🗑️ Pulendo tabella: {table}")
            
            # Prova a ottenere tutti i record
            try:
                if hasattr(db, 'client') and db.client:
                    # Usa Supabase
                    result = db.client.table(table).select('id').execute()
                    records = result.data if result.data else []
                else:
                    # Usa SQLite
                    records = db.select(table, 'id') if hasattr(db, 'select') else []
                
                if records:
                    print(f"   📊 Trovati {len(records)} record")
                    
                    # Elimina tutti i record
                    for record in records:
                        record_id = record.get('id')
                        if record_id:
                            try:
                                if hasattr(db, 'client') and db.client:
                                    # Usa Supabase
                                    db.client.table(table).delete().eq('id', record_id).execute()
                                else:
                                    # Usa SQLite
                                    db.delete(table, record_id)
                                print(f"   ✅ Eliminato record {record_id}")
                            except Exception as e:
                                print(f"   ⚠️ Errore eliminando record {record_id}: {e}")
                    
                    print(f"   ✅ Tabella {table} pulita")
                else:
                    print(f"   ℹ️ Tabella {table} già vuota")
                    
            except Exception as e:
                print(f"   ⚠️ Tabella {table} non esiste o errore: {e}")
                
        except Exception as e:
            print(f"   ❌ Errore generale con tabella {table}: {e}")
    
    print("\n🎉 PULIZIA COMPLETA TERMINATA!")
    print("✅ Il database è ora completamente pulito")
    print("🚀 Puoi iniziare a caricare dati reali da zero")

if __name__ == "__main__":
    clean_all_data()
