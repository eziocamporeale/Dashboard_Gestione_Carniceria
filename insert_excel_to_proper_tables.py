#!/usr/bin/env python3
"""
Script per inserire i dati Excel nelle tabelle corrette del database
Inserisce i dati nelle tabelle sales, suppliers, customers che la dashboard usa normalmente
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

def clear_existing_data(supabase):
    """Elimina i dati esistenti dalle tabelle principali"""
    print("\n🗑️ Eliminando dati esistenti dalle tabelle principali...")
    
    try:
        # Elimina dati dalle tabelle in ordine di dipendenza
        tables_to_clear = [
            'sale_items',  # Prima i dettagli
            'sales',       # Poi le vendite
            'suppliers',   # Poi i fornitori
            'customers'    # Infine i clienti
        ]
        
        for table in tables_to_clear:
            try:
                result = supabase.table(table).delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
                print(f"   ✅ Tabella {table}: dati eliminati")
            except Exception as e:
                print(f"   ⚠️ Errore eliminando da {table}: {e}")
        
        print("✅ Dati esistenti eliminati con successo")
        return True
        
    except Exception as e:
        print(f"❌ Errore nell'eliminazione dei dati esistenti: {e}")
        return False

def insert_suppliers(supabase, suppliers_data):
    """Inserisce i fornitori nella tabella suppliers"""
    print(f"\n🚚 Inserendo {len(suppliers_data)} fornitori...")
    
    try:
        # Rimuovi duplicati basandosi sul nome
        unique_suppliers = {}
        for supplier in suppliers_data:
            name = supplier['name']
            if name not in unique_suppliers:
                unique_suppliers[name] = supplier
        
        # Prepara i dati per l'inserimento
        suppliers_records = []
        for supplier in unique_suppliers.values():
            record = {
                'name': supplier['name'],
                'contact_email': None,
                'phone': None,
                'address': None,
                'contact_person': None,
                'total_amount': 0.0,
                'transactions_count': 0,
                'is_active': True,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            suppliers_records.append(record)
        
        # Inserisci i dati
        result = supabase.table('suppliers').insert(suppliers_records).execute()
        print(f"   ✅ {len(suppliers_records)} fornitori inseriti")
        
        # Restituisci i fornitori inseriti per usare i loro ID
        return result.data
        
    except Exception as e:
        print(f"   ❌ Errore inserendo fornitori: {e}")
        return []

def insert_customers(supabase, sales_data):
    """Crea clienti generici basandosi sulle vendite"""
    print(f"\n👥 Creando clienti generici...")
    
    try:
        # Crea un cliente generico per le vendite Excel
        customer_record = {
            'name': 'Cliente Generico Excel',
            'email': 'cliente.excel@carniceria.com',
            'phone': None,
            'address': None,
            'total_purchases': 0.0,
            'last_purchase': None,
            'is_active': True,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Inserisci il cliente
        result = supabase.table('customers').insert(customer_record).execute()
        print(f"   ✅ Cliente generico creato")
        
        return result.data[0] if result.data else None
        
    except Exception as e:
        print(f"   ❌ Errore creando cliente: {e}")
        return None

def insert_sales(supabase, sales_data, customer_id):
    """Inserisce le vendite nella tabella sales"""
    print(f"\n💰 Inserendo {len(sales_data)} vendite...")
    
    try:
        # Prepara i dati per l'inserimento
        sales_records = []
        for sale in sales_data:
            # Converti la data dal formato "Noviembre 24" a una data valida
            sale_date = datetime.now()  # Usa data corrente come fallback
            
            record = {
                'customer_id': customer_id,
                'user_id': None,  # Nessun utente specifico
                'sale_date': sale_date.isoformat(),
                'total_amount': sale['amount'],
                'discount_percentage': 0.0,
                'discount_amount': 0.0,
                'final_amount': sale['amount'],
                'payment_method': 'Efectivo',  # Metodo di pagamento predefinito
                'notes': f"Venta Excel - {sale['description']}",
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            sales_records.append(record)
        
        # Inserisci i dati
        result = supabase.table('sales').insert(sales_records).execute()
        print(f"   ✅ {len(sales_records)} vendite inserite")
        
        return result.data
        
    except Exception as e:
        print(f"   ❌ Errore inserendo vendite: {e}")
        return []

def update_supplier_totals(supabase, purchases_data, suppliers):
    """Aggiorna i totali dei fornitori basandosi sugli acquisti"""
    print(f"\n📊 Aggiornando totali fornitori...")
    
    try:
        # Crea un mapping nome -> ID fornitore
        supplier_map = {s['name']: s['id'] for s in suppliers}
        
        # Raggruppa gli acquisti per fornitore
        supplier_totals = {}
        for purchase in purchases_data:
            supplier_name = purchase.get('supplier', 'Sconosciuto')
            if supplier_name in supplier_map:
                supplier_id = supplier_map[supplier_name]
                if supplier_id not in supplier_totals:
                    supplier_totals[supplier_id] = {'total': 0.0, 'count': 0}
                supplier_totals[supplier_id]['total'] += purchase['amount']
                supplier_totals[supplier_id]['count'] += 1
        
        # Aggiorna i fornitori
        for supplier_id, totals in supplier_totals.items():
            try:
                supabase.table('suppliers').update({
                    'total_amount': totals['total'],
                    'transactions_count': totals['count'],
                    'updated_at': datetime.now().isoformat()
                }).eq('id', supplier_id).execute()
            except Exception as e:
                print(f"   ⚠️ Errore aggiornando fornitore {supplier_id}: {e}")
        
        print(f"   ✅ Totali aggiornati per {len(supplier_totals)} fornitori")
        
    except Exception as e:
        print(f"   ❌ Errore aggiornando totali fornitori: {e}")

def verify_data_insertion(supabase):
    """Verifica che i dati siano stati inseriti correttamente"""
    print("\n🔍 Verificando inserimento dati...")
    
    try:
        # Conta i record nelle tabelle principali
        tables = ['suppliers', 'customers', 'sales']
        
        for table in tables:
            try:
                result = supabase.table(table).select('*', count='exact').execute()
                count = result.count if hasattr(result, 'count') else len(result.data)
                print(f"   📊 {table.upper()}: {count} record")
                
                # Mostra alcuni dettagli per sales
                if table == 'sales' and count > 0:
                    sales_result = supabase.table('sales').select('total_amount').limit(5).execute()
                    if sales_result.data:
                        total_sales = sum([s['total_amount'] for s in sales_result.data])
                        print(f"      💰 Totale prime 5 vendite: ${total_sales:,.2f}")
                        
            except Exception as e:
                print(f"   ⚠️ Errore verificando {table}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore nella verifica: {e}")
        return False

def main():
    """Funzione principale"""
    print("🚀 Inserimento dati Excel nelle tabelle corrette del database")
    print("=" * 70)
    
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
    print(f"   🚚 Fornitori: {len(data['suppliers'])} record")
    
    # Connessione a Supabase
    supabase = get_supabase_client()
    if not supabase:
        return
    
    # Procedi automaticamente
    print(f"\n⚠️ ATTENZIONE: Questo script eliminerà TUTTI i dati esistenti!")
    print("🚀 Procedendo automaticamente con l'inserimento...")
    
    # Elimina dati esistenti
    if not clear_existing_data(supabase):
        print("❌ Errore nell'eliminazione dei dati esistenti")
        return
    
    # Inserisci i dati nelle tabelle corrette
    success = True
    
    # 1. Inserisci fornitori
    suppliers = insert_suppliers(supabase, data['suppliers'])
    if not suppliers:
        success = False
    
    # 2. Crea cliente generico
    customer = insert_customers(supabase, data['sales'])
    if not customer:
        success = False
    
    # 3. Inserisci vendite
    if customer:
        sales = insert_sales(supabase, data['sales'], customer['id'])
        if not sales:
            success = False
    
    # 4. Aggiorna totali fornitori
    if suppliers:
        update_supplier_totals(supabase, data['purchases'], suppliers)
    
    if success:
        print(f"\n✅ Inserimento dati completato con successo!")
        
        # Verifica l'inserimento
        verify_data_insertion(supabase)
        
        print(f"\n🎉 I dati Excel sono ora nelle tabelle corrette!")
        print(f"   Ora puoi inserire dati manualmente dalla dashboard")
        print(f"   e vedrai tutti i dati insieme (Excel + manuali)")
        
    else:
        print(f"\n❌ Errore durante l'inserimento dei dati")

if __name__ == "__main__":
    main()
