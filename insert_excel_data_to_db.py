#!/usr/bin/env python3
"""
Script per inserire i dati estratti dal file Excel nel database Supabase
"""

import json
import os
from datetime import datetime
from supabase import create_client, Client
import sys

# Aggiungi il path per importare i moduli locali
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_supabase_client():
    """Crea il client Supabase"""
    try:
        # Importa la configurazione locale
        from config.supabase_config import SupabaseConfig
        
        # Usa la configurazione esistente
        url = SupabaseConfig.SUPABASE_URL
        key = SupabaseConfig.SUPABASE_ANON_KEY
        
        if not url or not key:
            print("❌ Configurazione Supabase non trovata")
            return None
        
        supabase: Client = create_client(url, key)
        print("✅ Connessione a Supabase stabilita")
        return supabase
        
    except Exception as e:
        print(f"❌ Errore nella connessione a Supabase: {e}")
        return None

def clear_test_data(supabase):
    """Elimina i dati di test dal database"""
    print("\n🗑️ Eliminando dati di test...")
    
    try:
        # Elimina dati di test dalla tabella excel_data
        try:
            result = supabase.table('excel_data').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
            print(f"   ✅ Tabella excel_data: dati eliminati")
        except Exception as e:
            print(f"   ⚠️ Errore eliminando da excel_data: {e}")
        
        # Elimina anche da monthly_summary se esiste
        try:
            result = supabase.table('monthly_summary').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
            print(f"   ✅ Tabella monthly_summary: dati eliminati")
        except Exception as e:
            print(f"   ⚠️ Errore eliminando da monthly_summary: {e}")
        
        print("✅ Dati di test eliminati con successo")
        return True
        
    except Exception as e:
        print(f"❌ Errore nell'eliminazione dei dati di test: {e}")
        return False

def insert_excel_data(supabase, all_data):
    """Inserisce tutti i dati Excel nella tabella excel_data"""
    print(f"\n📊 Inserendo dati Excel nel database...")
    
    try:
        # Prepara i dati per l'inserimento
        excel_record = {
            'file_name': 'Gestion Carniceria El Tablero.xlsx',
            'upload_date': datetime.now().isoformat(),
            'data': all_data,
            'processed_by': None,  # Nessun utente specifico per questo inserimento
            'created_at': datetime.now().isoformat()
        }
        
        # Inserisci i dati
        result = supabase.table('excel_data').insert(excel_record).execute()
        print(f"   ✅ Dati Excel inseriti con successo")
        return True
        
    except Exception as e:
        print(f"   ❌ Errore inserendo dati Excel: {e}")
        return False

def create_monthly_summary(supabase, all_data):
    """Crea un riepilogo mensile dei dati"""
    print(f"\n📅 Creando riepilogo mensile...")
    
    try:
        # Raggruppa i dati per mese
        monthly_data = {}
        
        for sale in all_data['sales']:
            month = sale['date']
            if month not in monthly_data:
                monthly_data[month] = {'sales': 0, 'purchases': 0, 'expenses': 0}
            monthly_data[month]['sales'] += sale['amount']
        
        for purchase in all_data['purchases']:
            month = purchase['date']
            if month not in monthly_data:
                monthly_data[month] = {'sales': 0, 'purchases': 0, 'expenses': 0}
            monthly_data[month]['purchases'] += purchase['amount']
        
        # Inserisci i riepiloghi mensili
        summary_records = []
        for month, data in monthly_data.items():
            profit = data['sales'] - data['purchases'] - data['expenses']
            
            # Converti il mese in formato YYYY-MM
            month_formatted = month.replace(' ', '-').replace('24', '2024').replace('25', '2025')
            if len(month_formatted) > 7:
                month_formatted = month_formatted[:7]  # Limita a 7 caratteri
            
            record = {
                'month': month_formatted,
                'total_sales': data['sales'],
                'total_expenses': data['purchases'] + data['expenses'],
                'total_profit': profit,
                'created_at': datetime.now().isoformat()
            }
            summary_records.append(record)
        
        # Inserisci i dati
        if summary_records:
            result = supabase.table('monthly_summary').insert(summary_records).execute()
            print(f"   ✅ {len(summary_records)} riepiloghi mensili creati")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Errore creando riepilogo mensile: {e}")
        return False

def verify_data_insertion(supabase):
    """Verifica che i dati siano stati inseriti correttamente"""
    print("\n🔍 Verificando inserimento dati...")
    
    try:
        # Conta i record nelle tabelle principali
        tables = ['excel_data', 'monthly_summary']
        
        for table in tables:
            try:
                result = supabase.table(table).select('*', count='exact').execute()
                count = result.count if hasattr(result, 'count') else len(result.data)
                print(f"   📊 {table.upper()}: {count} record")
                
                # Mostra alcuni dettagli per excel_data
                if table == 'excel_data' and count > 0:
                    data_result = supabase.table('excel_data').select('*').limit(1).execute()
                    if data_result.data:
                        excel_data = data_result.data[0]['data']
                        print(f"      💰 Vendite: {len(excel_data.get('sales', []))} record")
                        print(f"      🛒 Acquisti: {len(excel_data.get('purchases', []))} record")
                        print(f"      🚚 Fornitori: {len(excel_data.get('suppliers', []))} record")
                        
            except Exception as e:
                print(f"   ⚠️ Errore verificando {table}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore nella verifica: {e}")
        return False

def main():
    """Funzione principale"""
    print("🚀 Avvio inserimento dati Excel nel database Supabase")
    print("=" * 60)
    
    # Carica i dati estratti
    data_file = "extracted_carniceria_data.json"
    if not os.path.exists(data_file):
        print(f"❌ File {data_file} non trovato")
        print("Esegui prima analyze_excel_data.py per estrarre i dati")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 Dati caricati:")
    print(f"   💰 Vendite: {len(data['sales'])} record")
    print(f"   🛒 Acquisti: {len(data['purchases'])} record")
    print(f"   💸 Spese: {len(data['expenses'])} record")
    print(f"   🚚 Fornitori: {len(data['suppliers'])} record")
    
    # Connessione a Supabase
    supabase = get_supabase_client()
    if not supabase:
        return
    
    # Procedi automaticamente (per script non interattivo)
    print(f"\n⚠️ ATTENZIONE: Questo script eliminerà TUTTI i dati esistenti!")
    print("🚀 Procedendo automaticamente con l'inserimento...")
    
    # Elimina dati di test
    if not clear_test_data(supabase):
        print("❌ Errore nell'eliminazione dei dati di test")
        return
    
    # Inserisci i nuovi dati
    success = True
    
    success &= insert_excel_data(supabase, data)
    success &= create_monthly_summary(supabase, data)
    
    if success:
        print(f"\n✅ Inserimento dati completato con successo!")
        
        # Verifica l'inserimento
        verify_data_insertion(supabase)
        
        print(f"\n🎉 I dati del file Excel sono ora disponibili nella dashboard!")
        print(f"   Puoi accedere alla dashboard e vedere i dati reali")
        
    else:
        print(f"\n❌ Errore durante l'inserimento dei dati")

if __name__ == "__main__":
    main()
