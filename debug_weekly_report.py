#!/usr/bin/env python3
"""
Debug approfondito per il report settimanale
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

def debug_weekly_report():
    """Debug approfondito del report settimanale"""
    
    print("🔍 DEBUG APPROFONDITO REPORT SETTIMANALE")
    print("=" * 50)
    
    db = get_hybrid_manager()
    
    # Simula esattamente quello che fa l'app
    week_start = datetime.now().date() - timedelta(days=7)
    print(f"📅 Settimana simulata: {week_start}")
    
    # Chiama il metodo come fa l'app
    print("\n🔍 Chiamando get_weekly_summary()...")
    weekly_data = db.get_weekly_summary(week_start.isoformat())
    
    print(f"📊 Risultato: {len(weekly_data)} giorni")
    
    if weekly_data:
        # Calcola esattamente come fa l'app
        total_income = sum([d['total_income'] for d in weekly_data])
        total_expenses = sum([d['total_expenses'] for d in weekly_data])
        total_profit = sum([d['net_profit'] for d in weekly_data])
        total_transactions = sum([d['transactions_count'] for d in weekly_data])
        
        print(f"\n📊 CALCOLI COME NELL'APP:")
        print(f"💰 total_income = {total_income}")
        print(f"💸 total_expenses = {total_expenses}")
        print(f"📈 total_profit = {total_profit}")
        print(f"📊 total_transactions = {total_transactions}")
        
        # Verifica se corrisponde a $8,498.42
        if abs(total_expenses - 8498.42) < 0.01:
            print(f"\n🎯 TROVATO! total_expenses = ${total_expenses} corrisponde a $8,498.42")
            
            # Analizza ogni giorno per trovare da dove viene
            print(f"\n🔍 ANALISI GIORNALIERA:")
            for i, day_data in enumerate(weekly_data):
                date = day_data.get('date', 'N/A')
                expenses = day_data.get('total_expenses', 0)
                transactions = day_data.get('transactions_count', 0)
                
                print(f"  📅 {date}: ${expenses:,.2f} ({transactions} transazioni)")
                
                if abs(expenses - 8498.42) < 0.01:
                    print(f"    🎯 QUESTO È IL GIORNO CON $8,498.42!")
                    
                    # Investigazione più approfondita per questo giorno
                    investigate_specific_day(date)
        else:
            print(f"\n❌ total_expenses = ${total_expenses} NON corrisponde a $8,498.42")
    else:
        print("❌ Nessun dato settimanale")

def investigate_specific_day(date_str):
    """Investiga un giorno specifico in dettaglio"""
    
    print(f"\n🔍 INVESTIGAZIONE DETTAGLIATA PER {date_str}")
    print("=" * 50)
    
    db = get_hybrid_manager()
    
    try:
        # Ottieni tutte le transazioni di quel giorno
        date_obj = datetime.fromisoformat(date_str).date()
        
        if hasattr(db, 'get_monthly_transactions'):
            monthly_data = db.get_monthly_transactions(date_obj.year, date_obj.month)
            
            # Filtra per il giorno specifico
            day_income = [t for t in monthly_data.get('income', []) if t.get('date', '').startswith(date_str)]
            day_expenses = [t for t in monthly_data.get('expenses', []) if t.get('date', '').startswith(date_str)]
            
            print(f"📊 Transazioni trovate:")
            print(f"  💰 Entrate: {len(day_income)}")
            print(f"  💸 Uscite: {len(day_expenses)}")
            
            if day_expenses:
                print(f"\n💸 DETTAGLIO USCITE:")
                total_expenses = 0
                for i, expense in enumerate(day_expenses):
                    amount = float(expense.get('amount', 0))
                    total_expenses += amount
                    print(f"  {i+1}. ${amount:,.2f} - {expense.get('category', 'N/A')} - {expense.get('description', 'N/A')}")
                    
                    if abs(amount - 8498.42) < 0.01:
                        print(f"    🎯 QUESTA È LA TRANSACTIONE DI $8,498.42!")
                        print(f"    📋 Dettagli completi: {expense}")
                
                print(f"\n📊 Totale uscite calcolato: ${total_expenses:,.2f}")
                
                if abs(total_expenses - 8498.42) < 0.01:
                    print(f"✅ CONFERMATO: Il totale corrisponde a $8,498.42")
                else:
                    print(f"❌ Il totale NON corrisponde a $8,498.42")
            else:
                print("❌ Nessuna uscita trovata per questo giorno")
        else:
            print("❌ Metodo get_monthly_transactions non disponibile")
            
    except Exception as e:
        print(f"❌ Errore durante investigazione: {e}")

def check_database_directly():
    """Controlla direttamente il database per la transazione"""
    
    print("\n🔍 CONTROLLO DIRETTO DATABASE")
    print("=" * 35)
    
    db = get_hybrid_manager()
    
    try:
        if db.use_supabase and db.supabase_manager and db.supabase_manager.is_connected():
            print("📡 Connesso a Supabase - controllo diretto...")
            
            # Cerca tutte le transazioni con importo 8498.42
            print("\n🔍 Cercando transazioni con importo $8,498.42...")
            
            try:
                # Query diretta per entrate
                income_response = db.supabase_manager.client.table('daily_income').select('*').eq('amount', 8498.42).execute()
                income_8498 = income_response.data or []
                
                # Query diretta per uscite
                expense_response = db.supabase_manager.client.table('daily_expenses').select('*').eq('amount', 8498.42).execute()
                expense_8498 = expense_response.data or []
                
                print(f"💰 Entrate con $8,498.42: {len(income_8498)}")
                print(f"💸 Uscite con $8,498.42: {len(expense_8498)}")
                
                if income_8498:
                    print(f"\n💰 ENTRATE TROVATE:")
                    for income in income_8498:
                        print(f"  📅 {income.get('date', 'N/A')} - {income.get('category', 'N/A')} - {income.get('description', 'N/A')}")
                
                if expense_8498:
                    print(f"\n💸 USCITE TROVATE:")
                    for expense in expense_8498:
                        print(f"  📅 {expense.get('date', 'N/A')} - {expense.get('category', 'N/A')} - {expense.get('description', 'N/A')}")
                        print(f"    🏪 Fornitore: {expense.get('supplier', 'N/A')}")
                        print(f"    💳 Metodo: {expense.get('payment_method', 'N/A')}")
                
                if not income_8498 and not expense_8498:
                    print("❌ Nessuna transazione con importo $8,498.42 trovata nel database")
                    print("🤔 Il valore potrebbe venire da un'altra fonte")
                
            except Exception as e:
                print(f"❌ Errore query diretta: {e}")
        else:
            print("❌ Connessione Supabase non disponibile")
            
    except Exception as e:
        print(f"❌ Errore controllo database: {e}")

if __name__ == "__main__":
    print("🔍 DEBUG APPROFONDITO REPORT SETTIMANALE")
    print("=" * 50)
    
    # 1. Debug del report settimanale
    debug_weekly_report()
    
    # 2. Controllo diretto database
    check_database_directly()
    
    print("\n🎯 DEBUG COMPLETATO!")
    print("=" * 25)
