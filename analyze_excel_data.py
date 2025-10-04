#!/usr/bin/env python3
"""
Script per analizzare e estrarre dati dal file Excel della macelleria
"""

import pandas as pd
import json
from datetime import datetime
import os

def analyze_excel_structure(file_path):
    """Analizza la struttura del file Excel"""
    print(f"📊 Analizzando file: {file_path}")
    
    try:
        # Leggi tutte le sheet del file Excel
        excel_file = pd.ExcelFile(file_path)
        print(f"📋 Sheet disponibili: {excel_file.sheet_names}")
        
        all_data = {}
        
        for sheet_name in excel_file.sheet_names:
            print(f"\n🔍 Analizzando sheet: {sheet_name}")
            
            # Leggi il sheet
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            print(f"   📏 Dimensioni: {df.shape[0]} righe x {df.shape[1]} colonne")
            print(f"   📝 Colonne: {list(df.columns)}")
            
            # Mostra le prime righe
            print(f"   📄 Prime 3 righe:")
            print(df.head(3).to_string())
            
            # Salva i dati
            all_data[sheet_name] = {
                'data': df.to_dict('records'),
                'columns': list(df.columns),
                'shape': df.shape
            }
            
            print(f"   ✅ Sheet '{sheet_name}' processato")
        
        return all_data
        
    except Exception as e:
        print(f"❌ Errore nell'analisi del file: {e}")
        return None

def extract_structured_data(excel_data):
    """Estrae dati strutturati per il database"""
    print("\n🔄 Estraendo dati strutturati...")
    
    structured_data = {
        'sales': [],
        'purchases': [],
        'expenses': [],
        'suppliers': []
    }
    
    for sheet_name, sheet_data in excel_data.items():
        df = pd.DataFrame(sheet_data['data'])
        columns = sheet_data['columns']
        
        print(f"\n📊 Processando sheet: {sheet_name}")
        print(f"   Colonne disponibili: {columns}")
        
        # Converti le colonne in stringhe per l'analisi
        str_columns = [str(col).lower() for col in columns]
        
        # Analizza la struttura del file Excel
        print(f"   🔍 Analizzando struttura del file...")
        
        # Cerca le righe con i dati effettivi (non header)
        data_rows = []
        for idx, row in df.iterrows():
            # Cerca righe con dati numerici nelle colonne principali
            has_numeric_data = False
            for col in [1, 2, 3, 4, 5, 6]:  # Colonne numeriche principali
                if col in df.columns:
                    try:
                        val = row[col]
                        if pd.notna(val) and str(val).replace('.', '').replace('-', '').isdigit():
                            has_numeric_data = True
                            break
                    except:
                        pass
            
            if has_numeric_data:
                data_rows.append((idx, row))
        
        print(f"   📊 Trovate {len(data_rows)} righe con dati numerici")
        
        # Processa le righe con dati
        for idx, row in data_rows[:10]:  # Limita a prime 10 righe per test
            try:
                # Estrai dati dalle colonne numeriche
                base_venta = row.get(1, 0)  # Base I (Vendite)
                igic_venta = row.get(2, 0)  # IGIC (Vendite)
                cobro = row.get(3, 0)       # COBRO (Vendite)
                base_compra = row.get(4, 0) # Base I (Compras)
                igic_compra = row.get(5, 0) # IGIC (Compras)
                pagos = row.get(6, 0)       # Pagos (Compras)
                
                # Converti in float, gestendo valori NaN
                def safe_float(val):
                    try:
                        if pd.isna(val) or val == '' or val is None:
                            return 0.0
                        return float(str(val).replace(',', '.'))
                    except:
                        return 0.0
                
                base_venta = safe_float(base_venta)
                igic_venta = safe_float(igic_venta)
                cobro = safe_float(cobro)
                base_compra = safe_float(base_compra)
                igic_compra = safe_float(igic_compra)
                pagos = safe_float(pagos)
                
                # Crea record di vendita se ci sono dati
                if base_venta > 0 or cobro > 0:
                    sale_record = {
                        'date': f"{sheet_name}",
                        'amount': cobro if cobro > 0 else base_venta + igic_venta,
                        'base_amount': base_venta,
                        'tax_amount': igic_venta,
                        'description': f"Venta del {sheet_name}",
                        'sheet_source': sheet_name,
                        'row_index': idx
                    }
                    structured_data['sales'].append(sale_record)
                
                # Crea record di acquisto se ci sono dati
                if base_compra > 0 or pagos > 0:
                    purchase_record = {
                        'date': f"{sheet_name}",
                        'amount': pagos if pagos > 0 else base_compra + igic_compra,
                        'base_amount': base_compra,
                        'tax_amount': igic_compra,
                        'supplier': f"Proveedor_{sheet_name}",
                        'description': f"Compra del {sheet_name}",
                        'sheet_source': sheet_name,
                        'row_index': idx
                    }
                    structured_data['purchases'].append(purchase_record)
                
                # Crea record di fornitore
                supplier_record = {
                    'name': f"Proveedor_{sheet_name}",
                    'contact_info': f"Contacto per {sheet_name}",
                    'sheet_source': sheet_name
                }
                structured_data['suppliers'].append(supplier_record)
                
            except Exception as e:
                print(f"   ⚠️ Errore processando riga {idx}: {e}")
                continue
        
        print(f"   ✅ Sheet '{sheet_name}' processato: {len([r for r in data_rows if r[0] < 10])} righe elaborate")
    
    return structured_data

def save_extracted_data(structured_data, output_file):
    """Salva i dati estratti in un file JSON"""
    print(f"\n💾 Salvando dati estratti in: {output_file}")
    
    # Converti le date in stringhe per la serializzazione JSON
    def convert_dates(obj):
        if isinstance(obj, dict):
            return {k: convert_dates(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_dates(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, 'date'):  # datetime.date
            return obj.isoformat()
        else:
            return obj
    
    converted_data = convert_dates(structured_data)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Dati salvati con successo!")
    
    # Mostra statistiche
    print(f"\n📊 Statistiche dati estratti:")
    for category, data in structured_data.items():
        print(f"   {category.upper()}: {len(data)} record")

def main():
    """Funzione principale"""
    file_path = "/Users/ezio/Downloads/Gestion Carniceria El Tablero .xlsx"
    output_file = "extracted_carniceria_data.json"
    
    print("🚀 Avvio analisi file Excel macelleria")
    print("=" * 50)
    
    # Analizza la struttura
    excel_data = analyze_excel_structure(file_path)
    
    if excel_data:
        # Estrae dati strutturati
        structured_data = extract_structured_data(excel_data)
        
        # Salva i dati
        save_extracted_data(structured_data, output_file)
        
        print(f"\n✅ Analisi completata!")
        print(f"📁 File di output: {output_file}")
    else:
        print("❌ Errore nell'analisi del file Excel")

if __name__ == "__main__":
    main()
