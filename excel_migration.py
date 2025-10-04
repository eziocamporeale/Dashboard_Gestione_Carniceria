#!/usr/bin/env python3
"""
Script per migrare i dati dal file Excel "Gestion Carniceria El Tablero.xlsx"
al dashboard di gestione macelleria.
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelMigrator:
    """Classe per migrare dati Excel al dashboard"""
    
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.months_mapping = {
            'Noviembre 24': '2024-11',
            'Deciembre 24': '2024-12', 
            'Enero 25': '2025-01',
            'Febrero 25': '2025-02',
            'Marzo 25': '2025-03',
            'Abril 25': '2025-04',
            'Mayo 25': '2025-05',
            'Junio 25': '2025-06'
        }
        
    def read_excel_data(self) -> Dict[str, Any]:
        """Legge tutti i dati dal file Excel"""
        try:
            logger.info(f"📊 Leggendo file Excel: {self.excel_path}")
            
            # Leggi tutti i fogli
            xl_file = pd.ExcelFile(self.excel_path)
            all_data = {}
            
            for sheet_name in xl_file.sheet_names:
                logger.info(f"📋 Processando foglio: {sheet_name}")
                
                # Leggi il foglio
                df = pd.read_excel(self.excel_path, sheet_name=sheet_name, header=None)
                
                # Processa i dati del foglio
                processed_data = self.process_sheet_data(df, sheet_name)
                all_data[sheet_name] = processed_data
                
            return all_data
            
        except Exception as e:
            logger.error(f"❌ Errore leggendo Excel: {e}")
            return {}
    
    def process_sheet_data(self, df: pd.DataFrame, sheet_name: str) -> Dict[str, Any]:
        """Processa i dati di un singolo foglio"""
        try:
            # Identifica le colonne principali
            columns_mapping = {
                0: 'movimiento_id',
                1: 'numero', 
                2: 'fecha',
                3: 'base_venta',
                4: 'igic_venta',
                5: 'cobro_venta',
                6: 'base_compra',
                7: 'igic_compra', 
                8: 'pagos_compra',
                9: 'nombre_operacion',
                10: 'beneficio',
                11: 'nomina',
                12: 'seguridad_social',
                13: 'retencion',
                14: 'vacaciones',
                15: 'liquidacion',
                16: 'gastos',
                17: 'beneficio_total',
                18: 'beneficio_neto',
                19: 'fondo',
                20: 'stock'
            }
            
            # Estrai i dati delle transazioni
            transactions = []
            daily_totals = []
            
            for i in range(len(df)):
                row = df.iloc[i]
                
                # Cerca righe con dati di transazione
                if pd.notna(row.iloc[0]) and isinstance(row.iloc[0], (int, float)):
                    transaction = self.extract_transaction(row, columns_mapping, sheet_name)
                    if transaction:
                        transactions.append(transaction)
                
                # Cerca totali giornalieri
                if pd.notna(row.iloc[9]) and 'TOTAL DEL DIA' in str(row.iloc[9]):
                    daily_total = self.extract_daily_total(row, columns_mapping, sheet_name)
                    if daily_total:
                        daily_totals.append(daily_total)
            
            return {
                'month': self.months_mapping.get(sheet_name, sheet_name),
                'transactions': transactions,
                'daily_totals': daily_totals,
                'summary': self.calculate_monthly_summary(transactions, daily_totals)
            }
            
        except Exception as e:
            logger.error(f"❌ Errore processando foglio {sheet_name}: {e}")
            return {}
    
    def extract_transaction(self, row: pd.Series, columns_mapping: Dict, sheet_name: str) -> Dict[str, Any]:
        """Estrae una singola transazione"""
        try:
            transaction = {
                'id': int(row.iloc[0]) if pd.notna(row.iloc[0]) else None,
                'fecha': self.parse_date(row.iloc[2]) if pd.notna(row.iloc[2]) else None,
                'tipo': 'venta' if pd.notna(row.iloc[3]) else 'compra' if pd.notna(row.iloc[6]) else 'gasto',
                'importo': 0,
                'descripcion': str(row.iloc[9]) if pd.notna(row.iloc[9]) else '',
                'month': self.months_mapping.get(sheet_name, sheet_name)
            }
            
            # Determina importo e tipo
            if pd.notna(row.iloc[3]):  # Venta
                transaction['importo'] = float(row.iloc[3])
                transaction['igic'] = float(row.iloc[4]) if pd.notna(row.iloc[4]) else 0
                transaction['total'] = float(row.iloc[5]) if pd.notna(row.iloc[5]) else transaction['importo']
            elif pd.notna(row.iloc[6]):  # Compra
                transaction['importo'] = float(row.iloc[6])
                transaction['igic'] = float(row.iloc[7]) if pd.notna(row.iloc[7]) else 0
                transaction['total'] = float(row.iloc[8]) if pd.notna(row.iloc[8]) else transaction['importo']
            elif pd.notna(row.iloc[11]):  # Gasto
                transaction['importo'] = float(row.iloc[11])
                transaction['tipo'] = 'nomina'
            elif pd.notna(row.iloc[12]):  # Seguridad Social
                transaction['importo'] = float(row.iloc[12])
                transaction['tipo'] = 'seguridad_social'
            elif pd.notna(row.iloc[13]):  # Retencion
                transaction['importo'] = float(row.iloc[13])
                transaction['tipo'] = 'retencion'
            elif pd.notna(row.iloc[14]):  # Vacaciones
                transaction['importo'] = float(row.iloc[14])
                transaction['tipo'] = 'vacaciones'
            elif pd.notna(row.iloc[15]):  # Liquidacion
                transaction['importo'] = float(row.iloc[15])
                transaction['tipo'] = 'liquidacion'
            elif pd.notna(row.iloc[16]):  # Gastos
                transaction['importo'] = float(row.iloc[16])
                transaction['tipo'] = 'gasto'
            
            return transaction if transaction['importo'] > 0 else None
            
        except Exception as e:
            logger.error(f"❌ Errore estraendo transazione: {e}")
            return None
    
    def extract_daily_total(self, row: pd.Series, columns_mapping: Dict, sheet_name: str) -> Dict[str, Any]:
        """Estrae un totale giornaliero"""
        try:
            return {
                'fecha': self.parse_date(row.iloc[2]) if pd.notna(row.iloc[2]) else None,
                'ventas': float(row.iloc[3]) if pd.notna(row.iloc[3]) else 0,
                'cobros': float(row.iloc[5]) if pd.notna(row.iloc[5]) else 0,
                'month': self.months_mapping.get(sheet_name, sheet_name)
            }
        except Exception as e:
            logger.error(f"❌ Errore estraendo totale giornaliero: {e}")
            return None
    
    def parse_date(self, date_value) -> str:
        """Converte una data in formato stringa"""
        try:
            if pd.isna(date_value):
                return None
            
            if isinstance(date_value, datetime):
                return date_value.strftime('%Y-%m-%d')
            elif isinstance(date_value, str):
                # Prova a parsare stringhe di data
                return pd.to_datetime(date_value).strftime('%Y-%m-%d')
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Errore parsando data {date_value}: {e}")
            return None
    
    def calculate_monthly_summary(self, transactions: List[Dict], daily_totals: List[Dict]) -> Dict[str, Any]:
        """Calcola il riepilogo mensile"""
        try:
            summary = {
                'total_ventas': 0,
                'total_compras': 0,
                'total_gastos': 0,
                'total_beneficio': 0,
                'num_transacciones': len(transactions),
                'num_dias': len(daily_totals)
            }
            
            for transaction in transactions:
                if transaction['tipo'] == 'venta':
                    summary['total_ventas'] += transaction['importo']
                elif transaction['tipo'] == 'compra':
                    summary['total_compras'] += transaction['importo']
                else:
                    summary['total_gastos'] += transaction['importo']
            
            summary['total_beneficio'] = summary['total_ventas'] - summary['total_compras'] - summary['total_gastos']
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Errore calcolando riepilogo: {e}")
            return {}
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Genera i dati formattati per il dashboard"""
        try:
            logger.info("🔄 Generando dati per dashboard...")
            
            excel_data = self.read_excel_data()
            
            # Raggruppa tutti i dati
            all_transactions = []
            all_daily_totals = []
            monthly_summaries = {}
            
            for sheet_name, data in excel_data.items():
                all_transactions.extend(data.get('transactions', []))
                all_daily_totals.extend(data.get('daily_totals', []))
                monthly_summaries[data.get('month')] = data.get('summary', {})
            
            # Genera dati per il dashboard
            dashboard_data = {
                'sales': self.format_sales_data(all_transactions),
                'purchases': self.format_purchases_data(all_transactions),
                'expenses': self.format_expenses_data(all_transactions),
                'daily_totals': all_daily_totals,
                'monthly_summaries': monthly_summaries,
                'financial_summary': self.calculate_financial_summary(monthly_summaries),
                'suppliers': self.extract_suppliers(all_transactions),
                'customers': self.extract_customers(all_transactions)
            }
            
            logger.info("✅ Dati generati con successo!")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ Errore generando dati dashboard: {e}")
            return {}
    
    def format_sales_data(self, transactions: List[Dict]) -> List[Dict]:
        """Formatta i dati delle vendite per il dashboard"""
        sales = []
        for i, transaction in enumerate(transactions):
            if transaction['tipo'] == 'venta':
                sales.append({
                    'id': i + 1,
                    'fecha': transaction['fecha'],
                    'cliente': transaction['descripcion'] or 'Cliente General',
                    'producto': 'Productos Varios',
                    'cantidad': 1,
                    'precio_unitario': transaction['importo'],
                    'total': transaction.get('total', transaction['importo']),
                    'igic': transaction.get('igic', 0),
                    'metodo_pago': 'Efectivo',
                    'vendedor': 'Sistema',
                    'estado': 'Completada'
                })
        return sales
    
    def format_purchases_data(self, transactions: List[Dict]) -> List[Dict]:
        """Formatta i dati degli acquisti per il dashboard"""
        purchases = []
        for i, transaction in enumerate(transactions):
            if transaction['tipo'] == 'compra':
                purchases.append({
                    'id': i + 1,
                    'fecha': transaction['fecha'],
                    'proveedor': transaction['descripcion'] or 'Proveedor General',
                    'producto': 'Productos Varios',
                    'cantidad': 1,
                    'precio_unitario': transaction['importo'],
                    'total': transaction.get('total', transaction['importo']),
                    'igic': transaction.get('igic', 0),
                    'metodo_pago': 'Transferencia',
                    'estado': 'Pagado'
                })
        return purchases
    
    def format_expenses_data(self, transactions: List[Dict]) -> List[Dict]:
        """Formatta i dati delle spese per il dashboard"""
        expenses = []
        for i, transaction in enumerate(transactions):
            if transaction['tipo'] in ['nomina', 'seguridad_social', 'retencion', 'vacaciones', 'liquidacion', 'gasto']:
                expenses.append({
                    'id': i + 1,
                    'fecha': transaction['fecha'],
                    'categoria': transaction['tipo'],
                    'descripcion': transaction['descripcion'] or f'Gasto {transaction["tipo"]}',
                    'importo': transaction['importo'],
                    'metodo_pago': 'Transferencia',
                    'estado': 'Pagado'
                })
        return expenses
    
    def calculate_financial_summary(self, monthly_summaries: Dict) -> Dict[str, Any]:
        """Calcola il riepilogo finanziario generale"""
        try:
            total_ventas = sum(s.get('total_ventas', 0) for s in monthly_summaries.values())
            total_compras = sum(s.get('total_compras', 0) for s in monthly_summaries.values())
            total_gastos = sum(s.get('total_gastos', 0) for s in monthly_summaries.values())
            total_beneficio = sum(s.get('total_beneficio', 0) for s in monthly_summaries.values())
            
            return {
                'total_ventas': total_ventas,
                'total_compras': total_compras,
                'total_gastos': total_gastos,
                'total_beneficio': total_beneficio,
                'margen_beneficio': (total_beneficio / total_ventas * 100) if total_ventas > 0 else 0,
                'num_meses': len(monthly_summaries),
                'promedio_mensual_ventas': total_ventas / len(monthly_summaries) if monthly_summaries else 0
            }
        except Exception as e:
            logger.error(f"❌ Errore calcolando riepilogo finanziario: {e}")
            return {}
    
    def extract_suppliers(self, transactions: List[Dict]) -> List[Dict]:
        """Estrae i fornitori dalle transazioni"""
        suppliers = {}
        for transaction in transactions:
            if transaction['tipo'] == 'compra' and transaction['descripcion']:
                supplier_name = transaction['descripcion']
                if supplier_name not in suppliers:
                    suppliers[supplier_name] = {
                        'name': supplier_name,
                        'total_amount': 0,
                        'transactions_count': 0
                    }
                suppliers[supplier_name]['total_amount'] += transaction['importo']
                suppliers[supplier_name]['transactions_count'] += 1
        
        return list(suppliers.values())
    
    def extract_customers(self, transactions: List[Dict]) -> List[Dict]:
        """Estrae i clienti dalle transazioni"""
        customers = {}
        for transaction in transactions:
            if transaction['tipo'] == 'venta' and transaction['descripcion']:
                customer_name = transaction['descripcion']
                if customer_name not in customers:
                    customers[customer_name] = {
                        'name': customer_name,
                        'total_purchases': 0,
                        'total_orders': 0
                    }
                customers[customer_name]['total_purchases'] += transaction['importo']
                customers[customer_name]['total_orders'] += 1
        
        return list(customers.values())
    
    def save_dashboard_data(self, output_path: str = 'migrated_data.json'):
        """Salva i dati migrati in un file JSON"""
        try:
            dashboard_data = self.generate_dashboard_data()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"✅ Dati salvati in: {output_path}")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ Errore salvando dati: {e}")
            return {}

def main():
    """Funzione principale"""
    excel_path = "/Users/ezio/Downloads/Gestion Carniceria El Tablero .xlsx"
    
    migrator = ExcelMigrator(excel_path)
    dashboard_data = migrator.save_dashboard_data()
    
    print("\n📊 RIEPILOGO MIGRAZIONE:")
    print("=" * 50)
    
    if dashboard_data:
        financial_summary = dashboard_data.get('financial_summary', {})
        print(f"💰 Total Ventas: ${financial_summary.get('total_ventas', 0):,.2f}")
        print(f"💸 Total Compras: ${financial_summary.get('total_compras', 0):,.2f}")
        print(f"📊 Total Gastos: ${financial_summary.get('total_gastos', 0):,.2f}")
        print(f"📈 Total Beneficio: ${financial_summary.get('total_beneficio', 0):,.2f}")
        print(f"📅 Meses procesados: {financial_summary.get('num_meses', 0)}")
        
        print(f"\n📋 Transacciones:")
        print(f"  - Ventas: {len(dashboard_data.get('sales', []))}")
        print(f"  - Compras: {len(dashboard_data.get('purchases', []))}")
        print(f"  - Gastos: {len(dashboard_data.get('expenses', []))}")
        
        print(f"\n👥 Entidades:")
        print(f"  - Proveedores: {len(dashboard_data.get('suppliers', []))}")
        print(f"  - Clientes: {len(dashboard_data.get('customers', []))}")
    
    print("\n✅ Migrazione completata!")

if __name__ == "__main__":
    main()
