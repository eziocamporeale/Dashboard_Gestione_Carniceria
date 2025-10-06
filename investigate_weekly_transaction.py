#!/usr/bin/env python3
"""
Script per investigare la transazione settimanale di $8,498.42
Creado por Ezio Camporeale
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Aggiungi il percorso della directory corrente al path di Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

try:
    from database.hybrid_database_manager import get_hybrid_manager
    print("✅ Importato HybridDatabaseManager")
except ImportError as e:
    print(f"❌ Errore import HybridDatabaseManager: {e}")
    sys.exit(1)

def investigate_weekly_transaction():
    """Investiga la transazione settimanale di $8,498.42"""
    
    print("🔍 INVESTIGAZIONE TRANSACTIONE SETTIMANALE")
    print("=" * 50)
    
    db = get_hybrid_manager()
    
    # Calcola la settimana dal 05/10 al 11/10/2025
    week_start = datetime(2025, 10, 5).date()
    week_end = week_start + timedelta(days=6)
    
    print(f"📅 Settimana investigata: {week_start} - {week_end}")
    print(f"🎯 Cercando transazione di $8,498.42")
    
    # Verifica se il metodo get_weekly_summary esiste
    if hasattr(db, 'get_weekly_summary'):
        print("✅ Metodo get_weekly_summary trovato")
        try:
            weekly_data = db.get_weekly_summary(week_start.isoformat())
            print(f"📊 Dati settimanali ottenuti: {len(weekly_data) if weekly_data else 0} giorni")
            
            if weekly_data:
                total_expenses = sum([d.get('total_expenses', 0) for d in weekly_data])
                print(f"💸 Totale uscite settimanali: ${total_expenses:,.2f}")
                
                if abs(total_expenses - 8498.42) < 0.01:
                    print("🎯 TROVATA! La transazione di $8,498.42 corrisponde ai dati settimanali")
                else:
                    print(f"❌ La transazione di $8,498.42 NON corrisponde ai dati settimanali (${total_expenses:,.2f})")
            else:
                print("❌ Nessun dato settimanale trovato")
                
        except Exception as e:
            print(f"❌ Errore chiamando get_weekly_summary: {e}")
    else:
        print("❌ Metodo get_weekly_summary NON ESISTE - questo potrebbe essere il problema!")
    
    # Investigazione diretta nel database
    print("\n🔍 INVESTIGAZIONE DIRETTA NEL DATABASE")
    print("=" * 40)
    
    try:
        # Ottieni tutte le transazioni della settimana
        weekly_income = []
        weekly_expenses = []
        
        for i in range(7):
            current_date = week_start + timedelta(days=i)
            date_str = current_date.isoformat()
            
            print(f"📅 Investigando {date_str}:")
            
            # Usa il metodo get_monthly_transactions per ottenere i dati giornalieri
            if hasattr(db, 'get_monthly_transactions'):
                # Ottieni transazioni del mese e filtra per il giorno
                monthly_data = db.get_monthly_transactions(current_date.year, current_date.month)
                
                day_income = [t for t in monthly_data.get('income', []) if t.get('date', '').startswith(date_str)]
                day_expenses = [t for t in monthly_data.get('expenses', []) if t.get('date', '').startswith(date_str)]
                
                if day_income:
                    print(f"  💰 Entrate: {len(day_income)} transazioni")
                    for income in day_income:
                        amount = float(income.get('amount', 0))
                        print(f"    - ${amount:,.2f} ({income.get('category', 'N/A')}) - {income.get('description', 'N/A')}")
                        weekly_income.append(income)
                
                if day_expenses:
                    print(f"  💸 Uscite: {len(day_expenses)} transazioni")
                    for expense in day_expenses:
                        amount = float(expense.get('amount', 0))
                        print(f"    - ${amount:,.2f} ({expense.get('category', 'N/A')}) - {expense.get('description', 'N/A')}")
                        weekly_expenses.append(expense)
                        
                        # Verifica se questa è la transazione di $8,498.42
                        if abs(amount - 8498.42) < 0.01:
                            print(f"    🎯 TROVATA! Questa è la transazione di $8,498.42!")
                            print(f"    📋 Dettagli: {expense}")
                
                if not day_income and not day_expenses:
                    print(f"  📊 Nessuna transazione per questo giorno")
            else:
                print(f"  ❌ Metodo get_monthly_transactions non disponibile")
        
        # Riepilogo settimanale
        print(f"\n📊 RIEPILOGO SETTIMANALE")
        print("=" * 30)
        
        total_weekly_income = sum([float(t.get('amount', 0)) for t in weekly_income])
        total_weekly_expenses = sum([float(t.get('amount', 0)) for t in weekly_expenses])
        
        print(f"💰 Totale entrate settimanali: ${total_weekly_income:,.2f} ({len(weekly_income)} transazioni)")
        print(f"💸 Totale uscite settimanali: ${total_weekly_expenses:,.2f} ({len(weekly_expenses)} transazioni)")
        
        if abs(total_weekly_expenses - 8498.42) < 0.01:
            print("✅ CONFERMATO: La transazione di $8,498.42 è presente nel database!")
            print("📋 È la somma di tutte le uscite della settimana")
        else:
            print(f"❌ La transazione di $8,498.42 NON corrisponde ai dati del database")
            print(f"🔍 Differenza: ${abs(total_weekly_expenses - 8498.42):,.2f}")
            
            # Cerca transazioni individuali di $8,498.42
            found_8498 = False
            for expense in weekly_expenses:
                amount = float(expense.get('amount', 0))
                if abs(amount - 8498.42) < 0.01:
                    print(f"🎯 TROVATA transazione individuale di $8,498.42:")
                    print(f"   📅 Data: {expense.get('date', 'N/A')}")
                    print(f"   📂 Categoria: {expense.get('category', 'N/A')}")
                    print(f"   📝 Descrizione: {expense.get('description', 'N/A')}")
                    print(f"   🏪 Fornitore: {expense.get('supplier', 'N/A')}")
                    found_8498 = True
            
            if not found_8498:
                print("❌ Nessuna transazione individuale di $8,498.42 trovata")
                print("🤔 La transazione potrebbe essere hardcoded nel codice")
        
    except Exception as e:
        print(f"❌ Errore durante investigazione database: {e}")

def check_hardcoded_data():
    """Verifica se ci sono dati hardcoded nel codice"""
    
    print("\n🔍 RICERCA DATI HARDCODED NEL CODICE")
    print("=" * 45)
    
    # Cerca il valore 8498.42 nel codice
    import subprocess
    
    try:
        result = subprocess.run(['grep', '-r', '8498.42', '.'], 
                              capture_output=True, text=True, cwd=current_dir)
        
        if result.stdout:
            print("🎯 TROVATO! Il valore 8498.42 è presente nel codice:")
            print(result.stdout)
        else:
            print("✅ Il valore 8498.42 NON è hardcoded nel codice")
            
        # Cerca anche 8498
        result2 = subprocess.run(['grep', '-r', '8498', '.'], 
                               capture_output=True, text=True, cwd=current_dir)
        
        if result2.stdout:
            print("\n🔍 Altri riferimenti a 8498:")
            print(result2.stdout)
            
    except Exception as e:
        print(f"❌ Errore durante ricerca nel codice: {e}")

if __name__ == "__main__":
    print("🔍 INVESTIGAZIONE TRANSACTIONE SETTIMANALE")
    print("=" * 50)
    
    # 1. Investigazione database
    investigate_weekly_transaction()
    
    # 2. Ricerca dati hardcoded
    check_hardcoded_data()
    
    print("\n🎯 INVESTIGAZIONE COMPLETATA!")
    print("=" * 30)
