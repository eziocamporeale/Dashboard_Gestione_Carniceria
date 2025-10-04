#!/usr/bin/env python3
"""
Script per verificare che non ci siano più warning di Plotly deprecati
"""

import re
from pathlib import Path

def verify_no_plotly_warnings():
    """Verifica che non ci siano più warning di Plotly deprecati"""
    
    print("🔍 VERIFICA ASSENZA WARNING PLOTLY...")
    print("=" * 60)
    
    app_file = Path("app_es.py")
    
    if not app_file.exists():
        print("❌ File app_es.py non trovato!")
        return False
    
    # Leggi il file
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    warnings_found = 0
    
    # Pattern per cercare warning deprecati
    patterns = [
        (r'width=\'stretch\'', 'Parametro width=\'stretch\' deprecato'),
        (r'color_discrete_sequence=', 'Parametro color_discrete_sequence deprecato'),
        (r'color_discrete_map=', 'Parametro color_discrete_map deprecato'),
        (r'markers=True', 'Parametro markers=True deprecato'),
        (r'orientation=\'h\'', 'Parametro orientation=\'h\' deprecato'),
        (r'labels=\{[^}]+\}', 'Parametro labels deprecato'),
    ]
    
    for pattern, description in patterns:
        matches = re.findall(pattern, content)
        if matches:
            warnings_found += len(matches)
            print(f"   ❌ Trovati {len(matches)} {description}")
            for match in matches[:3]:  # Mostra solo i primi 3
                print(f"      - {match}")
            if len(matches) > 3:
                print(f"      ... e altri {len(matches) - 3}")
    
    print("\n" + "=" * 60)
    
    if warnings_found == 0:
        print("✅ VERIFICA COMPLETATA!")
        print("🎉 Nessun warning di Plotly deprecato trovato!")
        print("📊 I grafici ora usano la sintassi aggiornata di Plotly")
        return True
    else:
        print(f"⚠️  TROVATI {warnings_found} WARNING PLOTLY!")
        print("🔧 Esegui fix_plotly_warnings.py per risolverli")
        return False

if __name__ == "__main__":
    verify_no_plotly_warnings()
