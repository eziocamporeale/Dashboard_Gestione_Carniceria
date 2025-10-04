#!/usr/bin/env python3
"""
Script per rimuovere TUTTI i dati hardcoded dal file app_es.py
"""

import re
from pathlib import Path

def remove_hardcoded_data():
    """Rimuove tutti i dati hardcoded dal file app_es.py"""
    
    print("🧹 RIMOZIONE COMPLETA DATI HARDCODED...")
    print("=" * 60)
    
    app_file = Path("app_es.py")
    
    if not app_file.exists():
        print("❌ File app_es.py non trovato!")
        return
    
    # Leggi il file
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = 0
    
    # Pattern per rimuovere dati hardcoded
    patterns = [
        # Dati prodotti hardcoded
        (r'sample_products = \[[\s\S]*?\]', 'sample_products = []'),
        (r'products_data = \[[\s\S]*?\]', 'products_data = []'),
        (r'all_products = \[[\s\S]*?\]', 'all_products = []'),
        
        # Dati clienti hardcoded
        (r'sample_customers = \[[\s\S]*?\]', 'sample_customers = []'),
        (r'customers_data = \[[\s\S]*?\]', 'customers_data = []'),
        (r'all_customers = \[[\s\S]*?\]', 'all_customers = []'),
        
        # Dati fornitori hardcoded
        (r'sample_suppliers = \[[\s\S]*?\]', 'sample_suppliers = []'),
        (r'suppliers_data = \[[\s\S]*?\]', 'suppliers_data = []'),
        (r'all_suppliers = \[[\s\S]*?\]', 'all_suppliers = []'),
        
        # Dati vendite hardcoded
        (r'sample_sales = \[[\s\S]*?\]', 'sample_sales = []'),
        (r'sales_data = \[[\s\S]*?\]', 'sales_data = []'),
        (r'all_sales = \[[\s\S]*?\]', 'all_sales = []'),
        
        # Dati dipendenti hardcoded
        (r'sample_employees = \[[\s\S]*?\]', 'sample_employees = []'),
        (r'employees_data = \[[\s\S]*?\]', 'employees_data = []'),
        (r'all_employees = \[[\s\S]*?\]', 'all_employees = []'),
        
        # Dati turni hardcoded
        (r'sample_shifts = \[[\s\S]*?\]', 'sample_shifts = []'),
        (r'shifts_data = \[[\s\S]*?\]', 'shifts_data = []'),
        
        # Dati contabilità hardcoded
        (r'sample_income = \[[\s\S]*?\]', 'sample_income = []'),
        (r'sample_expenses = \[[\s\S]*?\]', 'sample_expenses = []'),
        (r'income_data = \[[\s\S]*?\]', 'income_data = []'),
        (r'expenses_data = \[[\s\S]*?\]', 'expenses_data = []'),
        
        # Dati analytics hardcoded
        (r'sales_data = \[[\s\S]*?\]', 'sales_data = []'),
        (r'chart_data = \[[\s\S]*?\]', 'chart_data = []'),
        (r'analytics_data = \[[\s\S]*?\]', 'analytics_data = []'),
    ]
    
    # Applica i pattern
    for pattern, replacement in patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        if matches:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            changes_made += len(matches)
            print(f"   ✅ Rimosso {len(matches)} blocchi di dati hardcoded")
    
    # Rimuovi anche dati hardcoded specifici
    specific_patterns = [
        # Valori monetari hardcoded
        (r'\$[0-9,]+\.?[0-9]*', '$0.00'),
        (r'"[0-9,]+\.?[0-9]*"', '"0"'),
        
        # Nomi prodotti hardcoded
        (r"'name': 'Pollo Entero'", "'name': ''"),
        (r"'name': 'Jamón Cocido'", "'name': ''"),
        (r"'name': 'Carne de Res Premium'", "'name': ''"),
        (r"'name': 'Salchichas'", "'name': ''"),
        (r"'name': 'Bife de Chorizo'", "'name': ''"),
        (r"'name': 'Producto'", "'name': ''"),
        (r"'name': 'Cliente'", "'name': ''"),
        (r"'name': 'Proveedor'", "'name': ''"),
        
        # Categorie hardcoded
        (r"'category': 'Carnes'", "'category': ''"),
        (r"'category': 'Aves'", "'category': ''"),
        (r"'category': 'Embutidos'", "'category': ''"),
        (r"'category': 'Pescados'", "'category': ''"),
        (r"'category': 'Verduras'", "'category': ''"),
        (r"'category': 'Ventas Carnes'", "'category': ''"),
        (r"'category': 'Ventas Embutidos'", "'category': ''"),
        (r"'category': 'Gastos Operativos'", "'category': ''"),
        
        # Quantità hardcoded
        (r"'quantity': [0-9]+", "'quantity': 0"),
        (r"'amount': [0-9]+", "'amount': 0"),
        (r"'price': [0-9]+", "'price': 0"),
    ]
    
    for pattern, replacement in specific_patterns:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            changes_made += len(matches)
            print(f"   ✅ Rimosso {len(matches)} valori hardcoded specifici")
    
    # Scrivi il file modificato
    if content != original_content:
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n🎉 PULIZIA COMPLETATA!")
        print(f"✅ Rimossi {changes_made} blocchi di dati hardcoded")
        print(f"📝 File app_es.py aggiornato")
    else:
        print("\n✅ File app_es.py già pulito - nessuna modifica necessaria")

if __name__ == "__main__":
    remove_hardcoded_data()
