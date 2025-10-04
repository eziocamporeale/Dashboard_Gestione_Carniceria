#!/usr/bin/env python3
"""
Script per pulire TUTTI i dati hardcoded da tutti i file
"""

import re
from pathlib import Path

def clean_hardcoded_data():
    """Pulisce tutti i dati hardcoded"""
    
    print("🧹 PULIZIA COMPLETA DATI HARDCODED...")
    
    # File da pulire
    files_to_clean = [
        'database/database_manager_simple.py',
        'database/supabase_manager.py',
        'app_es.py'
    ]
    
    for file_path in files_to_clean:
        file_full_path = Path(file_path)
        
        if not file_full_path.exists():
            print(f"⚠️ File non trovato: {file_path}")
            continue
            
        print(f"📝 Pulendo file: {file_path}")
        
        # Leggi il file
        with open(file_full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Rimuovi dati hardcoded comuni
        patterns_to_remove = [
            # Lista prodotti hardcoded
            (r'all_products = \[[\s\S]*?\]', 'all_products = []'),
            (r'sample_products = \[[\s\S]*?\]', 'sample_products = []'),
            (r'products_data = \[[\s\S]*?\]', 'products_data = []'),
            
            # Lista clienti hardcoded
            (r'all_customers = \[[\s\S]*?\]', 'all_customers = []'),
            (r'sample_customers = \[[\s\S]*?\]', 'sample_customers = []'),
            (r'customers_data = \[[\s\S]*?\]', 'customers_data = []'),
            
            # Lista fornitori hardcoded
            (r'all_suppliers = \[[\s\S]*?\]', 'all_suppliers = []'),
            (r'sample_suppliers = \[[\s\S]*?\]', 'sample_suppliers = []'),
            (r'suppliers_data = \[[\s\S]*?\]', 'suppliers_data = []'),
            
            # Lista vendite hardcoded
            (r'all_sales = \[[\s\S]*?\]', 'all_sales = []'),
            (r'sample_sales = \[[\s\S]*?\]', 'sample_sales = []'),
            (r'sales_data = \[[\s\S]*?\]', 'sales_data = []'),
            
            # Lista personale hardcoded
            (r'sample_employees = \[[\s\S]*?\]', 'sample_employees = []'),
            (r'employees_data = \[[\s\S]*?\]', 'employees_data = []'),
            
            # Dati hardcoded specifici
            (r"'name': 'Pollo Entero'", "'name': ''"),
            (r"'name': 'Jamón Cocido'", "'name': ''"),
            (r"'name': 'Carne de Res Premium'", "'name': ''"),
            (r"'name': 'Test products'", "'name': ''"),
            
            # Metriche hardcoded
            (r'\$[0-9,]+\.?[0-9]*', '$0.00'),
            (r'"[0-9,]+\.?[0-9]*"', '"0"'),
            
            # Logs hardcoded
            (r'logs = \[[\s\S]*?\]', 'logs = []'),
        ]
        
        # Applica i pattern
        for pattern, replacement in patterns_to_remove:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # Se il contenuto è cambiato, scrivi il file
        if content != original_content:
            with open(file_full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   ✅ File {file_path} pulito")
        else:
            print(f"   ℹ️ File {file_path} già pulito")
    
    print("\n🎉 PULIZIA COMPLETA TERMINATA!")
    print("✅ Tutti i dati hardcoded sono stati rimossi")

if __name__ == "__main__":
    clean_hardcoded_data()
