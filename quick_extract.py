#!/usr/bin/env python3
"""
Script rapido per estrarre i dati essenziali dal file Excel
"""

import pandas as pd
import json
from datetime import datetime

def extract_excel_data():
    """Estrae i dati essenziali dal file Excel"""
    file_path = "/Users/ezio/Downloads/Gestion Carniceria El Tablero .xlsx"
    
    print("📊 Estrando dati essenziali dal file Excel...")
    
    try:
        # Leggi tutte le sheet del file Excel
        excel_file = pd.ExcelFile(file_path)
        print(f"📋 Sheet disponibili: {excel_file.sheet_names}")
        
        all_data = {
            'sales': [],
            'purchases': [],
            'suppliers': []
        }
        
        for sheet_name in excel_file.sheet_names:
            print(f"🔍 Processando sheet: {sheet_name}")
            
            # Leggi il sheet
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Cerca le righe con dati numerici
            data_rows = []
            for idx, row in df.iterrows():
                has_numeric_data = False
                for col in [1, 2, 3, 4, 5, 6]:
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
            
            # Processa le righe con dati (limita a prime 5 per velocità)
            for idx, row in data_rows[:5]:
                try:
                    # Estrai dati dalle colonne numeriche
                    base_venta = row.get(1, 0)
                    igic_venta = row.get(2, 0)
                    cobro = row.get(3, 0)
                    base_compra = row.get(4, 0)
                    igic_compra = row.get(5, 0)
                    pagos = row.get(6, 0)
                    
                    # Converti in float
                    def safe_float(val):
                        try:
                            if pd.isna(val) or val == '' or val is None:
                                return 0.0
                            return float(str(val).replace(',', '.'))
                        except:
                            return 0.0
                    
                    base_venta = safe_float(base_venta)
                    cobro = safe_float(cobro)
                    base_compra = safe_float(base_compra)
                    pagos = safe_float(pagos)
                    
                    # Crea record di vendita
                    if base_venta > 0 or cobro > 0:
                        sale_record = {
                            'date': sheet_name,
                            'amount': cobro if cobro > 0 else base_venta,
                            'description': f"Venta del {sheet_name}",
                            'sheet_source': sheet_name
                        }
                        all_data['sales'].append(sale_record)
                    
                    # Crea record di acquisto
                    if base_compra > 0 or pagos > 0:
                        purchase_record = {
                            'date': sheet_name,
                            'amount': pagos if pagos > 0 else base_compra,
                            'supplier': f"Proveedor_{sheet_name}",
                            'description': f"Compra del {sheet_name}",
                            'sheet_source': sheet_name
                        }
                        all_data['purchases'].append(purchase_record)
                    
                    # Crea record di fornitore
                    supplier_record = {
                        'name': f"Proveedor_{sheet_name}",
                        'contact_info': f"Contacto per {sheet_name}",
                        'sheet_source': sheet_name
                    }
                    all_data['suppliers'].append(supplier_record)
                    
                except Exception as e:
                    continue
        
        # Salva i dati
        with open('extracted_carniceria_data.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Dati estratti e salvati:")
        print(f"   💰 Vendite: {len(all_data['sales'])} record")
        print(f"   🛒 Acquisti: {len(all_data['purchases'])} record")
        print(f"   🚚 Fornitori: {len(all_data['suppliers'])} record")
        
        return all_data
        
    except Exception as e:
        print(f"❌ Errore nell'estrazione: {e}")
        return None

if __name__ == "__main__":
    extract_excel_data()
