#!/usr/bin/env python3
"""
Script per correggere sistematicamente tutti gli errori di sintassi nel file app_es.py
"""

import re
import ast
from pathlib import Path

def fix_all_syntax_errors():
    """Corregge tutti gli errori di sintassi nel file app_es.py"""
    
    print("🔧 CORREZIONE SISTEMATICA ERRORI DI SINTASSI...")
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
    
    # Dividi in righe per analisi
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        line_num = i + 1
        fixed_line = line
        
        # 1. Correggi indentazione errata per blocchi with
        if re.match(r'^\s*with\s+col\d+:', line):
            # Verifica che l'indentazione sia corretta (4 spazi per livello)
            indent_level = len(line) - len(line.lstrip())
            if indent_level > 0:
                # Calcola l'indentazione corretta
                correct_indent = ' ' * indent_level
                if not line.startswith(correct_indent):
                    fixed_line = correct_indent + line.lstrip()
                    if fixed_line != line:
                        print(f"   ✅ Riga {line_num}: Corretta indentazione with col")
                        changes_made += 1
        
        # 2. Correggi indentazione per st.metric
        if 'st.metric(' in line and not line.strip().startswith('st.metric('):
            # Verifica che st.metric sia correttamente indentato
            if line.strip().startswith('st.metric('):
                # Trova il livello di indentazione del blocco precedente
                prev_line = lines[i-1] if i > 0 else ""
                if 'with col' in prev_line:
                    prev_indent = len(prev_line) - len(prev_line.lstrip())
                    correct_indent = ' ' * (prev_indent + 4)
                    fixed_line = correct_indent + line.strip()
                    if fixed_line != line:
                        print(f"   ✅ Riga {line_num}: Corretta indentazione st.metric")
                        changes_made += 1
        
        # 3. Correggi indentazione per st.write
        if 'st.write(' in line and not line.strip().startswith('st.write('):
            if line.strip().startswith('st.write('):
                prev_line = lines[i-1] if i > 0 else ""
                if 'with col' in prev_line:
                    prev_indent = len(prev_line) - len(prev_line.lstrip())
                    correct_indent = ' ' * (prev_indent + 4)
                    fixed_line = correct_indent + line.strip()
                    if fixed_line != line:
                        print(f"   ✅ Riga {line_num}: Corretta indentazione st.write")
                        changes_made += 1
        
        # 4. Correggi indentazione per st.caption
        if 'st.caption(' in line and not line.strip().startswith('st.caption('):
            if line.strip().startswith('st.caption('):
                prev_line = lines[i-1] if i > 0 else ""
                if 'with col' in prev_line:
                    prev_indent = len(prev_line) - len(prev_line.lstrip())
                    correct_indent = ' ' * (prev_indent + 4)
                    fixed_line = correct_indent + line.strip()
                    if fixed_line != line:
                        print(f"   ✅ Riga {line_num}: Corretta indentazione st.caption")
                        changes_made += 1
        
        # 5. Correggi indentazione per st.button
        if 'st.button(' in line and not line.strip().startswith('st.button('):
            if line.strip().startswith('st.button('):
                prev_line = lines[i-1] if i > 0 else ""
                if 'with col' in prev_line:
                    prev_indent = len(prev_line) - len(prev_line.lstrip())
                    correct_indent = ' ' * (prev_indent + 4)
                    fixed_line = correct_indent + line.strip()
                    if fixed_line != line:
                        print(f"   ✅ Riga {line_num}: Corretta indentazione st.button")
                        changes_made += 1
        
        # 6. Correggi indentazione per st.markdown
        if 'st.markdown(' in line and not line.strip().startswith('st.markdown('):
            if line.strip().startswith('st.markdown('):
                prev_line = lines[i-1] if i > 0 else ""
                if 'with col' in prev_line:
                    prev_indent = len(prev_line) - len(prev_line.lstrip())
                    correct_indent = ' ' * (prev_indent + 4)
                    fixed_line = correct_indent + line.strip()
                    if fixed_line != line:
                        print(f"   ✅ Riga {line_num}: Corretta indentazione st.markdown")
                        changes_made += 1
        
        # 7. Correggi indentazione per if statements
        if line.strip().startswith('if ') and not line.strip().startswith('if '):
            if line.strip().startswith('if '):
                prev_line = lines[i-1] if i > 0 else ""
                if 'with col' in prev_line:
                    prev_indent = len(prev_line) - len(prev_line.lstrip())
                    correct_indent = ' ' * (prev_indent + 4)
                    fixed_line = correct_indent + line.strip()
                    if fixed_line != line:
                        print(f"   ✅ Riga {line_num}: Corretta indentazione if")
                        changes_made += 1
        
        # 8. Correggi indentazione per else statements
        if line.strip().startswith('else:') and not line.strip().startswith('else:'):
            if line.strip().startswith('else:'):
                prev_line = lines[i-1] if i > 0 else ""
                if 'with col' in prev_line:
                    prev_indent = len(prev_line) - len(prev_line.lstrip())
                    correct_indent = ' ' * (prev_indent + 4)
                    fixed_line = correct_indent + line.strip()
                    if fixed_line != line:
                        print(f"   ✅ Riga {line_num}: Corretta indentazione else")
                        changes_made += 1
        
        fixed_lines.append(fixed_line)
    
    # Ricostruisci il contenuto
    fixed_content = '\n'.join(fixed_lines)
    
    # Scrivi il file modificato
    if fixed_content != original_content:
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"\n🎉 CORREZIONE SINTASSI COMPLETATA!")
        print(f"✅ Corrette {changes_made} righe con errori di indentazione")
        print(f"📝 File app_es.py aggiornato")
    else:
        print("\n✅ File app_es.py già corretto - nessuna modifica necessaria")
    
    # Verifica sintassi finale
    try:
        with open(app_file, 'r', encoding='utf-8') as f:
            test_content = f.read()
        ast.parse(test_content)
        print("✅ Sintassi Python verificata - nessun errore!")
    except SyntaxError as e:
        print(f"❌ Errore di sintassi rimanente: {e}")
        print(f"   Riga {e.lineno}: {e.text}")

if __name__ == "__main__":
    fix_all_syntax_errors()
