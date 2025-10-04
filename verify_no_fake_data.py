#!/usr/bin/env python3
"""
Script per verificare che non ci siano più dati fittizi nella dashboard
"""

import re
import os

def check_for_fake_data():
    """Verifica che non ci siano dati fittizi"""
    print("🔍 Verificando assenza di dati fittizi...")
    
    # File da controllare
    files_to_check = [
        "app_es.py",
        "database/supabase_manager.py",
        "database/hybrid_database_manager.py", 
        "database/database_manager_simple.py"
    ]
    
    fake_data_patterns = [
        # Pattern per dati di vendita fittizi
        r"'sales':\s*\d+\.?\d*",
        r"'ventas':\s*\d+\.?\d*",
        r"'revenue':\s*\d+\.?\d*",
        r"'amount':\s*\d+\.?\d*",
        
        # Pattern per date fittizie
        r"'date':\s*'2024-\d{2}-\d{2}'",
        r"'fecha':\s*'2024-\d{2}-\d{2}'",
        
        # Pattern per quantità fittizie (escludere valori di default)
        r"'quantity':\s*[2-9]\d*",
        r"'cantidad':\s*[2-9]\d*",
        
        # Pattern per prezzi fittizi
        r"'price':\s*\d+\.?\d*",
        r"'precio':\s*\d+\.?\d*",
        
        # Pattern per generazione dinamica di dati
        r"base_sales\s*=\s*\d+",
        r"variation\s*=\s*.*hash.*",
        r"daily_sales\s*=\s*max.*",
        r"random\.randint.*",
        r"hash\(str\(date\)\).*",
        
        # Pattern per liste di dati fittizi
        r"return\s*\[.*\{.*'sales'.*\}\]",
        r"return\s*\[.*\{.*'ventas'.*\}\]",
    ]
    
    issues_found = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"\n📁 Controllando {file_path}...")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    for pattern in fake_data_patterns:
                        if re.search(pattern, line):
                            issues_found.append({
                                'file': file_path,
                                'line': i,
                                'content': line.strip(),
                                'pattern': pattern
                            })
                            print(f"  ❌ Riga {i}: {line.strip()[:80]}...")
    
    if issues_found:
        print(f"\n❌ Trovati {len(issues_found)} problemi con dati fittizi:")
        for issue in issues_found:
            print(f"  📄 {issue['file']}:{issue['line']}")
            print(f"     {issue['content']}")
        return False
    else:
        print("\n✅ Nessun dato fittizio trovato!")
        return True

def check_for_empty_returns():
    """Verifica che i metodi restituiscano liste vuote"""
    print("\n🔍 Verificando che i metodi restituiscano liste vuote...")
    
    files_to_check = [
        "database/supabase_manager.py",
        "database/hybrid_database_manager.py", 
        "database/database_manager_simple.py"
    ]
    
    methods_to_check = [
        "get_daily_sales",
        "get_daily_sales_data", 
        "get_sales_by_category",
        "get_top_selling_products",
        "get_sales_forecast"
    ]
    
    issues_found = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                for method in methods_to_check:
                    # Cerca il metodo
                    method_pattern = rf"def\s+{method}\s*\([^)]*\):"
                    method_match = re.search(method_pattern, content)
                    
                    if method_match:
                        # Estrai il corpo del metodo
                        start = method_match.end()
                        lines = content[start:].split('\n')
                        
                        method_body = []
                        indent_level = None
                        
                        for line in lines:
                            if line.strip() == '':
                                continue
                            
                            # Determina il livello di indentazione
                            current_indent = len(line) - len(line.lstrip())
                            
                            if indent_level is None and current_indent > 0:
                                indent_level = current_indent
                            
                            if indent_level is not None and current_indent < indent_level:
                                break
                                
                            if current_indent >= indent_level:
                                method_body.append(line)
                        
                        method_text = '\n'.join(method_body)
                        
                        # Verifica che restituisca una lista vuota
                        if "return []" not in method_text and "return [{" in method_text:
                            issues_found.append({
                                'file': file_path,
                                'method': method,
                                'issue': 'Metodo restituisce dati fittizi invece di lista vuota'
                            })
                            print(f"  ❌ {file_path} - {method}: restituisce dati fittizi")
    
    if issues_found:
        print(f"\n❌ Trovati {len(issues_found)} metodi che restituiscono dati fittizi:")
        for issue in issues_found:
            print(f"  📄 {issue['file']} - {issue['method']}: {issue['issue']}")
        return False
    else:
        print("\n✅ Tutti i metodi restituiscono liste vuote!")
        return True

def main():
    """Funzione principale"""
    print("🧹 Verifica completa assenza dati fittizi")
    print("=" * 50)
    
    # Verifica pattern di dati fittizi
    fake_data_clean = check_for_fake_data()
    
    # Verifica metodi che restituiscono liste vuote
    empty_returns_clean = check_for_empty_returns()
    
    print("\n" + "=" * 50)
    if fake_data_clean and empty_returns_clean:
        print("✅ VERIFICA COMPLETATA: Dashboard completamente pulita!")
        print("🎉 Nessun dato fittizio trovato.")
        return True
    else:
        print("❌ VERIFICA FALLITA: Ancora presenti dati fittizi!")
        print("🔧 È necessario rimuovere i dati fittizi rimanenti.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
