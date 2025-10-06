#!/usr/bin/env python3
"""
Verifica finale per la transazione di $8,498.42
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

def final_verification():
    """Verifica finale per la transazione di $8,498.42"""
    
    print("🔍 VERIFICA FINALE TRANSACTIONE $8,498.42")
    print("=" * 50)
    
    db = get_hybrid_manager()
    
    # 1. Verifica diretta nel database
    print("\n1️⃣ VERIFICA DIRETTA NEL DATABASE")
    print("-" * 40)
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            # Cerca tutte le transazioni con importo 8498.42
            print("🔍 Cercando transazioni con importo $8,498.42...")
            
            # Query per entrate
            income_response = db.supabase_manager.client.table('daily_income').select('*').eq('amount', 8498.42).execute()
            income_8498 = income_response.data or []
            
            # Query per uscite
            expense_response = db.supabase_manager.client.table('daily_expenses').select('*').eq('amount', 8498.42).execute()
            expense_8498 = expense_response.data or []
            
            print(f"💰 Entrate con $8,498.42: {len(income_8498)}")
            print(f"💸 Uscite con $8,498.42: {len(expense_8498)}")
            
            if income_8498 or expense_8498:
                print("❌ TROVATE TRANSACTIONI CON $8,498.42!")
                for income in income_8498:
                    print(f"  💰 ENTRATA: {income.get('date', 'N/A')} - {income.get('category', 'N/A')} - {income.get('description', 'N/A')}")
                for expense in expense_8498:
                    print(f"  💸 USCITA: {expense.get('date', 'N/A')} - {expense.get('category', 'N/A')} - {expense.get('description', 'N/A')}")
            else:
                print("✅ NESSUNA TRANSACTIONE CON $8,498.42 NEL DATABASE")
        else:
            print("❌ Connessione Supabase non disponibile")
    except Exception as e:
        print(f"❌ Errore verifica database: {e}")
    
    # 2. Test del metodo get_weekly_summary
    print("\n2️⃣ TEST METODO GET_WEEKLY_SUMMARY")
    print("-" * 40)
    
    try:
        if hasattr(db, 'get_weekly_summary'):
            print("✅ Metodo get_weekly_summary() esiste")
            
            # Test con la settimana problematica
            week_start = datetime(2025, 10, 5).date()
            print(f"📅 Testando settimana dal {week_start}")
            
            weekly_data = db.get_weekly_summary(week_start.isoformat())
            
            if weekly_data:
                total_expenses = sum([d.get('total_expenses', 0) for d in weekly_data])
                print(f"💸 Totale uscite: ${total_expenses:,.2f}")
                
                if abs(total_expenses - 8498.42) < 0.01:
                    print("❌ IL METODO RESTITUISCE ANCORA $8,498.42!")
                    
                    # Analizza ogni giorno
                    print("\n🔍 ANALISI GIORNALIERA:")
                    for day_data in weekly_data:
                        date = day_data.get('date', 'N/A')[:10]
                        expenses = day_data.get('total_expenses', 0)
                        if abs(expenses - 8498.42) < 0.01:
                            print(f"  🎯 {date}: ${expenses:,.2f} - QUESTO È IL PROBLEMA!")
                else:
                    print("✅ IL METODO RESTITUISCE I DATI CORRETTI!")
            else:
                print("❌ Nessun dato settimanale restituito")
        else:
            print("❌ Metodo get_weekly_summary() NON ESISTE")
    except Exception as e:
        print(f"❌ Errore testando metodo: {e}")
    
    # 3. Verifica tutte le transazioni della settimana
    print("\n3️⃣ VERIFICA TUTTE LE TRANSACTIONI DELLA SETTIMANA")
    print("-" * 50)
    
    try:
        week_start = datetime(2025, 10, 5).date()
        week_end = week_start + timedelta(days=6)
        
        print(f"📅 Settimana: {week_start} - {week_end}")
        
        # Ottieni tutte le transazioni della settimana
        all_transactions = []
        
        for i in range(7):
            current_date = week_start + timedelta(days=i)
            date_str = current_date.isoformat()
            
            # Query diretta per questo giorno
            try:
                income_response = db.supabase_manager.client.table('daily_income').select('*').eq('date', date_str).execute()
                expense_response = db.supabase_manager.client.table('daily_expenses').select('*').eq('date', date_str).execute()
                
                day_income = income_response.data or []
                day_expenses = expense_response.data or []
                
                if day_income or day_expenses:
                    print(f"  📅 {date_str}:")
                    for income in day_income:
                        amount = float(income.get('amount', 0))
                        print(f"    💰 ${amount:,.2f} - {income.get('category', 'N/A')}")
                        all_transactions.append(('income', amount, date_str))
                    for expense in day_expenses:
                        amount = float(expense.get('amount', 0))
                        print(f"    💸 ${amount:,.2f} - {expense.get('category', 'N/A')}")
                        all_transactions.append(('expense', amount, date_str))
                        
                        if abs(amount - 8498.42) < 0.01:
                            print(f"      🎯 TROVATA TRANSACTIONE DI $8,498.42!")
                            print(f"      📋 Dettagli: {expense}")
            except Exception as e:
                print(f"    ❌ Errore query per {date_str}: {e}")
        
        if not all_transactions:
            print("✅ NESSUNA TRANSACTIONE TROVATA PER QUESTA SETTIMANA")
        else:
            total_expenses = sum([amount for trans_type, amount, date in all_transactions if trans_type == 'expense'])
            print(f"\n📊 TOTALE USCITE SETTIMANALI: ${total_expenses:,.2f}")
            
            if abs(total_expenses - 8498.42) < 0.01:
                print("❌ IL TOTALE CORRISPONDE A $8,498.42!")
            else:
                print("✅ IL TOTALE NON CORRISPONDE A $8,498.42")
                
    except Exception as e:
        print(f"❌ Errore verifica transazioni: {e}")

if __name__ == "__main__":
    print("🔍 VERIFICA FINALE TRANSACTIONE $8,498.42")
    print("=" * 50)
    
    final_verification()
    
    print("\n🎯 VERIFICA COMPLETATA!")
    print("=" * 25)
