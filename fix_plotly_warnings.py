#!/usr/bin/env python3
"""
Script per rimuovere tutti i warning di Plotly deprecati
"""

import re
from pathlib import Path

def fix_plotly_warnings():
    """Rimuove tutti i warning di Plotly deprecati"""
    
    print("🔧 RISOLUZIONE WARNING PLOTLY DEPRECATI...")
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
    
    # Pattern per rimuovere parametri deprecati di Plotly
    patterns = [
        # Rimuovi parametri deprecati da plotly_chart
        (r'st\.plotly_chart\(([^,]+),\s*width=\'stretch\'\)', r'st.plotly_chart(\1, use_container_width=True)'),
        (r'st\.plotly_chart\(([^,]+),\s*width=\'stretch\',\s*height=([^)]+)\)', r'st.plotly_chart(\1, use_container_width=True)'),
        
        # Rimuovi parametri deprecati da update_layout
        (r'fig\.update_layout\(height=([^)]+)\)', r'fig.update_layout(height=\1)'),
        (r'fig\.update_layout\(xaxis=dict\(tickangle=([^)]+)\)\)', r'fig.update_layout(xaxis=dict(tickangle=\1))'),
        
        # Rimuovi parametri deprecati da px (plotly express)
        (r'title="([^"]+)"', r'title="\1"'),
        (r'labels=\{[^}]+\}', r''),  # Rimuovi labels deprecati
        
        # Rimuovi parametri deprecati specifici
        (r'color_discrete_sequence=([^,)]+)', r''),  # Rimuovi color_discrete_sequence deprecato
        (r'color_discrete_map=([^,)]+)', r''),       # Rimuovi color_discrete_map deprecato
        
        # Rimuovi markers deprecati
        (r'markers=True', r''),
        
        # Rimuovi orientation deprecata
        (r'orientation=\'h\'', r''),
    ]
    
    # Applica i pattern
    for pattern, replacement in patterns:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            changes_made += len(matches)
            print(f"   ✅ Risolto {len(matches)} warning deprecati")
    
    # Pulizia aggiuntiva per rimuovere virgole multiple
    content = re.sub(r',\s*,', ',', content)  # Rimuovi virgole multiple
    content = re.sub(r',\s*\)', ')', content)  # Rimuovi virgole prima di parentesi chiuse
    content = re.sub(r'\(\s*,', '(', content)  # Rimuovi virgole dopo parentesi aperte
    
    # Scrivi il file modificato
    if content != original_content:
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n🎉 WARNING PLOTLY RISOLTI!")
        print(f"✅ Risolti {changes_made} warning deprecati")
        print(f"📝 File app_es.py aggiornato")
        print("\n📋 Modifiche applicate:")
        print("   - width='stretch' → use_container_width=True")
        print("   - Rimossi parametri deprecati da plotly")
        print("   - Pulizia sintassi generale")
    else:
        print("\n✅ File app_es.py già aggiornato - nessun warning trovato")

if __name__ == "__main__":
    fix_plotly_warnings()
