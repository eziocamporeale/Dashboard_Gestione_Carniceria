#!/usr/bin/env python3
"""
Script per creare le tabelle di contabilità giornaliera in Supabase
"""

import sys
from pathlib import Path

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.supabase_manager import SupabaseManager

def create_accounting_tables():
    """Crea le tabelle di contabilità giornaliera"""
    
    print("🏗️ Creando tabelle di contabilità giornaliera...")
    
    # Leggi lo schema SQL
    schema_file = current_dir / "database" / "daily_accounting_schema.sql"
    
    if not schema_file.exists():
        print(f"❌ File schema non trovato: {schema_file}")
        return
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Inizializza Supabase
    supabase_manager = SupabaseManager()
    
    if not supabase_manager.is_connected():
        print("❌ Errore connessione Supabase")
        return
    
    try:
        # Esegui lo schema SQL
        print("📝 Eseguendo schema SQL...")
        
        # Dividi lo schema in singole query
        queries = schema_sql.split(';')
        
        for i, query in enumerate(queries):
            query = query.strip()
            if query and not query.startswith('--'):
                print(f"   🔄 Eseguendo query {i+1}/{len(queries)}...")
                try:
                    # Usa la connessione diretta per eseguire DDL
                    result = supabase_manager.supabase.rpc('exec_sql', {'sql': query}).execute()
                    print(f"   ✅ Query {i+1} eseguita")
                except Exception as e:
                    print(f"   ⚠️ Query {i+1} fallita (potrebbe già esistere): {e}")
        
        print("✅ Schema SQL eseguito!")
        
        # Verifica che le tabelle siano state create
        print("🔍 Verificando tabelle create...")
        
        tables_to_check = [
            'daily_income',
            'daily_expenses', 
            'accounting_categories',
            'daily_reports'
        ]
        
        for table in tables_to_check:
            try:
                result = supabase_manager.select(table, limit=1)
                print(f"   ✅ Tabella {table} creata correttamente")
            except Exception as e:
                print(f"   ❌ Errore verificando tabella {table}: {e}")
        
        print("🎉 Creazione tabelle completata!")
        
    except Exception as e:
        print(f"❌ Errore eseguendo schema: {e}")

if __name__ == "__main__":
    create_accounting_tables()
