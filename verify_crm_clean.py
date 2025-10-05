#!/usr/bin/env python3
"""
Script per verificare che il CRM sia stato pulito dai dati hardcoded
Creado por Ezio Camporeale
"""

import os
import re
from pathlib import Path

def verify_crm_clean():
    """Verifica che il CRM sia stato pulito dai dati hardcoded"""
    
    app_file = Path("app_es.py")
    if not app_file.exists():
        print("❌ File app_es.py non trovato")
        return False
    
    print("🔍 VERIFICA PULIZIA CRM")
    print("=" * 30)
    
    # Leggi il file
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern da cercare (dati hardcoded)
    hardcoded_patterns = [
        (r"4\.1, 4\.0, 4\.2, 4\.3, 4\.1, 4\.4, 4\.2, 4\.3, 4\.2", "Dati hardcoded soddisfazione"),
        (r"'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep'", "Mesi hardcoded"),
        (r"analytics\['total_customers'\]", "Analytics hardcoded"),
        (r"analytics\['active_customers'\]", "Clienti attivi hardcoded"),
        (r"analytics\['churn_rate'\]", "Tasso abbandono hardcoded"),
        (r"analytics\['customer_satisfaction'\]", "Soddisfazione hardcoded"),
        (r"segments", "Segmenti hardcoded"),
        (r"campaigns", "Campagne hardcoded"),
        (r"predictions", "Predizioni hardcoded"),
        (r"get_customer_analytics\(\)", "Metodo analytics"),
        (r"get_customer_segments\(\)", "Metodo segmenti"),
        (r"get_marketing_campaigns\(\)", "Metodo campagne"),
        (r"get_customer_predictions\(\)", "Metodo predizioni")
    ]
    
    found_hardcoded = []
    
    for pattern, description in hardcoded_patterns:
        if re.search(pattern, content):
            found_hardcoded.append(description)
    
    # Verifica messaggi informativi
    info_patterns = [
        (r"Nessun dato disponibile", "Messaggi informativi presenti"),
        (r"Nessuna campagna disponibile", "Messaggi campagne presenti"),
        (r"Nessuna predizione disponibile", "Messaggi predizioni presenti"),
        (r"Inserisci dati reali", "Istruzioni per dati reali"),
        (r"aggiungi clienti", "Istruzioni per clienti")
    ]
    
    found_info = []
    
    for pattern, description in info_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            found_info.append(description)
    
    # Risultati
    print(f"\n📊 RISULTATI VERIFICA:")
    print(f"   Dati hardcoded trovati: {len(found_hardcoded)}")
    print(f"   Messaggi informativi trovati: {len(found_info)}")
    
    if found_hardcoded:
        print(f"\n⚠️  DATI HARDCODED ANCORA PRESENTI:")
        for item in found_hardcoded:
            print(f"   - {item}")
    else:
        print(f"\n✅ NESSUN DATO HARDCODED TROVATO!")
    
    if found_info:
        print(f"\n✅ MESSAGGI INFORMATIVI PRESENTI:")
        for item in found_info:
            print(f"   - {item}")
    else:
        print(f"\n❌ NESSUN MESSAGGIO INFORMATIVO TROVATO!")
    
    # Diagnosi finale
    print(f"\n🎯 DIAGNOSI FINALE:")
    if not found_hardcoded and found_info:
        print("✅ CRM COMPLETAMENTE PULITO!")
        print("✅ Messaggi informativi presenti")
        print("✅ Nessun dato hardcoded")
        return True
    elif found_hardcoded:
        print("❌ CRM NON COMPLETAMENTE PULITO")
        print("❌ Ancora presenti dati hardcoded")
        return False
    else:
        print("⚠️  CRM pulito ma mancano messaggi informativi")
        return False

if __name__ == "__main__":
    success = verify_crm_clean()
    if success:
        print("\n🎉 VERIFICA SUPERATA!")
        print("💡 Il CRM è pronto per mostrare solo dati reali.")
    else:
        print("\n❌ VERIFICA FALLITA!")
        print("🔧 È necessaria ulteriore pulizia.")
