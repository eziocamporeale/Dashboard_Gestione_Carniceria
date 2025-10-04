#!/usr/bin/env python3
"""
Script per verificare che non ci siano più dati hardcoded
"""

import re
from pathlib import Path

def verify_no_hardcoded_data():
    """Verifica che non ci siano più dati hardcoded"""
    
    print("🔍 VERIFICA ASSENZA DATI HARDCODED...")
    print("=" * 60)
    
    app_file = Path("app_es.py")
    
    if not app_file.exists():
        print("❌ File app_es.py non trovato!")
        return False
    
    # Leggi il file
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues_found = 0
    
    # Pattern per cercare dati hardcoded
    patterns = [
        # Liste di dati hardcoded
        (r'sample_\w+ = \[.*?\]', 'Liste di dati hardcoded (sample_)'),
        (r'products_data = \[.*?\]', 'Dati prodotti hardcoded'),
        (r'customers_data = \[.*?\]', 'Dati clienti hardcoded'),
        (r'suppliers_data = \[.*?\]', 'Dati fornitori hardcoded'),
        (r'sales_data = \[.*?\]', 'Dati vendite hardcoded'),
        (r'employees_data = \[.*?\]', 'Dati dipendenti hardcoded'),
        
        # Valori monetari hardcoded
        (r'\$[1-9][0-9,]*\.?[0-9]*', 'Valori monetari hardcoded'),
        (r'"[1-9][0-9,]*\.?[0-9]*"', 'Valori numerici hardcoded'),
        
        # Nomi prodotti hardcoded
        (r"'name': '[A-Za-z\s]+'", 'Nomi prodotti hardcoded'),
        (r"'category': '[A-Za-z\s]+'", 'Categorie hardcoded'),
        
        # Quantità hardcoded
        (r"'quantity': [1-9][0-9]*", 'Quantità hardcoded'),
        (r"'amount': [1-9][0-9]*", 'Importi hardcoded'),
        (r"'price': [1-9][0-9]*", 'Prezzi hardcoded'),
    ]
    
    for pattern, description in patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        if matches:
            issues_found += len(matches)
            print(f"   ❌ Trovati {len(matches)} {description}")
            for match in matches[:3]:  # Mostra solo i primi 3
                print(f"      - {match[:50]}...")
            if len(matches) > 3:
                print(f"      ... e altri {len(matches) - 3}")
    
    print("\n" + "=" * 60)
    
    if issues_found == 0:
        print("✅ VERIFICA COMPLETATA!")
        print("🎉 Nessun dato hardcoded trovato!")
        print("📊 I grafici ora mostreranno dati vuoti o dal database")
        return True
    else:
        print(f"⚠️  TROVATI {issues_found} DATI HARDCODED!")
        print("🔧 Esegui remove_all_hardcoded_data.py per rimuoverli")
        return False

if __name__ == "__main__":
    verify_no_hardcoded_data()
